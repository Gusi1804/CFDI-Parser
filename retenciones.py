from xml.dom.minidom import parse, Node
from decimal import Decimal
import glob, os


def main():
    for filename in glob.iglob('//Users/gustavogarfias/Library/CloudStorage/OneDrive-Personal/Casa/Contaduría DiDi y Uber/CFDI Parser/retenciones/**', recursive=True):
        if os.path.isfile(filename):  # filter dirs
            folio_with_extension = filename.split('/')[-1].split('.')
            extension = folio_with_extension[1]
            folio = folio_with_extension[0]

            # print(filename)

            with open('processed-rets.txt', 'r') as f:  # open the file
                contents = f.readlines()  # put the lines to a variable.

                if extension == "xml" and folio.lower() not in contents[0].lower():
                    # print(folio)
                    result = {
                        'folio': folio
                    }

                    def remove_whitespace(node):
                        if node.nodeType == Node.TEXT_NODE:
                            if node.nodeValue.strip() == "":
                                node.nodeValue = ""
                            for child in node.childNodes:
                                remove_whitespace(child)

                    document = parse(f"retenciones/{folio}.xml")
                    remove_whitespace(document)
                    document.normalize()

                    result['fecha'] = dict(document.documentElement.attributes.items())['FechaExp']

                    # print(document.documentElement.childNodes)
                    for node in document.documentElement.childNodes:
                        # print(node)
                        if node.nodeType != Node.TEXT_NODE:
                            if node.tagName == "retenciones:Emisor":
                                #  retenciones:Periodo
                                attributes = dict(node.attributes.items())
                                rfc = attributes['RfcE']
                                if rfc == "UBV121024TN8":
                                    result['emisor'] = 'Uber'
                                if rfc == "DMI1712045J9":
                                    result['emisor'] = 'DiDi'
                                # print(attributes)
                            if node.tagName == "retenciones:Periodo":
                                #  retenciones:Periodo
                                attributes = dict(node.attributes.items())
                                result['inicio'] = int(attributes['MesIni'])
                                result['final'] = int(attributes['MesFin'])
                                result['ejercicio'] = attributes['Ejercicio']
                            if node.tagName == "retenciones:Totales":
                                #  retenciones:Periodo
                                attributes = dict(node.attributes.items())
                                total = attributes['MontoTotOperacion']
                                result['total'] = Decimal(total)

                    results = open("res-rets.csv", "a+")
                    results.write(
                        f'{result["total"]},,,,,,{result["inicio"]},{result["final"]},{result["ejercicio"]},{result["fecha"]},{result["emisor"]},{result["folio"].upper()}\n'
                    )  # Write results to res.txt file
                    results.close()

                    processed = open("processed-rets.txt", "a+")
                    processed.write(
                        f'{folio.upper()},'
                    )  # Write results to res.txt file
                    processed.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()