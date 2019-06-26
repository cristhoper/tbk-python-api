from serial import Serial
from threading import RLock
from constants import *
import posutils
from transaction import TransactionData
from time import sleep, time


class TbkPos(object):
    lock = RLock()    

    def __init__(self, device, baudrate=115200):
        self.ser = None
        self.device = None
        try:
            self.ser = Serial(device, baudrate=baudrate, timeout=3)
            self.device = device
        except:
            pass

    def __execute(self, command, nowait=False):
        self.lock.acquire()
        print("Sending message {}".format(command))
        self.ser.flush()
        self.ser.write(command)
        val = self.ser.readall()
        cnt = 0
        while len(val) <= 0 and cnt < MAX_ATTEMPT and not nowait:
            print("Sending message {}".format(command))
            self.ser.write(command)
            val = self.ser.readall()
            cnt += 1
        self.lock.release()
        print("Received message {}".format(val))
        ret = self.__extract_messages(val.decode('utf-8'))
        return ret

    def __wait_data(self, timeout=10):
        val = ''
        c_t = 0
        i_t = time()
        self.ser.flush()
        while len(val) <= 0 and c_t - i_t < timeout:
            val = self.ser.readall()
            c_t = time()

        return self.__extract_messages(val.decode('utf-8'))

    @staticmethod
    def __extract_messages(in_stream):
        messages = []
        msg_init_index = -1
        for index in range(len(in_stream)):
            # print("{}:{}[{}]".format(index, ord(in_stream[index]), in_stream[index]))
            if in_stream[index] in [ACK, NAK]:
                messages.append(in_stream[index])
            if in_stream[index] in [STX, SP1, SP2]:
                msg_init_index = index + 1
            if in_stream[index] == ETX:
                messages.append(in_stream[msg_init_index:index])
        # print("__extracted message: {}".format(messages))
        return messages

    @staticmethod
    def __get_properties(token):
        try:
            message = TOKEN_PROPERTIES[token]
        except KeyError:
            message = "Token not found: {}".format(token)
        return message

    @staticmethod
    def __get_flags(in_stream, flag_number):
        i = 0
        flag = False
        if in_stream is None or len(in_stream) <= 0:
            return flag
        print("__get_flags: {}".format(in_stream))
        data = in_stream.split('|')
        print(data)
        for token in data:
            if i == flag_number:
                flag = token
                break
            i += 1
        if not flag and flag_number == VENTA_OP_MONTO_CUOTA:
            flag = "0"
        if flag_number == TX_TERMINAL_ID:
            separator = ""+ETX
            parts = flag.split(separator)
            flag = parts[0]
        return flag

    def initialization(self):
        print("POS initialization...")
        obj = TransactionData()
        cmd = STX + "0070" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            results = obj.set_response(self.__execute(cmd_hex))
            for result in results:
                obj.set_text("Problema al conectar")
                if result == ACK:
                    obj.result = True
                    obj.set_text("Inicializado")
                    break

        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def ack(self, nowait=False):
        obj = TransactionData()
        cmd = ACK
        cmd_hex = posutils.hex_string(cmd)
        try:
            obj.set_response(self.__execute(cmd_hex, nowait=nowait))
            obj.result = True
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def load_keys(self):
        print("load_keys")
        obj = TransactionData()
        cmd = STX + "0800" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            results = obj.set_response(self.__execute(cmd_hex))
            for result in results:
                if result == ACK:
                    break

            results = obj.set_response(self.__wait_data(30))
            flag = self.__get_flags(results[0], TX_RESPUESTA)
            obj.set_response_code(flag)
            if flag == "00":
                obj.result = True
                obj.add_content("codigo_comercio", self.__get_flags(results[0], TX_CODIGO_COMERCIO))
                obj.add_content("terminal_id", self.__get_flags(results[0], TX_TERMINAL_ID))
        except Exception as err:
            print("More errors: {}".format(err))
        self.ack()
        return obj
                                              
    def polling(self):
        print("POS POLLING...")
        obj = TransactionData()
        cmd = STX + "0100" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            results = obj.set_response(self.__execute(cmd_hex))
            if results[0] == ACK:
                obj.result = True
                obj.set_text("Conexion establecida en puerto: {}".format(str(self.device)))
            else:
                obj.set_text("Puerto incorrecto, intente con otro puerto.")
        except IOError as err:
            print("More errors: {}".format(err))
        self.ack()
        return obj

    def sale_init(self, amount, voucher='0', dummy=False):  # , **kwargs):
        voucher = "" + str(voucher)
        print("sale_init({}, {}, {})".format(amount, voucher, dummy))
        obj = TransactionData()
        cmd = STX + "0200|" + str(amount) + "|" + str(voucher[-6:]) + "|0|1" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        flag = False
        try:
            results = obj.set_response(self.__execute(cmd_hex))
            print("Sends the sale")
            if results[0] == ACK:
                print("wait for more data")
                results = obj.set_response(self.__wait_data())
            result = None
            for res in results:
                print("process data: {}".format(res))
                flag = self.__get_flags(res, TX_RESPUESTA)
                while flag not in STOP_TOKENS:
                    res = obj.set_response(self.__wait_data(10))
                    for data in res:
                        flag = self.__get_flags(data, TX_RESPUESTA)
                        print("current flag: {}".format(flag))
                        if flag in STOP_TOKENS:
                            result = res
                            break
                if flag in STOP_TOKENS:
                    result = res
                    break
            print("current result: {}".format(result))
            if result is not None and flag == "00":
                print("result: {}".format(result))
                if isinstance(result, list):
                    result = result[0]
                result = result.split('|')

                obj.add_content("num_voucher", voucher)
                obj.add_content("codigo_comercio", result[TX_CODIGO_COMERCIO])
                obj.add_content("terminal_id", result[TX_TERMINAL_ID])
                obj.add_content("num_voucher_mapfre", result[VENTA_TX_NUM_VOUCHER_MAPFRE])
                obj.add_content("codigo_autorizacion", result[VENTA_TX_CODIGO_AUTORIZACION])
                obj.add_content("monto", result[VENTA_TX_MONTO])
                obj.add_content("ult_4_numeros", result[VENTA_TX_ULT_4_DIGITOS])
                obj.add_content("codigo_operacion", result[VENTA_TX_CODIGO_OPERACION])
                obj.add_content("codigo_tarjeta", result[VENTA_TX_CODIGO_TARJETA])
                obj.add_content("tipo_tarjeta", result[VENTA_TX_TIPO_TARJETA])
                obj.add_content("fecha", result[VENTA_TX_FECHA_TRANSAC])
                obj.add_content("hora", result[VENTA_TX_HORA_TRANSAC])
                obj.add_content("num_cuotas", result[VENTA_OP_NUM_CUOTA])
                obj.add_content("monto_cuota", result[VENTA_OP_MONTO_CUOTA])
                obj.add_content("status", "OK")
                obj.set_text(self.__get_properties(flag))
                obj.set_response_code(flag)
                obj.result = True
            else:
                obj.set_response_code(flag)
                obj.set_text(self.__get_properties(flag))
                obj.add_content("status", "FAIL")
            self.ack(nowait=True)
        except Exception as err:
            print("More errors: {}".format(err))
        return obj
    
    def sale_detail(self):  # TODO check return data
        obj = TransactionData()
        cmd = STX + "0260|0" + ETX + "K"
        cmd_hex = posutils.hex_string(cmd)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            if result == ACK:
                obj.result = True
                obj.set_response_code("00")
                obj.set_text("Detalle de ventas en Pos solicitado exitosamente.")
            else:
                obj.set_text("Error al obtener detalle de ventas.")
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def close(self):
        obj = TransactionData()
        cmd = STX + "0500|0" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            results = obj.set_response(self.__execute(cmd_hex))
            for result in results:
                obj.set_response_code(result[7:9])
                obj.set_text(self.__get_properties(result[7:9]))
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def all_transactions(self):
        obj = TransactionData()
        cmd = STX + "0700|0" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            while result == ACK:
                result = obj.set_response(self.__execute(cmd_hex))
            flag = self.__get_flags(result, TX_RESPUESTA)
            obj.set_text(self.__get_properties(flag))
            obj.set_response_code(flag)
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def last_sale(self):
        obj = TransactionData()
        cmd = STX + "0250|0" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            while result == ACK:
                result = obj.set_response(self.__execute(cmd_hex))
            flag = self.__get_flags(result, TX_RESPUESTA)
            obj.set_text(self.__get_properties(flag))
            obj.set_response_code(flag)
            self.ack()
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def cancel_transaction(self):  # , **kwargs):
        obj = TransactionData()
        cmd = STX + "1200" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            while result == ACK:
                result = obj.set_response(self.__execute(cmd_hex))
            flag = self.__get_flags(result, TX_RESPUESTA)
            obj.set_response_code(flag)
            obj.set_text(self.__get_properties(flag))
            if flag == "00":
                obj.result = True
                obj.add_content("codigo_comercio", self.__get_flags(result, TX_CODIGO_COMERCIO))
                obj.add_content("terminal_id", self.__get_flags(result, TX_TERMINAL_ID))
                obj.add_content("codigo_autorizacion", self.__get_flags(result, ANULA_TX_CODIGO_AUTORIZACION))
            self.ack()
        except IOError as err:
            print("More errors: {}".format(err))
        return obj


