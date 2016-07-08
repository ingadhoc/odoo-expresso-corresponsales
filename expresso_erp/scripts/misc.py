from suds.client import Client
from lxml import objectify

# Titulo
def print_isbns(day='01', month='09', year='2012', hour='01', minute ='00', second ='00'):
    url_titulos = 'http://www.expressows.tk/ExpressoWSP/WS_Titulos.php?wsdl'
    cliente = Client(url_titulos)

    parametro = '<libro><FMo>' + year + month + day + hour + minute + second + '</FMo></libro>'
    new_isbns_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
    new_isbns = objectify.fromstring(new_isbns_xml)
    
    if hasattr(new_isbns, 'error'):
        print 'No hay nuevos ISBNs'
        return True
    
    idx = 0
    for new_isbn_it in new_isbns.iterchildren():
        print '%s' % (new_isbn_it.isbn)
        idx += 1
    print 'idx: %s' % idx

def buscar_isbns(isbn, day='01', month='09', year='2012', hour='01', minute ='00', second ='00'):
    url_titulos = 'http://www.expressows.tk/ExpressoWSP/WS_Titulos.php?wsdl'
    cliente = Client(url_titulos)
    
    print 'Buscando ISBNs a partir del %s/%s/%s %s:%s:%s' % (day, month, year, hour, minute, second)
    
    parametro = '<libro><FMo>' + year + month + day + hour + minute + second + '</FMo></libro>'
    new_isbns_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
    new_isbns = objectify.fromstring(new_isbns_xml)
    
    if hasattr(new_isbns, 'error'):
        print 'No hay nuevos ISBNs'
        return
        
    idx = 0
    
    for new_isbn_it in new_isbns.iterchildren():
        idx += 1;
        if new_isbn_it.isbn == isbn:
            print 'Encontrado! %s' % (new_isbn_it.isbn)
    
    print 'Hay %s ISBNs' % idx
    
def print_book(isbn):
    url_titulos = 'http://www.expressows.tk/ExpressoWSP/WS_Titulos.php?wsdl'
    cliente = Client(url_titulos)
    parametro = '<libro><isbn>' + isbn + '</isbn></libro>'
    libros_x_isbn_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
    print libros_x_isbn_xml
    #libros_x_isbn = objectify.fromstring(libros_x_isbn_xml)
    #libro = libros_x_isbn.libro[0]
    #print 'isbn: %s' % libro.isbn
    #print 'autor: %s' % libro.autor
    #print 'name: %s' % libro.titulo
    #print 'precio_dolares: %s' % libro.preciodolares

def test_book():
    url_titulos = 'http://www.expressows.tk/ExpressoWSP/WS_Titulos.php?wsdl'
    cliente = Client(url_titulos)
    parametro = '<libro><FMo>20120101010000</FMo></libro>'
    #parametro = '<libro><FMo>20120131000000</FMo></libro>'
    libros_x_isbn_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
    print 'libros_x_isbn_xml: ' + str(libros_x_isbn_xml)

# Facturas

def print_invoice():
    url_facturas = 'http://www.expressows.tk/ExpressoWSP/WS_Facturas.php?wsdl'
    cliente = Client(url_facturas)

    factura_xml = cliente.service.getFactura(usuario='114', password='magisterio', id='8836').encode("iso-8859-1").replace('&','&amp;')
    print factura_xml
    factura = objectify.fromstring(factura_xml)

# Main
def main():
    print_isbns()

if __name__ == "__main__":
    main()
