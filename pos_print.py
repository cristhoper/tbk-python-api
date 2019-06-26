from xhtml2pdf import pisa
import win32print
import win32api

PDF_PATHS = "C:\\FOLDER\\"


def print_pdf_file(PDFFile):
    filename = PDF_PATHS + PDFFile
    GHOSTSCRIPT_PATH = ".\\utils\\bin_files\\GHOSTSCRIPT\\bin\\gswin32.exe"
    GSPRINT_PATH = ".\\utils\\bin_files\\GSPRINT\\gsprint.exe"

    # YOU CAN PUT HERE THE NAME OF YOUR SPECIFIC PRINTER INSTEAD OF DEFAULT
    currentprinter = win32print.GetDefaultPrinter()

    win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "' + GHOSTSCRIPT_PATH + '" -printer "'
                          + currentprinter + '" "' + filename + '"', '.', 0)



def print_html_data(json_values):
    source_html = """
    pasen el html oe
    """
    filename = PDF_PATHS + "boleta.pdf"

    result = open(PDF_PATHS + filename, "w+b")
    pisa_status = pisa.CreatePDF(source_html, dest=result)
    result.close()  # close output file
    print_pdf_file("boleta")
    return pisa_status.err

