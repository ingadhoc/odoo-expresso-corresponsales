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

import time
import datetime
import traceback
import urllib2
import re
from os.path import basename
from urlparse import urlsplit
import base64

import logging
from osv import osv, fields
from suds.client import Client
from lxml import objectify # http://lxml.de/objectify.html

from actualizador_generico import Actualizador_Generico
import configuracion_actualizacion

_logger = logging.getLogger(__name__)

class Actualizador_Titulos(Actualizador_Generico):
    
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_titulos)
        
    def obtener_info_objeto_remoto(self, cr, uid, sync_info, context=None):
        '''
        Esta función recibe cual fue la última actualización que se ejecuto y obtiene (desde los Web Services de Expresso)
        los ISBNs que insertaron a partir de ese entonces. Si alguno de estos ISBN ya existe no se hace nada, si no existe se
        crea un nuevo registro en la base de datos.
        '''
        _logger.info('Obteniendo nuevos ISBNs')
        
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        # Se forma la cadena para pedir los ISBNs agregados desde la última actualización.
        if sync_info:
            dt = self.get_string_datetime(sync_info)
            year = dt[0:4]
            month = dt[5:7]
            day = dt[8:10]
            hour = dt[11:13]
            minute = dt[14:16]
            second = dt[17:19]
        else:
            year = configuracion_actualizacion.default_year
            month = configuracion_actualizacion.default_month
            day = configuracion_actualizacion.default_day
            hour = configuracion_actualizacion.default_hour
            minute = configuracion_actualizacion.default_minute
            second = configuracion_actualizacion.default_second
        
        parametro = '<libro><FMo>' + year + month + day + hour + minute + second + '</FMo></libro>'
        # Se pide la lista de los nuevos ISBNs a través de los WS.
        try:
            new_isbns_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
            new_isbns = objectify.fromstring(new_isbns_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services para obtener los nuevos ISBNs. Error: %s', e)
            return False
        
        if hasattr(new_isbns, 'error'):
            _logger.info('No hay nuevos ISBNs')
            return True
        
        isbns_agregados = 0
        for new_isbn_it in new_isbns.iterchildren():
            isbns_agregados += 1
            isbn = new_isbn_it.isbn
            
            info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
            sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
            
            filtros = [('id_remoto', '=', isbn), ('class', '=', 'product.product')]
            info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
            
            if not info_objeto_ids:
                vals = {}
                vals['id_remoto'] = isbn
                vals['class'] = 'product.product'
                info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
            
            if not isinstance(info_objeto_ids, list):
                info_objeto_ids = [info_objeto_ids]
            
            for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                    vals = {}
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    vals['datetime_creation'] = now
                    vals['info_objeto_remoto_id'] = info_objeto.id
                    sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos ISBNs', str(isbns_agregados))
        return True
    
    def actualizar_un_libro_desde_info_objeto_id(self, cr, uid, info_objeto_id, context=None):
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        filtros = [('info_objeto_remoto_id.id', '=', info_objeto_id), ('procesado', '=', False)]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        sincronizacion_objeto = sinc_obj.browse(cr, uid, sinc_a_procesar, context=context)
        
        if not sincronizacion_objeto:
            return False
        if isinstance(sincronizacion_objeto, list):
            sincronizacion_objeto = sincronizacion_objeto[0]
        return self.actualizar_un_libro(cr, uid, sincronizacion_objeto, context=context)
    
    
    def actualizar_un_libro(self, cr, uid, sincronizacion, context=None):
        if sincronizacion.procesado:
            return False
        cliente = self.get_cliente()
        if not cliente:
            return False
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        
        isbn = sincronizacion.info_objeto_remoto_id.id_remoto
        # Se obtiene la factura desde el WS y se convierte en objeto
        parametro = '<libro><isbn>' + isbn + '</isbn></libro>'
        try:
            libros_x_isbn_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
            libros_x_isbn = objectify.fromstring(libros_x_isbn_xml)
        # Si hay se marca el error en el registro
        except:
            e = traceback.format_exc()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = e
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        
        # Si se devolvio 'error' en el atributo del objeto entonces se marca el error en el registro
        if hasattr(libros_x_isbn, 'error'):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = libros_x_isbn.error
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        
        # Se procesa la factura y se marca el registro como procesado y se indica que no necesita ser reprocesado
        libro_x_isbn = libros_x_isbn.libro[0]
        ret = self.process_titulo(cr, uid, libro_x_isbn, context=context)
        if ret:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = False
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return True
        else:
            return False
    
    def actualizar_libros(self, cr, uid, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        filtros = [('procesado', '=', False), ('info_objeto_remoto_id.class', '=', 'product.product')]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        
        # Cantidad de titulos procesados correctamente
        titulos_procesados = 0
        # Cantidad de iteraciones del bucle
        iteraciones = 0
        
        _logger.info('Hay %s Titulos para procesar', len(sinc_a_procesar))
        
        for sincronizacion in sinc_obj.browse(cr, uid, sinc_a_procesar, context=context):
            # Para no bloquear tanto el trafico de internet
            time.sleep(1)
            
            isbn = sincronizacion.info_objeto_remoto_id.id_remoto
            # Si se itero un cierto numero de veces entonces se publica un mensaje en el log
            if iteraciones % configuracion_actualizacion.books_frequency_print_working == 0:
                _logger.info('Procesando Titulos')
            iteraciones += 1
            # Si se itero un cierto numero de veces entonces se sale del bucle
            if iteraciones > configuracion_actualizacion.books_update_quantity:
                break
            ret = self.actualizar_un_libro(cr, uid, sincronizacion, context=context)
            if ret:
                titulos_procesados += 1
        
        _logger.info('Se procesaron finalmente %s Titulos', titulos_procesados)
        
    
    def process_titulo(self, cr, uid, libro, context=None):
        '''
        Recibe un libro (objetificado, con la información desde los WS), se extraen los campos desde el objeto creando un
        nuevo libro si este no existe en la BD o actualizandolo si existe.
        '''
        isbn = libro.isbn
        autor = libro.autor
        name = libro.titulo
        editorial = libro.editorial
        default_code = libro.ean
        numero_paginas = libro.paginas
        anio_edicion = libro.anoedicion
        numero_edicion = libro.numeroedicion
        volumen = libro.volumen
        edad_recomendada_min = libro.edadrecomendada
        edad_recomendada_max = libro.edadrecomendadahasta
        alto = libro.alto
        ancho = libro.ancho
        espesor = libro.grueso
        peso = libro.peso
        soporte = libro.soporte
        sinopsis = libro.extracto.text
        list_price = libro.precioeuros
        precio_dolares = libro.preciodolares
        materia_cdu = libro.cdu
        caratula = libro.caratula
        
        # idioma_id
        idioma_id = False
        idioma_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.idioma', libro.IDidioma, context=context)
        if idioma_ids:
            idioma_id = idioma_ids[0]
        
        # encuadernacion_id
        encuadernacion_id = False
        encuadernacion_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.encuadernacion', libro.IDencuadernacion, context=context)
        if encuadernacion_ids:
            encuadernacion_id = encuadernacion_ids[0]
        
        # coleccion_id
        coleccion_id = False
        coleccion_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.coleccion', libro.IDcoleccion, context=context)
        if coleccion_ids:
            coleccion_id = coleccion_ids[0]
            
        # materia_id
        materia_id = False
        materia_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.materia', libro.IDmateria, context=context)
        if materia_ids:
            materia_id = materia_ids[0]
        
        #proyecto_id
        proyecto_id = False
        if materia_id:
            materia = self.pooler.get_pool(cr.dbname).get('expresso.materia').browse(cr, uid, materia_id, context=context)
            proyecto_id = materia.proyecto_id.id
        
        # situacion_id
        situacion_id = False
        situacion_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.situacion', libro.IDsituacion, context=context)
        if situacion_ids:
            situacion_id = situacion_ids[0]
        
        # ciclo_id
        ciclo_id = False
        ciclo_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.ciclo', libro.IDciclo, context=context)
        if ciclo_ids:
            ciclo_id = ciclo_ids[0]
        
        # curso_id
        curso_id = False
        curso_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.curso', libro.IDcurso, context=context)
        if curso_ids:
            curso_id = curso_ids[0]
        
        # tipo_id
        tipo_id = False
        tipo_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.tipo', libro.IDtipo, context=context)
        if tipo_ids:
            tipo_id = tipo_ids[0]
        
        # publico_id
        publico_id = False
        publico_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.publico', libro.IDpublicoobjetivo, context=context)
        if publico_ids:
            publico_id = publico_ids[0]
        
        # product_image
        product_image = False
        if caratula:
            if 'http:' not in caratula:
                img_url = 'http://www.expressobibliografico.com/' + libro.caratula
            else:
                img_url = caratula
            try:
                img_data = urllib2.urlopen(img_url).read()
                product_image = base64.encodestring(img_data)
            except:
                pass
            
        # Los nuevos valores del titulo.
        new_values = {'isbn': isbn, 'autor': autor, 'name': name, 'editorial': editorial, 'default_code': default_code,
                      'idioma_id': idioma_id, 'numero_paginas': numero_paginas, 'anio_edicion': anio_edicion,
                      'numero_edicion': numero_edicion, 'encuadernacion_id': encuadernacion_id, 'coleccion_id': coleccion_id,
                      'volumen': volumen, 'materia_id': materia_id, 'edad_recomendada_min': edad_recomendada_min,
                      'edad_recomendada_max': edad_recomendada_max, 'situacion_id': situacion_id, 'ciclo_id': ciclo_id,
                      'curso_id': curso_id, 'tipo_id': tipo_id, 'alto': alto, 'ancho': ancho, 'espesor': espesor, 'peso': peso,
                      'soporte': soporte, 'publico_id': publico_id, 'sinopsis': sinopsis, 'proyecto_id': proyecto_id,
                      'list_price': list_price, 'precio_dolares': precio_dolares, 'materia_cdu': materia_cdu,
                      'caratula': caratula, 'product_image': product_image}
        
        # Si existe un libro con el isbn en la BD se actualiza, sino se crea uno nuevo.
        product_obj = self.pooler.get_pool(cr.dbname).get('product.product')
        stored_product_ids = product_obj.search(cr, uid, [('isbn', '=', isbn)], context=context)
        if not stored_product_ids:
            stored_product_ids = [product_obj.create(cr, uid, new_values)]
        else:
            product_obj.write(cr, uid, stored_product_ids, new_values)
        
        return stored_product_ids
    
    def actualizar_imagenes(self, cr, uid, context=None):
        product_obj = self.pooler.get_pool(cr.dbname).get('product.product')
        filtros = [('caratula', '!=', False),('caratula', '!=', ''),('product_image', '=', False)]
        product_ids = product_obj.search(cr, uid, filtros, context=context)
        
        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        _logger.info('Hay %s imagenes de Titulos para procesar', len(product_ids))
        
        iteraciones = 0
        imagenes_procesados = 0
        for libro in product_obj.browse(cr, uid, product_ids, context=context):
            # Si se itero un cierto numero de veces entonces se publica un mensaje en el log
            if iteraciones % configuracion_actualizacion.images_frequency_print_working == 0:
                _logger.info('Procesando Imagenes')
            iteraciones += 1
            
            # Si se itero un cierto numero de veces entonces se sale del bucle
            if iteraciones > configuracion_actualizacion.images_update_quantity:
                break
            
            if 'http:' not in libro.caratula:
                img_url = 'http://www.expressobibliografico.com/' + libro.caratula
            else:
                img_url = libro.caratula
            
            try:
                img_data = urllib2.urlopen(img_url).read()
                vals = {'product_image': base64.encodestring(img_data)}
                product_obj.write(cr, uid, libro.id, vals, context=context)
                imagenes_procesados += 1
            except:
                pass
                #_logger.error('Ocurrio un error al cargar la imagen en: %s', img_url)
        
        _logger.info('Se procesaron finalmente %s imagenes', imagenes_procesados)







    # Obtener ISBNs masivamente 
    def obtener_info_objeto_remoto_si_no_presente(self, cr, uid, context=None):
        '''
        Esta función obtiene todos los ISBNs y solamente inserta aquellos que no estan presentes en la base de
        datos actualmente.
        '''
        _logger.info('Obteniendo nuevos ISBNs si no presentes')
        
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        fecha = configuracion_actualizacion.default_date_isbn_obtener_si_no_presente
        parametro = '<libro><FMo>' + fecha + '</FMo></libro>'
        
        # Se pide la lista de los nuevos ISBNs a través de los WS.
        try:
            new_isbns_xml = cliente.service.listTitulos(parametro).encode("iso-8859-1").replace('&','&amp;')
            new_isbns = objectify.fromstring(new_isbns_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services para obtener los nuevos ISBNs. Error: %s', e)
            return False
        
        if hasattr(new_isbns, 'error'):
            _logger.info('No hay nuevos ISBNs')
            return True
        
        isbns_agregados = 0
        iteraciones = 0
        lista_isbns_agregados = []
        for new_isbn_it in new_isbns.iterchildren():
            iteraciones += 1
            if iteraciones % configuracion_actualizacion.books_frequency_isbn_si_no_presente == 0:
                _logger.info('Obteniendo nuevos ISBNs si no presentes')
            
            isbn = new_isbn_it.isbn
            
            info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
            sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
            
            filtros = [('id_remoto', '=', isbn), ('class', '=', 'product.product')]
            info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
            
            if not info_objeto_ids:
                isbns_agregados += 1
                vals = {}
                vals['id_remoto'] = isbn
                vals['class'] = 'product.product'
                info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
                lista_isbns_agregados.append(isbn)
                
                if not isinstance(info_objeto_ids, list):
                    info_objeto_ids = [info_objeto_ids]
                
                for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                    if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                        vals = {}
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        vals['datetime_creation'] = now
                        vals['info_objeto_remoto_id'] = info_objeto.id
                        sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos ISBNs', str(isbns_agregados))
        _logger.info('Los ISBNs agregados son: %s', str(lista_isbns_agregados))
        return True
        
        
        
        
        
        
    def marcar_todos_isbns_para_actualizar(self, cr, uid, datetime=False, context=None):
        '''
        Marca todos los registros de ISBN de la base de datos para ser procesados.
        '''
        _logger.info('Marcando ISBNs para reprocesar')
        
        info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        
        filters = [('class', '=', 'product.product')]
        if datetime:
            filters.append(('datetime_creation',  '<=', datetime))
        
        all_info_objeto_remoto_ids = info_objeto_obj.search(cr, uid, filters, context=context)
        
        isbns_agregados = 0
        iteracion = 0
        for info_objeto in info_objeto_obj.browse(cr, uid, all_info_objeto_remoto_ids, context=context):
            iteracion += 1
            if iteracion % configuracion_actualizacion.frequency_registro_reprocesar == 0:
                _logger.info('Marcando ISBNs para reprocesar')
            
            isbn = info_objeto.id_remoto
            if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                isbns_agregados += 1
                vals = {}
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vals['datetime_creation'] = now
                vals['info_objeto_remoto_id'] = info_objeto.id
                sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se marcaron %s ISBNs para reprocesar', str(isbns_agregados))
        return True
    
    def marcar_todos_isbns_para_actualizar(self, cr, uid, context=None):
        '''
        Marca todos los registros de ISBN de la base de datos para ser procesados.
        '''
        _logger.info('Marcando ISBNs para reprocesar')
        
        info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        
        all_info_objeto_remoto_ids = info_objeto_obj.search(cr, uid, [('class', '=', 'product.product')], context=context)
        
        isbns_agregados = 0
        iteracion = 0
        for info_objeto in info_objeto_obj.browse(cr, uid, all_info_objeto_remoto_ids, context=context):
            iteracion += 1
            if iteracion % configuracion_actualizacion.frequency_registro_reprocesar == 0:
                _logger.info('Marcando ISBNs para reprocesar')
            
            isbn = info_objeto.id_remoto
            if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                isbns_agregados += 1
                vals = {}
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vals['datetime_creation'] = now
                vals['info_objeto_remoto_id'] = info_objeto.id
                sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se marcaron %s ISBNs para reprocesar', str(isbns_agregados))
        return True


