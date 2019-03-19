STX = chr(0x02)
ETX = chr(0x03)
ACK = chr(0x06)

MAX_ATTEMPT = 5

MSG_RESPUESTA = "'"
MSG_TIP_TARJETA = "pos.messaje.tarjeta_"

TX_RESPUESTA = 1
TX_CODIGO_COMERCIO = 2
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
    '14': 'No hay Tono.',
    '15': 'Archivo BITMAP.DAT no encontrado. Favor cargue.',
    '16': 'Error Formato Respuesta del HOST.',
    '17': 'Error en los 4 \u00faltimos d\u00edgitos.',
    '18': 'Men\u00fa invalido.',
    '19': 'ERROR_TARJ_DIST.',
    '20': 'Tarjeta Invalida.',
    '21': 'Anulaci\u00f3n. No Permitida.',
    '22': 'TIMEOUT.',
    '24': 'Impresora Sin Papel.',
    '25': 'Fecha Invalida.',
    '26': 'Debe Cargar Llaves.',
    '57': 'Digito verificador no corresponde.',
    '68': 'Tarjeta con fecha expirada.',
    '70': 'Error de formato Campo de Boleta MAX 6.',
    '80': 'Solicitando Conformar Monto.',
    '81': 'Solicitando Ingreso de Clave.',
    '82': 'Enviando transacci\u00f3n al Host.',
    '88': 'Error Cantidad Cuotas.',
    '93': 'Declinada.',
}
