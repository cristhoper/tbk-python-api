class TransactionData(object):
    result = False

    def __init__(self):
        super(TransactionData, self).__init__()
        self.response = None
        self.response_code = None
        self.text = None
        self.content = {}

    def set_response(self, response):
        self.result = True
        self.response = response
        return response

    def set_text(self, text):
        self.text = text

    def set_response_code(self, code):
        self.response_code = code

    def add_content(self, key, value):
        if isinstance(key, str):
            self.content[key] = value
        else:
            raise TypeError("key must be an string parameter")


class PaymentData(object):
    amount = None
    transaction_id = None
    ready = False

    def __init__(self, transaction_id, amount):
        self.amount = amount
        self.transaction_id = transaction_id

    def is_ready(self):
        return self.ready

    def set_ready(self):
        self.ready = True
