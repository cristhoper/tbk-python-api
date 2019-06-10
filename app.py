from json import dumps
from threading import Thread, RLock

from flask import Flask, request, abort, Response
from tbkpos import TbkPos
from flask_cors import CORS

DEVICE = "COM11"
IP = "0.0.0.0"
PORT = 4001

app = Flask(__name__)
CORS(app)
pos = TbkPos(DEVICE)


transactions_in_progress = {}
safe_pos = RLock()
init_log = []


def get_init_data():
    global init_log
    return init_log


def worker_init():
    global init_log
    init_log = []
    print("Init started")
    safe_pos.acquire()
    _l = pos.close()
    init_log.append("{}:{} ({})".format(_l.response_code, _l.text, _l.response,))
    _l = pos.initialization()
    init_log.append("{}:{} ({})".format(_l.response_code, _l.text, _l.response,))
    _l = pos.load_keys()
    init_log.append("{}:{} ({})".format(_l.response_code, _l.text, _l.response,))
    _l = pos.polling()
    init_log.append("{}:{} ({})".format(_l.response_code, _l.text, _l.response,))
    safe_pos.release()
    print("init ended")


def worker_sale(amount, transaction_id, dummy=False):
    safe_pos.acquire()
    print("Worker started")
    transactions_in_progress[transaction_id] = None
    pos_status = pos.sale_init(amount, transaction_id, dummy)
    transactions_in_progress[transaction_id] = pos_status
    print("Worker ended")
    safe_pos.release()


def payment_on_thread(amount, transaction_id, dummy=False):
    th_pos = Thread(target=worker_sale, args=(amount, transaction_id, dummy,))
    th_pos.daemon = True
    try:
        th_pos.start()
    except RuntimeError as err:
        print("Issues in POS: {}".format(err.message))


@app.route("/init", methods=['POST', 'GET'])
def init():
    th_pos = Thread(target=worker_init)
    th_pos.daemon = True
    try:
        th_pos.start()
    except RuntimeError as err:
        print("Issues in POS: {}".format(err.message))
    th_pos.join(30)
    print(get_init_data())
    return "OK"


@app.route("/payment", methods=['POST'])
def payment():
    """
    POST /payment:
    {
    "transaction_id": integer
    "amount": integer
    }

    :returns
    """
    data = request.get_json() if request.method in ['POST'] else None

    if data is None:
        return abort(405)

    t_id = int(data['transaction_id'])
    amount = int(data['amount'])
    dummy = 'dummy' in data
    if request.method in ['POST']:
        if t_id not in transactions_in_progress.keys():
            payment_on_thread(amount, t_id, dummy)
            return "ACK"
        else:
            return "BUSY"
    return "NAK"


@app.route("/check/<transaction_id>", methods=['GET'])
def check(transaction_id):
    """
    GET /check/<transaction_id>:

    :returns 404 if transaction_id doesn't exists, json POST otherwise.
    {
    "status": string, # OK on success.
    "code": string, # in case of known erros
    "message": string, # in case of known erros
    ...
    }
    """
    if transaction_id is None:
        return abort(404)

    transaction_id = int(transaction_id)
    if transaction_id in transactions_in_progress.keys():
        status = transactions_in_progress[transaction_id]
        if status is not None:
            content = status.get_content()
            if content is None:
                content = {"code": status.response_code, "message": status.text, "status": "FAIL"}
            else:
                content["code"] = status.response_code
                content["message"] = status.text
                content["status"] = "OK"
        else:
            content = {"status": "BUSY"}
    else:
        content = {"status": "FAIL"}
    resp = Response(response=dumps(content, ensure_ascii=False),
                    status=200,
                    mimetype="application/json")
    return resp


if __name__ == "__main__":
    pos.polling()
    app.run(debug=True, host=IP, port=PORT, use_reloader=False)
    worker_init()
