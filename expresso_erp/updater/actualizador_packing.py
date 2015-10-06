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
import sys
import traceback

import logging
from suds.client import Client
from lxml import objectify # http://lxml.de/objectify.html

from generic_updater import Actualizador_Generico
import configuracion_actualizacion

_logger = logging.getLogger(__name__)

class Actualizador_Packing(Actualizador_Generico):
    
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_packing)
    
    def obtener_info_objeto_remoto(self, cr, uid, sync_info, context=None):
        _logger.info('Obteniendo nuevos registros de Packings.')
        cliente = self.get_cliente()
        if not cliente:
            return False
        
        from_date = self.get_string_date(sync_info)
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        info_corresponsal_ids = info_corresponsal_obj.search(cr, uid, [], context=context)
        
        packing_agregados = 0
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = info_corresponsal_obj.browse(cr, uid, info_corresponsal_id, context=context)
            try:
                if from_date:
                    packing_xml = cliente.service.listPacking(usuario=info_corresponsal.usuario, 
                                                              password=info_corresponsal.contrasenia,
                                                              updated=from_date).encode("iso-8859-1").replace('&','&amp;')
                else:
                    packing_xml = cliente.service.listPacking(usuario=info_corresponsal.usuario, 
                                                              password=info_corresponsal.contrasenia).encode(
                                                                                "iso-8859-1").replace('&','&amp;')
                packings = objectify.fromstring(packing_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return False
                
            if hasattr(packings, 'error'):
                #_logger.info('No hay nuevos registros de Packing.')
                continue
            
            for packing_it in packings.iterchildren():
                packing_agregados += 1
                id_remoto = packing_it.id
                
                info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
                sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
                
                filtros = [('id_remoto', '=', id_remoto), ('class', '=', 'expresso.packing')]
                info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
                
                if not info_objeto_ids:
                    vals = {}
                    vals['id_remoto'] = id_remoto
                    vals['class'] = 'expresso.packing'
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
                else:
                    vals = {}
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_obj.write(cr, uid, info_objeto_ids, vals, context=context)
                
                if not isinstance(info_objeto_ids, list):
                    info_objeto_ids = [info_objeto_ids]
                
                for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                    if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                        vals = {}
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        vals['datetime_creation'] = now
                        vals['info_objeto_remoto_id'] = info_objeto.id
                        sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos registros de Packings para procesar', str(packing_agregados))
        return True
    
    
    def actualizar_un_packing_desde_info_objeto_id(self, cr, uid, info_objeto_id, context=None):
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        filtros = [('info_objeto_remoto_id.id', '=', info_objeto_id), ('procesado', '=', False)]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        sincronizacion_objeto = sinc_obj.browse(cr, uid, sinc_a_procesar, context=context)
        
        if not sincronizacion_objeto:
            return False
        if isinstance(sincronizacion_objeto, list):
            sincronizacion_objeto = sincronizacion_objeto[0]
        return self.actualizar_un_packing(cr, uid, sincronizacion_objeto, context=context)
        
    
    def actualizar_un_packing(self, cr, uid, sincronizacion, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
            
        info_corresponsal_obj = self.pool.get('expresso.info_corresponsal')
        sinc_obj = self.pool.get('expresso.sincronizacion_objeto_remoto')
        # Se obtiene los packing desde el WS y se convierte en objeto
        id_remoto = sincronizacion.info_objeto_remoto_id.id_remoto
        
        if not sincronizacion.info_objeto_remoto_id.corresponsal.id:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = 'No se encuentra Corresponsal definido para este registro de Packing.'
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        info_corresponsal = info_corresponsal_obj.browse(cr, uid, sincronizacion.info_objeto_remoto_id.corresponsal.id, context=context)
        
        try:
            packing_xml = cliente.service.getPacking(usuario=info_corresponsal.usuario, 
                                                     password=info_corresponsal.contrasenia,
                                                     id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
            packing = objectify.fromstring(packing_xml)
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
        if hasattr(packing, 'error'):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = packing.error
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        
        # Se procesa los packings y se marca el registro como procesado y se indica que no necesita ser reprocesado
        ret = self.process_packing(cr, uid, packing, info_corresponsal, sincronizacion.id, context=context)
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
    
            
    def actualizar_packing(self, cr, uid, context=None):
        _logger.info('Procesando Packings')
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        sinc_obj = self.pool.get('expresso.sincronizacion_objeto_remoto')
        filtros = [('procesado', '=', False), ('info_objeto_remoto_id.class', '=', 'expresso.packing')]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        
        _logger.info('Hay %s packings para procesar' % len(sinc_a_procesar))
        
        # Cantidad de packings procesados correctamente
        packings_procesados = 0
        # Cantidad de iteraciones del bucle
        iteraciones = 0
        
        for sincronizacion in sinc_obj.browse(cr, uid, sinc_a_procesar, context=context):
            # Para no bloquear tanto el trafico de internet
            time.sleep(1)
            # Si se itero un cierto numero de veces entonces se publica un mensaje en el log
            iteraciones += 1
            if iteraciones % configuracion_actualizacion.packing_frequency_print_working == 0:
                _logger.info('Procesando Packings')
            
            # Si se itero un cierto numero de veces entonces se sale del bucle
            if iteraciones > configuracion_actualizacion.packing_update_quantity:
                break
            ret = self.actualizar_un_packing(cr, uid, sincronizacion, context=context)
            if ret:
                packings_procesados += 1
        
        _logger.info('Se procesaron finalmente %s Packings', packings_procesados)
        
    
    def process_packing(self, cr, uid, packing, info_corresponsal, sincronizacion_id, context=None):
        #_logger.info('Procesando packing [id_remoto: %s]', str(packing.id))
        # sinc_obj = self.pool.get['expresso.sincronizacion_objeto_remoto']
        picking_obj = self.pool.get('expresso.packing')
        
        id_remoto = packing.id
        imprimirpeso = False
        if packing.imprimirpeso:
            imprimirpeso = packing.imprimirpeso
        
        # number_of_packages
        number_of_packages = 0
        if packing.cajas:
            number_of_packages = len(packing.cajas.caja)
        
        # fecha    
        fecha = False
        if packing.fecha and len(str(packing.fecha.text)) == 8:
            fecha = str(packing.fecha)[0:4] + '-' + str(packing.fecha)[4:6] + '-' + str(packing.fecha)[6:8]
        
        #partner_id
        partner_id = False
        partner_ids = self.get_partner_ids_from_user_login(cr, uid, info_corresponsal.usuario, context=None)
        if partner_ids:
            partner_id = partner_ids[0]
        # address_id
        address_id = False
        if partner_id:
            address_ids = self.pool.get['res.partner.address'].search(cr, uid,
                                                        [('partner_id', '=', partner_id)], context=context)
            if address_ids:
                address_id = address_ids[0]
        # Save the new values or create a new stock.tracking
        new_data = {'id_remoto': id_remoto, 'date': fecha,
                    'number_of_packages': number_of_packages,
                    'partner_id': partner_id, 'address_id': address_id,
                    'imprimirpeso': imprimirpeso}
        stored_packing_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.packing', id_remoto, context=None)
        if not stored_packing_ids:
            stored_packing_ids = [picking_obj.create(cr, uid, new_data)]
        else:
            picking_obj.write(cr, uid, stored_packing_ids, new_data)
        
        # Process the objects caja attached to the object picking
        packings = picking_obj.browse(cr, uid, stored_packing_ids, context=context)
        
        if not isinstance(packings, list):
            packings = [packings]
        
        if not packing.cajas or not packing.cajas.caja:
            return stored_packing_ids
            
        for packing_it in packings:
            for caja in packing.cajas.caja:
                self.process_caja(cr, uid, packing_it, caja, context=context)
        
        return stored_packing_ids
    
    
    def process_caja(self, cr, uid, packing, caja, context=None):
        box_obj = self.pooler.get_pool(cr.dbname).get('expresso.packing.box')
        
        id_remoto = caja.id
        denomination = caja.denomination
        peso = caja.peso
        
        # Save the new values or create a new stock.tracking
        new_values = {'name': denomination, 'id_remoto': id_remoto,
                      'weight': peso, 'packing_id': packing.id}
        
        stored_caja_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.packing.box', id_remoto, context=None)
        if not stored_caja_ids:
            stored_caja_ids = [box_obj.create(cr, uid, new_values)]
        else:
            box_obj.write(cr, uid, stored_caja_ids, new_values)
        
        # Process the objects line attached to the object caja
        cajas = box_obj.browse(cr, uid, stored_caja_ids, context=context)
        
        if not isinstance(cajas, list):
            cajas = [cajas]
        
        if not caja.detalle or not caja.detalle.linea:
            return None
        
        for caja_it in cajas:
            for linea in caja.detalle.linea:
                self.process_linea(cr, uid, caja_it, linea, context=context)
    
    def process_linea(self, cr, uid, box, linea, context=None):
        product_obj = self.pooler.get_pool(cr.dbname).get('product.product')
        packing_detail_obj = self.pooler.get_pool(cr.dbname).get('expresso.packing.detail')
        
        id_remoto = linea.id
        cantidad = linea.cantidad
        peso = linea.peso
        
        # product_id
        product_id = False
        product_ids = product_obj.search(cr, uid, [('isbn', '=', linea.isbn)], context=context)
        if product_ids:
            product_id = product_ids[0]
            if len(product_ids) > 1:
                _logger.warning('Hay más de un producto con ISBN %s. Los productos son: %s',
                                    str(linea.isbn), str([p.name for p in product_ids]))
        
        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)
            name = product.name
        else:
            name = 'Producto no encontrado (ISBN: ' + str(linea.isbn) + ')'
            
        # Save the new values or create a new stock.move
        new_values = {'name': name, 'id_remoto': id_remoto,
                      'product_id': product_id, 'product_qty': cantidad,
                      'weight': peso, 'box_id': box.id,}
        
        stored_detail_id = packing_detail_obj.search(cr, uid, [('id_remoto', '=', id_remoto)], context=context)
        
        if not stored_detail_id:
            stored_detail_id = packing_detail_obj.create(cr, uid, new_values)
        else:
            packing_detail_obj.write(cr, uid, stored_detail_id, new_values)
        
        return stored_detail_id
        

    #
    def obtener_info_objeto_remoto_si_no_presente(self, cr, uid, context=None):
        _logger.info('Obteniendo nuevos registros de Packings.')
        cliente = self.get_cliente()
        if not cliente:
            return False
        
        info_corresponsal_obj = self.pool.get('expresso.info_corresponsal')
        info_corresponsal_ids = info_corresponsal_obj.search(cr, uid, [], context=context)
        
        packing_agregados = 0
        lista_packing_agregados = []
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = info_corresponsal_obj.browse(cr, uid, info_corresponsal_id, context=context)
            try:
                packing_xml = cliente.service.listPacking(usuario=info_corresponsal.usuario, 
                                                          password=info_corresponsal.contrasenia).encode(
                                                                            "iso-8859-1").replace('&','&amp;')
                packings = objectify.fromstring(packing_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return False
                
            if hasattr(packings, 'error'):
                #_logger.info('No hay nuevos registros de Packing.')
                continue
            
            for packing_it in packings.iterchildren():
                id_remoto = packing_it.id
                
                info_objeto_obj = self.pool.get('expresso.info_objeto_remoto')
                sinc_obj = self.pool.get('expresso.sincronizacion_objeto_remoto')
                
                filtros = [('id_remoto', '=', id_remoto), ('class', '=', 'expresso.packing')]
                info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
                
                if not info_objeto_ids:
                    vals = {}
                    vals['id_remoto'] = id_remoto
                    vals['class'] = 'expresso.packing'
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
                    
                    packing_agregados += 1
                    lista_packing_agregados.append(id_remoto)
                    
                    if not isinstance(info_objeto_ids, list):
                        info_objeto_ids = [info_objeto_ids]
                    
                    for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                        if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                            vals = {}
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            vals['datetime_creation'] = now
                            vals['info_objeto_remoto_id'] = info_objeto.id
                            sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos registros de Packings para procesar', str(packing_agregados))
        _logger.info('Los registros agregados son: %s', str(lista_packing_agregados))
        return True
        
    
    def marcar_info_objeto_remoto_para_actualizar(self, cr, uid, context=None):
        '''
        Marca todos los registros de la base de datos para ser procesados.
        '''
        _logger.info('Marcando registos de Packings para reprocesar')
        
        info_objeto_obj = self.pool.get('expresso.info_objeto_remoto')
        sinc_obj = self.pool.get('expresso.sincronizacion_objeto_remoto')
        
        all_info_objeto_remoto_ids = info_objeto_obj.search(cr, uid, [('class', '=', 'expresso.packing')], context=context)
        
        registro_agregados = 0
        iteracion = 0
        for info_objeto in info_objeto_obj.browse(cr, uid, all_info_objeto_remoto_ids, context=context):
            iteracion += 1
            if iteracion % configuracion_actualizacion.frequency_registro_reprocesar == 0:
                _logger.info('Marcando registos de Packings para reprocesar')
            
            isbn = info_objeto.id_remoto
            if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                registro_agregados += 1
                vals = {}
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vals['datetime_creation'] = now
                vals['info_objeto_remoto_id'] = info_objeto.id
                sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se marcaron %s registos de Packings para reprocesar', str(registro_agregados))
        return True
        
        
        
        
        
        
        
        
        
        
