STX = chr(0x02)
ETX = chr(0x03)
ACK = chr(0x06)
NAK = chr(0x15)

MAX_ATTEMPT = 3

MSG_RESPUESTA = "'"
MSG_TIP_TARJETA = "pos.messaje.tarjeta_"

TX_RESPUESTA = 1
TX_CODIGO_COMERCIO = 597029414300
TX_TERMINAL_ID = 3

VENTA_TX_NUM_VOUCHER_MAPFRE = 4
VENTA_TX_CODIGO_AUTORIZACION = 5
VENTA_TX_MONTO = 6
VENTA_TX_NUMERO_CUOTAS = 7
VENTA_TX_MONTO_CUOTA = 8
VENTA_TX_ULT_4_DIGITOS = 9
VENTA_TX_CODIGO_OPERACION = 10
VENTA_TX_TIPO_TARJETA = 11
VENTA_TX_CODIGO_TARJETA = 14
VENTA_TX_FECHA = 15
VENTA_TX_HORA = 16

ANULA_TX_CODIGO_AUTORIZACION = 4

TOKEN_PROPERTIES = {
    '00': 'Aprobado.',
    '01': 'Rechazado.',
    '02': 'Host no Responde.',
    '03': 'Conexi\u00f3n Fallo.',
    '04': 'Transacci\u00f3n ya Fue Anulada.',
    '05': 'No existe Transacci\u00f3n para Anular.',
    '06': 'Tarjeta no Soportada.',
    '07': 'Transacci\u00f3n Cancelada desde el POS.',
    '08': 'No puede Anular Transacci\u00f3n Debito.',
    '09': 'Error Lectura Tarjeta.',
    '10': 'Monto menor al m\u00ednimo permitido.',
    '11': 'No existe venta.',
    '12': 'Transacci\u00f3n No Soportada.',
    '13': 'Debe ejecutar cierre.',
    '14': 'Error encriptando PAN',
    '15': 'Error operando con debito',
    '80': 'Solicitando Conformar Monto.',
    '81': 'Solicitando Ingreso de Clave.',
    '82': 'Enviando transacci\u00f3n al Host.',
    '83': 'Seleccion de menu',
    '84': 'Opere tarjeta',
    '85': 'Seleccion de cuotas',
    '86': 'Ingreso de cuotas',
    '87': 'Confirmacion de cuotas',
    '88': 'Aceptar consulta de Cuotas.',
    '89': 'Opcion mes de gracia',
    '90': 'Inicializacion exitosa.',
    '91': 'Inicializacion fallida',
    '92': 'Lector no conectado',
    '93': 'Declinada.',
}
