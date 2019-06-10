from serial import Serial
from threading import RLock
from constants import *
import posutils
from transaction import TransactionData
from time import sleep, time


class TbkPos(object):
    lock = RLock()    

    def __init__(self, device, baudrate=115200):
        self.ser = Serial(device, baudrate=baudrate, timeout=3)
        self.device = device

    def __execute(self, command):
        self.lock.acquire()
        print("Sending message {}".format(command))
        self.ser.flush()
        self.ser.write(command)
        val = self.ser.readall()
        cnt = 0
        while len(val) <= 0 and cnt < MAX_ATTEMPT:
            print("Sending message {}".format(command))
            self.ser.write(command)
            val = self.ser.readall()
            cnt += 1
        self.lock.release()
        print("Received message {}".format(val))
        return val.decode('utf-8')

    def __wait_data(self, timeout=10):
        val = ''
        c_t = 0
        i_t = time()
        while len(val) <= 0 and c_t - i_t < timeout:
            val = self.ser.readall()
            c_t = time()
        return val.decode('utf-8')

    @staticmethod
    def __get_properties(token):
        message = None
        try:
            message = TOKEN_PROPERTIES[token]
        except KeyError:
            message = "Token not found: {}".format(token)
        return message

    @staticmethod
    def __get_flags(in_stream, flag_number):
        i = 0
        flag = False
        if len(in_stream) <= 0:
            return flag
        print(in_stream)
        data = str(in_stream).split('|')
        print(data)
        for token in data:
            if i == flag_number:
                flag = token
            i += 1
        if not flag and flag_number == VENTA_TX_MONTO_CUOTA:
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
            result = obj.set_response(self.__execute(cmd_hex))
            if result == ACK:
                obj.result = True
                obj.set_text("Inicializado")
            else:
                obj.set_text("Problema al conectar")
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def ack(self):
        obj = TransactionData()
        cmd = ACK
        cmd_hex = posutils.hex_string(cmd)
        try:
            obj.set_response(self.__execute(cmd_hex))
            obj.result = True
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def load_keys(self):
        obj = TransactionData()
        cmd = STX + "0800" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            if result[0] == ACK:
                result = obj.set_response(self.__wait_data(30)[2:-2])
            flag = self.__get_flags(result, TX_RESPUESTA)
            obj.set_response_code(flag)
            if flag == "00":
                obj.result = True
                obj.add_content("codigo_comercio", self.__get_flags(result, TX_CODIGO_COMERCIO))
                obj.add_content("terminal_id", self.__get_flags(result, TX_TERMINAL_ID))
        except IOError as err:
            print("More errors: {}".format(err))
        return obj
                                              
    def polling(self):
        print("POS POLLING...")
        obj = TransactionData()
        cmd = STX + "0100" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            if result == ACK:
                obj.result = True
                obj.set_text("Conexion establecida en puerto: {}".format(str(self.device)))
            else:
                obj.set_text("Puerto incorrecto, intente con otro puerto.")
        except IOError as err:
            print("More errors: {}".format(err))
        return obj

    def sale_init(self, amount, voucher='0', dummy=False):  # , **kwargs):
        voucher = "" + str(voucher)
        print("sale_init({}, {}, {})".format(amount, voucher, dummy))
        obj = TransactionData()
        cmd = STX + "0200|" + str(amount) + "|" + str(voucher[-6:]) + "|0|1" + ETX
        cmd_hex = posutils.hex_string(cmd, crc=True)
        flag = False
        try:
            result = obj.set_response(self.__execute(cmd_hex))
            if result[0] == ACK:
                result = obj.set_response(self.__wait_data()[2:-2])
                result = obj.set_response(self.__wait_data(180)[2:-2])
                flag = self.__get_flags(result, TX_RESPUESTA)
            if flag:
                obj.set_response_code(flag)
                obj.set_text(self.__get_properties(flag))
                if flag == "00":
                    obj.result = True
                    obj.add_content("num_voucher", voucher)  # VOUCHER INTERNO GENERADO POR MAPFRE
                    obj.add_content("codigo_comercio", self.__get_flags(result, TX_CODIGO_COMERCIO)) # 2
                    obj.add_content("terminal_id", self.__get_flags(result, TX_TERMINAL_ID))
                    obj.add_content("num_voucher_mapfre", self.__get_flags(result, VENTA_TX_NUM_VOUCHER_MAPFRE))# VOUCHER MAPFRE RETORNADO POR TBK
                    obj.add_content("codigo_autorizacion", self.__get_flags(result, VENTA_TX_CODIGO_AUTORIZACION))  # CODIGO AUTORIZACION TBK
                    obj.add_content("num_cuotas", self.__get_flags(result, VENTA_OP_NUMERO_CUOTAS))
                    obj.add_content("monto_cuota", self.__get_flags(result, VENTA_OP_MONTO_CUOTA))
                    obj.add_content("monto", self.__get_flags(result, VENTA_TX_MONTO))
                    obj.add_content("ult_4_numeros", self.__get_flags(result, VENTA_TX_ULT_4_DIGITOS))
                    obj.add_content("codigo_operacion", self.__get_flags(result, VENTA_TX_CODIGO_OPERACION))  # CODIGO OPERACION TBK
                    obj.add_content("tipo_tarjeta", self.__get_flags(result, VENTA_TX_TIPO_TARJETA))
                    obj.add_content("codigo_tarjeta", self.__get_flags(result, VENTA_TX_CODIGO_TARJETA))
                    obj.add_content("fecha", self.__get_flags(result, VENTA_TX_FECHA_TRANSAC))
                    obj.add_content("hora", self.__get_flags(result, VENTA_TX_HORA_TRANSAC))
            else:
                obj.add_content("status", "FAIL")
        except IOError as err:
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
            result = obj.set_response(self.__execute(cmd_hex))
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


