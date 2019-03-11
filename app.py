from Queue import Queue
from json import dumps
from threading import Thread

from flask import Flask, request, abort
from tbkpos import TbkPos

app = Flask(__name__)
pos = TbkPos('/dev/ttyUSB0', 9600)

GET = ['GET']
POST = ['POST']

payment_queue = Queue()
check_queue = Queue()

transactions_in_progress = {}


def worker_sale(amount, transaction_id):
    print("Worker started")
    transactions_in_progress[transaction_id] = None
    pos_status = pos.sale_init(amount, transaction_id)
    transactions_in_progress[transaction_id] = pos_status
    print("Worker ended")


def pos_on_thread(amount, transaction_id):
    th_pos = Thread(target=worker_sale, args=(amount, transaction_id,))
    th_pos.daemon = True
    try:
        th_pos.start()
    except RuntimeError as err:
        print("Issues in POS: {}".format(err.message))


@app.route("/payment", methods=POST)
def payment():
    """
    POST /payment:
    {
    "transaction_id": integer
    "amount": integer
    }

    :returns
    """
    data = request.get_json() if request.method in POST else None

    if data is None:
        return abort(405)

    t_id = int(data['transaction_id'])
    amount = data['amount']
    if request.method in POST:
        if t_id not in transactions_in_progress.keys():
            pos_on_thread(amount, t_id)
        else:
            return "BUSY"
        return "ACK"
    return "NAK"


@app.route("/check/<transaction_id>", methods=GET)
def check(transaction_id):
    """
    GET /check/<transaction_id>:

    :returns 404 if transaction_id doesn't exists, json POST otherwise.
    {
    "transaction_id": string,
    "approval_code": string,
    "print_data": string,
    }
    """
    if transaction_id is None:
        return abort(404)

    status = None
    transaction_id = int(transaction_id)
    if transaction_id in transactions_in_progress.keys():
        status = transactions_in_progress[transaction_id]
        if status is not None:
            content = status.get_content()
            return dumps(content, ensure_ascii=False)
        return "BUSY"
    return "NAK"


if __name__ == "__main__":
    pos.initialization()
    pos.polling()
    print("Turn on socket")
    app.run(debug=True, host='0.0.0.0', port=4001, use_reloader=False)

