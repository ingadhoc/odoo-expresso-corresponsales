# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

url_ciclos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Ciclos.php?wsdl'
url_colecciones = 'http://www.expressobibliografico.com/ExpressoWS/WS_Colecciones.php?wsdl'
url_cursos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Cursos.php?wsdl'
url_encuadernaciones = 'http://www.expressobibliografico.com/ExpressoWS/WS_Encuadernaciones.php?wsdl'
url_formas_envio = 'http://www.expressobibliografico.com/ExpressoWS/WS_FormasEnvio.php?wsdl'
url_idiomas = 'http://www.expressobibliografico.com/ExpressoWS/WS_Idiomas.php?wsdl'
url_proyectos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Proyectos.php?wsdl'
url_publicos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Publicos.php?wsdl'
url_situaciones = 'http://www.expressobibliografico.com/ExpressoWS/WS_Situaciones.php?wsdl'
url_tipos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Tipos.php?wsdl'
url_valores = 'http://www.expressobibliografico.com/ExpressoWS/WS_Valores.php?wsdl'
url_directores = 'http://www.expressobibliografico.com/ExpressoWS/WS_Directores.php?wsdl'
url_materias = 'http://www.expressobibliografico.com/ExpressoWS/WS_Materias.php?wsdl'
url_selecciones = 'http://www.expressobibliografico.com/ExpressoWS/WS_Selecciones.php?wsdl'

url_titulos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Titulos.php?wsdl'
url_clientes = 'http://www.expressobibliografico.com/ExpressoWS/WS_Clientes.php?wsdl'
url_facturas = 'http://www.expressobibliografico.com/ExpressoWS/WS_Facturas.php?wsdl'
url_packing = 'http://www.expressobibliografico.com/ExpressoWS/WS_Packing.php?wsdl'
url_pedidos = 'http://www.expressobibliografico.com/ExpressoWS/WS_Pedidos.php?wsdl'

# Esto es después de cuantos registros marcados para procesados se muestra que se sigue trabajando en las funciones
# en las que se marcan todos los registros de la base de datos para reprocesar.
frequency_registro_reprocesar = 5000

''' Titulos '''
# Cantidad de veces que se van a tratar de traer titulos por ejecución
books_update_quantity = 2000
# Esto es después de cuantos objetos procesados se muestra que se sigue trabajando
books_frequency_print_working = 50
# Esto es después de cuantos ISBNs procesados se muestra que se sigue trabajando en obtener_info_objeto_remoto_si_no_presente
books_frequency_isbn_si_no_presente = 1000
# Cantidad de veces que se van a tratar de traer imagenes por ejecución
images_update_quantity = 250
# Esto es después de cuantas imagenes procesadas se muestra que se sigue trabajando
images_frequency_print_working = 50
# Momento por defaults para traer los libros si no hay ningún registro
default_year = '2012'
default_month = '01'
default_day = '01'
default_hour = '01'
default_minute = '00'
default_second = '00'
# Momento por defaults para traer los libros con la función obtener_info_objeto_remoto_si_no_presente
default_date_isbn_obtener_si_no_presente = '20120401010000'


''' Facturas '''
# Cantidad de veces que se van a tratar de traer facturas por ejecucion
#invoice_update_quantity = 200
invoice_update_quantity = 200
# Cantidad de iteraciones para mostrar que se esta trabajando
invoice_frequency_print_working = 50

''' Packing '''
# Cantidad de veces que se van a tratar de traer facturas por ejecución
packing_update_quantity = 200
# Esto es después de cuantos objetos procesados se muestra que se sigue trabajando
packing_frequency_print_working = 50
