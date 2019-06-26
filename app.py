from json import dumps
from threading import Thread, RLock
import os

from flask import Flask, request, abort, Response
from tbkpos import TbkPos
from flask_cors import CORS

from os import name
DEVICE_LIST = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"]
if name == 'nt':
    DEVICE_LIST = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12"]
IP = "0.0.0.0"
PORT = 4001

app = Flask(__name__)
CORS(app)

pos = None
for device in DEVICE_LIST:
    pos = TbkPos(device)
    if pos.device:
        break


transactions_in_progress = {}
safe_pos = RLock()
init_status = {"type": None, "state": False, "response": None}

INIT = "init"
POLLING = "polling"
CLOSE_POS = "close_pos"
LOAD_KEYS = "load_keys"

pos_states = {
    INIT: pos.initialization,
    POLLING: pos.polling,
    CLOSE_POS: pos.close,
    LOAD_KEYS: pos.load_keys,
}


@app.route("/pos/<pos_type>", methods=['GET'])
def init(pos_type):
    global init_status

    if pos_type not in pos_states.keys():

        return "KNOWN TYPES: {}".format(pos_states.keys())

    if not init_status["state"]:
        init_status["type"] = pos_type
        launch_worker(pos_type=init_status["type"])
        return "STARTING"

    elif init_status["state"] and init_status["response"] is not None:
        _l = init_status["response"]
        data = dumps(_l.json())
        print(data)
        resp = Response(response=data,
                        status=200,
                        mimetype="application/json")
        init_status = {"type": None, "state": False, "response": None}
        return resp
    return "RUNNING"


def launch_worker(pos_type=None):
    global init_status
    th_pos = Thread(target=worker_type, args=(pos_type,))
    th_pos.daemon = True
    init_status = {"type": pos_type, "state": True, "response": None}
    try:
        th_pos.start()
    except Exception as err:
        print("Issues in POS: {}".format(err.message))


def worker_type(pos_type=None):
    if pos_type is None:
        return
    safe_pos.acquire()
    print("{} started".format(pos_type))
    _l = pos_states[pos_type]()
    global init_status
    init_status = {"type": pos_type, "state": True, "response": _l}
    safe_pos.release()
    print("{} ended".format(pos_type))


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
        else:
            content = {"status": "BUSY"}
    else:
        content = {"status": "FAIL"}
    resp = Response(response=dumps(content, ensure_ascii=False),
                    status=200,
                    mimetype="application/json")
    return resp


@app.route("/print/<filename>", methods=['GET'])
def print_file(filename):
    os.system("python utils/print.py {}.pdf".format(filename))
    return "PRINT SENDED"


if __name__ == "__main__":
    if pos.device:
        pos.all()
        app.run(debug=True, host=IP, port=PORT, use_reloader=False)
    else:
        print("ERROR: There is no connection to the POS")
        exit(1)
