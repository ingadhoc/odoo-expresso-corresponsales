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
import sys
import traceback

import logging
import pooler
from osv import osv, fields
from suds.client import Client
from lxml import objectify # http://lxml.de/objectify.html

from actualizador_generico import Actualizador_Generico
import configuracion_actualizacion

_logger = logging.getLogger(__name__)

class Actualizador_Pedidos(Actualizador_Generico):
    
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_pedidos)
    
    def check_order_lines(self, cr, uid, ids, context=None):
        order_obj = self.pooler.get_pool(cr.dbname).get('sale.order')
        
        for order in order_obj.browse(cr, uid, ids, context=context):
            for linea in order.order_line:
                cantidad = linea.product_uom_qty
                if not cantidad or cantidad <= 0:
                    titulo = u'Cantidad menor o igual a 0'
                    mensaje = u'Existe una lina de pedido cuya cantidad es menor o igual a 0. Por favor corriga este posible error modificando la cantidad en la linea o borrela antes de cerar el pedido.'
                    if linea.product_id and linea.product_id.isbn:
                        mensaje += u'\n\nLa lina hace referencia al isbn %s' % linea.product_id.isbn
                    raise osv.except_osv(titulo, mensaje)
                    
                
            
            
    def crear_pedido_remoto(self, cr, uid, ids, context=None):
        self.check_order_lines(cr, uid, ids, context=context)
        
        cliente = self.get_cliente()
        if not cliente:
            return None
        if not isinstance(ids, list):
            ids = [ids]
        
        order_obj = self.pooler.get_pool(cr.dbname).get('sale.order')
        order_line_obj = self.pooler.get_pool(cr.dbname).get('sale.order.line')
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        
        for order in order_obj.browse(cr, uid, ids, context=context):
            if not order.partner_id.info_corresponsal_id:
                titulo = u'Imposible procesar'
                mensaje = u'No se tiene información del cliente %s sobre el usuario remoto para actualizar el pedido en el sistema.'
                mensaje = mensaje % order.partner_id.name
                raise osv.except_osv(titulo, mensaje)
            info_corresponsal = order.partner_id.info_corresponsal_id
            
            usuario = info_corresponsal.usuario
            contrasenia = info_corresponsal.contrasenia
            fecha = str(order.date_order)
            forma_envio = ''
            if order.forma_envio_id_corresponsales:
                forma_envio = order.forma_envio_id_corresponsales.denominacion
            observaciones = ''
            if order.note:
                observaciones = order.note
            
            usuario = usuario.encode('utf-8')
            contrasenia = contrasenia.encode('utf-8')
            forma_envio = forma_envio.encode('utf-8')
            observaciones = observaciones.encode('utf-8')
            
            pedido_xml = '<pedido><usuario>%s</usuario><password>%s</password><fecha>%s</fecha><formaenvio>%s</formaenvio><observaciones>%s</observaciones></pedido>'
            pedido_xml = pedido_xml % (usuario, contrasenia, fecha, forma_envio, observaciones)
            pedido_xml = pedido_xml.decode('iso-8859-1')
            ret_xml = cliente.service.setPedido(pedido_xml)
            ret = objectify.fromstring(ret_xml)
            id_remoto = ret.id.text
            order_obj.write(cr, uid, order.id, {'id_remoto': id_remoto}, context=context)
            
            for linea in order.order_line:
                pedcliente = id_remoto
                isbn = ''
                if linea.product_id and linea.product_id.isbn:
                    isbn = linea.product_id.isbn
                concepto = ''
                editorial = ''
                if linea.product_id and linea.product_id.editorial:
                    editorial = linea.product_id.editorial
                cantidad = linea.product_uom_qty
                observaciones = ''
                if linea.notes:
                    observaciones = linea.notes
                
                isbn = isbn.encode('utf-8')
                editorial = editorial.encode('utf-8')
                observaciones = observaciones.encode('utf-8')
                
                detalle_xml = '<pedido><usuario>%s</usuario><password>%s</password><pedcliente>%s</pedcliente><isbn>%s</isbn><editorial>%s</editorial><cantidad>%s</cantidad><observaciones>%s</observaciones></pedido>'
                detalle_xml = detalle_xml % (usuario, contrasenia, pedcliente, isbn, editorial, cantidad, observaciones)
                detalle_xml = detalle_xml.decode('iso-8859-1')
                ret_xml = cliente.service.setPedidoD(detalle_xml)
                ret = objectify.fromstring(ret_xml)
                id_remoto_detalle = ret.id.text
                order_line_obj.write(cr, uid, linea.id, {'id_remoto': id_remoto_detalle}, context=context)
    
    '''
    def actualizar_pedidos(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        from_date = self.get_string_date(sync_info)
        
        info_corresponsal_ids = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal').search(cr, uid, [], context=context)
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal').browse(cr, uid,
                                                                                    info_corresponsal_id, context=context)
            _logger.info('Procesando pedidos de %s', info_corresponsal.corresponsal)
            
            try:
                if from_date:
                    pedidos_xml = cliente.service.listPedidos(usuario=info_corresponsal.usuario, 
                                                              password=info_corresponsal.contrasenia,
                                                              updated=from_date).encode("iso-8859-1").replace('&','&amp;')
                else:
                    pedidos_xml = cliente.service.listPedidos(usuario=info_corresponsal.usuario, 
                                                      password=info_corresponsal.contrasenia).encode("iso-8859-1").replace('&','&amp;')
                pedidos = objectify.fromstring(pedidos_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return None
            
            if hasattr(pedidos, 'error'):
                _logger.info('No hay pedidos de %s para procesar.', info_corresponsal.corresponsal)
                #_logger.error('Error procesando los pedidos de %s. Error: %s', info_corresponsal.corresponsal, pedidos.error)
                continue
            
            #TODO: Remover este contador
            #count = 0
            for pedido_it in pedidos.iterchildren():
                id_remoto = pedido_it.id
                
                try:
                    pedido_xml = cliente.service.getPedido(usuario=info_corresponsal.usuario, 
                                                           password=info_corresponsal.contrasenia,
                                                           id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
                    pedido = objectify.fromstring(pedido_xml)
                except:
                    e = traceback.format_exc()
                    _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                    return None
                
                if hasattr(pedido, 'error'):
                    _logger.error('Error procesando el pedidos [id_remoto: %s] de %s. Error: %s',
                                      id_remoto, info_corresponsal.corresponsal, pedido.error)
                    continue
                
                self.process_pedido(cr, uid, pedido, info_corresponsal, context=context)
                
                #count += 1
                #if count >= 10:
                #    break
    
    
    def process_pedido(self, cr, uid, pedido, info_corresponsal, context=None):
        _logger.info('Procesando pedido [id_remoto: %s]', str(pedido.id))
        
        id_remoto = pedido.id
        notes = False
        if pedido.observaciones:
            notes = pedido.observaciones.text
        
        # date_order
        date_order = False
        if pedido.fecha and len(str(pedido.fecha.text)) == 8:
            date_order = str(pedido.fecha)[0:4] + '-' + str(pedido.fecha)[4:6] + '-' + str(pedido.fecha)[6:8]
        
        # forma_envio_id
        forma_envio_id = False
        forma_envio_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.forma_envio', pedido.IDformaenvio, context=context)
        if forma_envio_ids:
            forma_envio_id = forma_envio_ids[0]
        
        # partner_id
        partner_id = False
        partner_ids = self.get_partner_ids_from_user_login(cr, uid, info_corresponsal.usuario, context=None)
        if partner_ids:
            partner_id = partner_ids[0]
        
        if not partner_id:
            _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro el res.partner %s asociado al usuario %s.',
                              str(id_remoto), info_corresponsal.corresponsal, info_corresponsal.usuario)
            return None
            
        # pricelist_id
        pricelist_id = False
        
        company_id = self.pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [], context=context)
        if isinstance(company_id, list):
            company_id = company_id[0]
        if company_id:
            company = self.pooler.get_pool(cr.dbname).get('res.company').browse(cr, uid, company_id, context=context)
            pricelist_id = company.partner_id.property_product_pricelist.id
        
        if not pricelist_id:
            any_pricelist_id = self.pooler.get_pool(cr.dbname).get('product.pricelist').search(cr, uid, [], context=context)
            if isinstance(any_pricelist_id, list):
                any_pricelist_id = any_pricelist_id[0]
            
            if any_pricelist_id:
                pricelist_id = any_pricelist_id
            else:
                _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ninguna lista de precios ' +
                                  '(product.pricelist) para asociarle.', str(id_remoto))
                return None
            
        
        
        # partner_order_id, partner_invoice_id, partner_shipping_id
        partner_order_id = False
        partner = self.pooler.get_pool(cr.dbname).get('res.partner').browse(cr, uid, partner_id, context=context)
        partner_order_id = partner.address[0].id
        partner_invoice_id = partner_order_id
        partner_shipping_id = partner_order_id
        
        if not partner_order_id:
            _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ningun partner_order_id ' +
                                  'para asociarle.', str(id_remoto))
            return None
        
        # Persist sale.order
        new_data = {'id_remoto': id_remoto, 'notes': notes, 'date_order': date_order, 'forma_envio_id': forma_envio_id,
                    'partner_id': partner_id, 'pricelist_id': pricelist_id, 'partner_order_id': partner_order_id,
                    'partner_invoice_id': partner_invoice_id, 'partner_shipping_id': partner_shipping_id}
        
        stored_order_ids = self.get_ids_from_id_remoto(cr, uid, 'sale.order', id_remoto, context=context)
        if not stored_order_ids:
            stored_order_ids = [self.pooler.get_pool(cr.dbname).get('sale.order').create(cr, uid, new_data)]
        else:
            self.pooler.get_pool(cr.dbname).get('sale.order').write(cr, uid, stored_order_ids, new_data)
        
        if not hasattr(pedido, 'detalle') or not hasattr(pedido.detalle, 'linea'):
            return None
        
        for stored_order_id in stored_order_ids:
            for linea in pedido.detalle.linea:
                self.process_linea(cr, uid, stored_order_id, linea, context=context)
    
    
    
    
    
    
    
    def process_linea(self, cr, uid, stored_order_id, linea, context=None):
        id_remoto = linea.id
        notes = linea.observaciones
        product_uom_qty = linea.cantidad
        
        # product_id
        product_id = False
        product_ids = self.pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [('isbn', '=', linea.isbn)], context=context)
        if product_ids:
            product_id = product_ids[0]
            if len(product_ids) > 1:
                _logger.warning('Hay más de un producto con ISBN %s. Los productos son: %s',
                                    str(linea.isbn), str([p.name for p in product_ids]))
        #TODO: remover esto
        if not product_id:
            product_ids = self.pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [], context=context)
            if product_ids:
                product_id = product_ids[0]
        
        # name
        name = False
        if linea.concepto:
            name = linea.concepto
        else:
            if product_id:
                product = self.pooler.get_pool(cr.dbname).get('product.product').browse(cr, uid, product_id, context=context)
                name = product.name
            else:
                name = 'Producto no especificado'
        
        # uom_id
        uom_ids = self.pooler.get_pool(cr.dbname).get('product.uom').search(cr, uid, [('name', '=', 'PCE')], context=context)
        if not uom_ids:
            uom_id = self.pooler.get_pool(cr.dbname).get('product.uom').search(cr, uid, [], context=context)[0]
        else:
            uom_id = uom_ids[0]
            
        # Save the new values or create a new stock.move
        new_values = {'id_remoto': id_remoto, 'notes': notes, 'product_uom_qty': product_uom_qty, 'product_id': product_id,
                      'name': name, 'order_id': stored_order_id, 'product_uom': uom_id}
        
        stored_line_ids = self.get_ids_from_id_remoto(cr, uid, 'sale.order.line', id_remoto, context=context)
        if not stored_line_ids:
            stored_line_ids = [self.pooler.get_pool(cr.dbname).get('sale.order.line').create(cr, uid, new_values)]
        else:
            self.pooler.get_pool(cr.dbname).get('sale.order.line').write(cr, uid, stored_line_ids, new_values)
        
        return stored_line_ids
    '''
