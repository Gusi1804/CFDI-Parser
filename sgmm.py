from xml.dom.minidom import parse, Node
from decimal import Decimal
import glob, os


def main():
    for filename in glob.iglob('//Users/gustavogarfias/Library/CloudStorage/OneDrive-Personal/Casa/Contaduría DiDi y Uber/CFDI Parser/sgmm/**', recursive=True):
        if os.path.isfile(filename):  # filter dirs
            folio_with_extension = filename.split('/')[-1].split('.')
            extension = folio_with_extension[1]
            file_name_no_ext = folio_with_extension[0]

            # print(filename)

            with open('processed-sgmm.txt', 'r') as f:  # open the file
                contents = f.readlines()  # put the lines to a variable.

                if extension.lower() == "xml" and file_name_no_ext.lower() not in contents[0].lower():
                    # print(folio)
                    result = {
                        'filename': file_name_no_ext,
                        'IVA': Decimal(0.00)
                    }

                    def remove_whitespace(node):
                        if node.nodeType == Node.TEXT_NODE:
                            if node.nodeValue.strip() == "":
                                node.nodeValue = ""
                            for child in node.childNodes:
                                remove_whitespace(child)

                    document = parse(f"sgmm/{file_name_no_ext}.xml")
                    remove_whitespace(document)
                    document.normalize()

                    result['fecha'] = dict(document.documentElement.attributes.items())['Fecha']
                    result['subtotal'] = Decimal(dict(document.documentElement.attributes.items())['SubTotal'])
                    result['total'] = Decimal(dict(document.documentElement.attributes.items())['Total'])

                    if "descuento" in dict(document.documentElement.attributes.items()):
                        result['descuento'] = dict(document.documentElement.attributes.items())['Descuento']
                    else:
                        result['descuento'] = Decimal(0.00)

                    # print(document.documentElement.childNodes)
                    for node in document.documentElement.childNodes:
                        # print(node)
                        if node.nodeType != Node.TEXT_NODE:
                            if node.tagName == "cfdi:Emisor":
                                #  cfdi:Emisor
                                attributes = dict(node.attributes.items())
                                result['emisor_rfc'] = attributes['Rfc']
                                result['emisor_nombre'] = attributes['Nombre']
                            if node.tagName == "cfdi:Conceptos":
                                #  cfdi:Conceptos
                                result['conceptos'] = []
                                for node_concepto in node.childNodes:
                                    if node_concepto.nodeType != Node.TEXT_NODE:
                                        # print(node_concepto)
                                        # Concepto
                                        concepto = {
                                            'IVA': Decimal(0.00)
                                        }
                                        attributes = dict(node_concepto.attributes.items())

                                        concepto['cantidad'] = Decimal(attributes['Cantidad'])
                                        concepto['descripcion'] = attributes['Descripcion']
                                        concepto['valor_unitario'] = Decimal(attributes['ValorUnitario'])
                                        concepto['importe'] = Decimal(attributes['Importe'])

                                        if "Descuento" in attributes:
                                            concepto['descuento'] = Decimal(attributes['Descuento'])
                                        else:
                                            concepto['descuento'] = Decimal(0.00)
                                        

                                        for node_imp in node_concepto.childNodes:
                                            # Impuestos
                                            if node_imp.nodeType != Node.TEXT_NODE:
                                                for node_tras in node_imp.childNodes:
                                                # Traslados
                                                    if node_tras.nodeType != Node.TEXT_NODE:
                                                        for node_traslado in node_tras.childNodes:
                                                            if node_traslado.nodeType != Node.TEXT_NODE:
                                                                attributes = dict(node_traslado.attributes.items())
                                                                # print(node_tras)
                                                                if attributes['Impuesto'] == "002":
                                                                    concepto['IVA'] = Decimal(attributes['Importe'])
                                                                    result['IVA'] = result['IVA'] + concepto['IVA']

                                        result['conceptos'].append(concepto)  

                            if node.tagName == "cfdi:Complemento":
                                # Complemento  
                                for child in node.childNodes:
                                    if child.nodeType != Node.TEXT_NODE and child.tagName == "tfd:TimbreFiscalDigital":
                                        attributes = dict(child.attributes.items())
                                        result['folio'] = attributes['UUID'].upper()
                                        print(result['folio'])
                            
                            print(result)
                            print('\n')

                    
                    results = open("res-sgmm-cfdis.csv", "a+")
                    results.write(
                        f'{result["total"]},{result["fecha"]},{result["emisor_nombre"]},{result["subtotal"]},{result["IVA"]},{result["descuento"]},{result["emisor_rfc"]},{result["folio"].upper()}\n'
                    )  # Write results to res-sgmm-cfdis.csv file
                    results.close()

                    for concepto in result['conceptos']:
                        results = open("res-sgmm-conceptos.csv", "a+")
                        results.write(
                            f'{concepto["importe"]},{concepto["descripcion"]},{concepto["cantidad"]},{concepto["descuento"]},{concepto["IVA"]},{result["emisor_rfc"]},{result["fecha"]},{result["folio"].upper()}\n'
                        )  # Write results to res-sgmm-conceptos.csv file
                        results.close()
                    
                    

                    processed = open("processed-sgmm.txt", "a+")
                    processed.write(
                        f'{result["folio"].upper()},'
                    )  # Write folio to processed-sgmm.txt file
                    processed.close()

                    print(result)
                    
                    if file_name_no_ext != result['folio'].upper():
                        os.rename(f'{filename}', f'sgmm/{result["folio"].upper()}.xml')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()