from SOAPpy import WSDL
from SOAPpy import SOAPProxy

url = 'http://www.pydp.net/ExpressoWSP/WS_Titulos.php?wsdl'
wsdlObject = WSDL.Proxy(url)


server = SOAPProxy('http://www.pydp.net/ExpressoWSP/WS_Titulos.php')
isbn = '84-218-4334-6'
parametro = u'<libro><isbn>' + isbn + '</isbn></libro>'
server.listTitulos(parametro)
