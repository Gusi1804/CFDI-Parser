from unicodedata import decimal
from xml.dom.minidom import parse, parseString
from decimal import Decimal
import glob, os


def main():
    for filename in glob.iglob('//Users/gustavogarfias/Library/CloudStorage/OneDrive-Personal/Casa/Contaduría DiDi y Uber/CFDI Parser/cfdis/**', recursive=True):
        if os.path.isfile(filename):  # filter dirs
            folio_with_extension = filename.split('/')[-1].split('.')
            extension = folio_with_extension[1]
            folio = folio_with_extension[0]

            with open('processed.txt', 'r') as f:  # open the file
                contents = f.readlines()  # put the lines to a variable.

                if extension == "xml" and folio.lower() not in contents[0].lower():
                    # print(folio)
                    document = parse(f"cfdis/{folio}.xml")

                    attributes = dict(document.documentElement.attributes.items())
                    subtotal = Decimal(attributes['SubTotal'])
                    total = Decimal(attributes['Total'])
                    fecha = attributes['Fecha']
                    iva = total - subtotal
                    print(folio, subtotal, iva, total, fecha)

                    results = open("res.csv", "a+")
                    results.write(
                        f'{total},{subtotal},{iva},{fecha},{folio.upper()}\n'
                    )  # Write results to res.txt file
                    results.close()

                    processed = open("processed.txt", "a+")
                    processed.write(
                        f'{folio.upper()},'
                    )  # Write results to res.txt file
                    processed.close()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
