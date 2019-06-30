# coding=utf-8

from xhtml2pdf import pisa
import win32print
import win32api

PDF_PATHS = "C:\\Program Files (x86)\\amps\\www\\htdocs\\assets\\files\\"


def print_pdf_file(pdf_file):
    filename = PDF_PATHS + pdf_file
    gsview_path = ".\\utils\\bin_files\\GHOSTSCRIPT\\bin\\gswin32.exe"
    gsprint_path = ".\\utils\\bin_files\\GSPRINT\\gsprint.exe"

    # YOU CAN PUT HERE THE NAME OF YOUR SPECIFIC PRINTER INSTEAD OF DEFAULT
    current_printer = win32print.GetDefaultPrinter()

    win32api.ShellExecute(0, 'open', gsprint_path, '-ghostscript "' + gsview_path + '" -printer "'
                          + current_printer + '" "' + filename + '"', '.', 0)


def print_html_data(data):
    invoice_values = {}
    values = data.get_content()
    invoice_keys = ["codigo_comercio", "terminal_id", "num_voucher", "codigo_autorizacion", "monto",
                    "ult_4_numeros", "codigo_operacion", "codigo_tarjeta", "tipo_tarjeta", "fecha", "hora",
                    "num_cuotas", "monto_cuota", "status", "numero_cuenta"]
    codigo_tarjeta = {"VI": "VISA", "MC": "MASTERCARD", "AX": "AMEX", "DC": "DINERS", "MG": "MAGNA", "DB": "DEBITO"}
    tipo_tarjeta = {"CR": "CREDITO", "DB": "DEBITO"}
    invoice_values["direccion_comercio"] = "ALGUNA CALLE #123, COMUNA"
    invoice_values["ciudad"] = "CIUDAD"
    try:
        invoice_values["tipo_tarjeta"] = tipo_tarjeta[values["tipo_tarjeta"]]
        invoice_values["codigo_tarjeta"] = codigo_tarjeta[values["codigo_tarjeta"]]
        invoice_values["abrev_tarjeta"] = "{}-{}".format(values["tipo_tarjeta"],values["codigo_tarjeta"])
        invoice_values["if_fecha_contable"] = "&nbsp;" if values["tipo_tarjeta"] == "CR" else "FECHA CONTABLE"
        invoice_values["fecha_contable"] = "&nbsp;" if values["tipo_tarjeta"] == "CR" else values["fecha"]
    except KeyError:
        pass

    for key in invoice_keys:
        try:
            invoice_values[key] = values[key]
        except KeyError:
            invoice_values[key] = ""

    source_html = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Untitled Document</title>
<style> table {{ max-width: 280px;}} </style>
</head>
<body>
<table width="300" border="0" cellspacing="0" cellpadding="0">
  <tbody>
    <tr>
      <td align="center">COMPROBANTE DE VENTA</td>
    </tr>
    <tr>
      <td align="center">TARJETA DE {tipo_tarjeta}</td>
    </tr>
    <tr>
      <td align="center">OPERACIONES TRANSBANK</td>
    </tr>
    <tr>
      <td align="center">{direccion}</td>
    </tr>
    <tr>
      <td align="center">{ciudad}</td>
    </tr>
    <tr>
      <td align="center">I786585585959659-V18.1A2</td>
    </tr>
    <tr>
      <td><table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
          <tr>
            <td width="33%">FECHA</td>
            <td width="34%" align="center">HORA</td>
            <td width="33%" align="right">TERMINAL</td>
          </tr>
          <tr>
            <td>{fecha}</td>
            <td align="center">{hora}</td>
            <td align="right">{terminal_id}</td>
          </tr>
        </tbody>
      </table></td>
    </tr>
    <tr>
      <td><table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
          <tr>
            <td width="50%">{if_fecha_contable}</td>
            <td width="50%" align="right">{fecha_contable}</td>
          </tr>
        </tbody>
      </table></td>
    </tr>
    <tr>
      <td><table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
          <tr>
            <td>NUMERO DE TARJETA</td>
            <td align="right">NUMERO DE CUENTA</td>
            <td align="right">MARCA</td>
          </tr>
          <tr>
            <td>{ult_4_numeros}</td>
            <td align="right">{numero_cuenta}</td>
            <td align="right">{abrev_tarjeta}</td>
          </tr>
        </tbody>
      </table></td>
    </tr>
    <tr>
      <td><table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tbody>
          <tr>
            <td>{codigo_tarjeta}</td>
            <td align="right">-</td>
          </tr>
          <tr>
            <td>TOTAL:</td>
            <td align="right">$ {monto}</td>
          </tr>
          <tr>
            <td>NUMERO DE BOLETA</td>
            <td align="right">{num_voucher}</td>
          </tr>
          <tr>
            <td>NUMERO DE OPERACIÓN:</td>
            <td align="right">{codigo_operacion}/td>
          </tr>
          <tr>
            <td>CODIGO DE AUTORIZACIÓN</td>
            <td align="right">{codigo_autorizacion}</td>
          </tr>
        </tbody>
      </table></td>
    </tr>
    <tr>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td align="center">GRACIAS POR SU COMPRA</td>
    </tr>
    <tr>
      <td align="center">ACEPTO PAGAR SEGÚN CONTRATO CON EMISOR</td>
    </tr>
  </tbody>
</table>
</body>
</html>
    """.format(**values)
    filename = PDF_PATHS + "boleta.pdf"
    result = open(PDF_PATHS + filename, "w+b")
    pisa_status = pisa.CreatePDF(source_html, dest=result)
    result.close()  # close output file
    print_pdf_file("boleta")
    return pisa_status.err

