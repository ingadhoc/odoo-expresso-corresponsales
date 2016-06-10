from suds.client import Client

url_ws = 'http://www.expressows.tk/ExpressoWS/WS_Titulos.php?wsdl'
cliente = Client(url_ws)

isbn = '84-614-2701-7'
parametro = u'<libro><isbn>' + isbn + '</isbn></libro>'
libros_x_isbn_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')

def get_libro_xml(isbn):
    parametro = '<libro><isbn>' + isbn + '</isbn></libro>'
    return cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')


libro_xml = get_libro_xml('84-218-4334-6')
