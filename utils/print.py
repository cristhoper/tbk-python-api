import win32print
import win32api
import sys

if len(sys.argv) == 2:
    PDFFile = sys.argv[1]
    GHOSTSCRIPT_PATH = ".\\bin_files\\GHOSTSCRIPT\\bin\\gswin32.exe"
    GSPRINT_PATH = ".\\bin_files\\GSPRINT\\gsprint.exe"

    # YOU CAN PUT HERE THE NAME OF YOUR SPECIFIC PRINTER INSTEAD OF DEFAULT
    currentprinter = win32print.GetDefaultPrinter()

    win32api.ShellExecute(0, 'open', GSPRINT_PATH, '-ghostscript "'+GHOSTSCRIPT_PATH+'" -printer "'+currentprinter+
                          '" "'+PDFFile+'"', '.', 0)
    exit(0)
else:
    print("THERE IS NO NAMEFILEINCLUDED")
    exit(1)
