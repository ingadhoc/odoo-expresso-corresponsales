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

import logging
from osv import osv, fields
import decimal_precision as dp
import netsvc

_logger = logging.getLogger(__name__)

class product_product(osv.osv):
    '''
    Titulo de Expresso Bibliografico
    '''
    _name = 'product.product'
    _inherit = 'product.product'
    _description = u'Título'
    
    _columns = {
        'autor':fields.char('Autor', size=64, required=False, readonly=False),
        'isbn':fields.char('ISBN', size=30, required=False, readonly=False),
        
        'editorial':fields.char('Editorial', size=64, required=False, readonly=False),
        'idioma_id':fields.many2one('expresso.idioma', 'Idioma', required=False),
        'encuadernacion_id':fields.many2one('expresso.encuadernacion', 'Encuadernacion', required=False),
        'coleccion_id':fields.many2one('expresso.coleccion', 'Coleccion', required=False),
        'volumen': fields.char('Volumen', size=10, required=False, readonly=False),
        'numero_paginas': fields.integer(u'Número de Páginas'),
        'anio_edicion': fields.integer(u'Año de Edición'),
        'numero_edicion': fields.char(u'Número de Edición', size=10, required=False, readonly=False),
        'situacion_id':fields.many2one('expresso.situacion', 'Situacion', required=False),
        'materia_id':fields.many2one('expresso.materia', 'Materia', required=False),
        'proyecto_id':fields.many2one('expresso.proyecto', 'Proyecto', required=False),
        
        'sinopsis': fields.text('Sinopsis'),
        'recomendado':fields.boolean('Recomendado', required=False),
        'edad_recomendada_min': fields.integer(u'Edad Mínima Recomendada'),
        'edad_recomendada_max': fields.integer(u'Edad Máxima Recomendada'),
        'imagen': fields.binary('Imagen', filters=None),
        'precio_dolares': fields.float('Precio en Dolares'),
        
        'valor_ids':fields.many2many('expresso.valor','expresso_product_valor_rel', 'product_id', 'valor_id', 'Valores', required=False),
        'seleccion_ids':fields.many2many('expresso.seleccion','expresso_product_seleccion_rel', 'product_id', 'seleccion_id', 'Selecciones', required=False),
        'ciclo_id':fields.many2one('expresso.ciclo', 'Ciclo', required=False),
        'curso_id':fields.many2one('expresso.curso', 'Curso', required=False),
        'tipo_id':fields.many2one('expresso.tipo', 'Tipo', required=False),
        'publico_id':fields.many2one('expresso.publico', u'Público Objetivo', required=False),
        'soporte':fields.char('Soporte', size=50, required=False, readonly=False),
        'alto': fields.integer('Alto'),
        'ancho': fields.integer('Ancho'),
        'espesor': fields.integer('Espesor'),
        'peso': fields.integer('Peso'),
        # Id que usan las bibliotecas para identificar las temáticas de los libros
        'materia_cdu': fields.char('Materia CDU', size=64, required=False, readonly=False),
        'caratula' : fields.char('Caratula', size=300, required=False, readonly=False),
    }
    
    def onchange_product_materia(self, cr, uid, ids, materia_id):
        v = {}
        if materia_id:
            materia = self.pool.get('expresso.materia').browse(cr, uid, materia_id, context=context)
            v['proyecto_id'] = materia.proyecto_id.id
        return {'value': v}
        
product_product()

# Producto Pendiente
class product_producto_pendiente(osv.osv):
    _name = 'product.producto_pendiente'
    _description = u'Título Pendiente'
    _order = 'create_date desc'
    
    _columns = {
        'name': fields.char('Descripcion', size=256, required=True),
        'product_id':fields.many2one('product.product', u'Título', required=False),
        'cantidad': fields.integer('Cantidad', required=False),
        'partner_id':fields.many2one('res.partner', 'Cliente', required=True),
        'order_id':fields.many2one('sale.order', 'Pedido', required=True),
        'situacion_id':fields.many2one('expresso.situacion', 'Situacion', required=False),
        'notas': fields.text('Notas', required=False),
        'state': fields.selection([
                            ('activo','Activo'),
                            ('cancelado','Cancelado'),
                            ('repedido','Repedido')], 'Estado', readonly=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute=dp.get_precision('Sale Price')),
    }
    
    def pendiente_a_nuevo_pedido(self, cr, uid, pendiente_id, context=None):
        '''
        Crea un nuevo pedido y llama a agregar_pendiente_a_pedido para agregar el titulo pendiente al nuevo pedido creado.
        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if isinstance(user, list):
            user = user[0]
        
        if not user.partner_id:
            raise osv.except_osv('No tiene Cliente asociado',
                                 'Usted no tiene ningún Cliente asociado y por lo tanto no se puede realizar esta acción' +
                                 ' por favor asignese un Cliente en el panel de administración de usuarios.')
        
        partner_id = user.partner_id.id
        
        if isinstance(pendiente_id, list):
            pendiente_id = pendiente_id[0]
        
        # pricelist_id
        pricelist_id = False
        
        company_id = self.pool.get('res.company').search(cr, uid, [], context=context)
        if isinstance(company_id, list):
            company_id = company_id[0]
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            pricelist_id = company.partner_id.property_product_pricelist.id
        
        if not pricelist_id:
            any_pricelist_id = self.pool.get('product.pricelist').search(cr, uid, [], context=context)
            if isinstance(any_pricelist_id, list):
                any_pricelist_id = any_pricelist_id[0]
            
            if any_pricelist_id:
                pricelist_id = any_pricelist_id
            else:
                _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ninguna lista de precios ' +
                                  '(product.pricelist) para asociarle.', str(id_remoto))
                return
        
        # partner_order_id, partner_invoice_id, partner_shipping_id
        partner_order_id = False
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        partner_order_id = partner.address[0].id
        partner_invoice_id = partner_order_id
        partner_shipping_id = partner_order_id
        
        if not partner_order_id:
            _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ningun partner_order_id ' +
                                  'para asociarle.', str(id_remoto))
            return
        
        new_data = {'partner_id': partner_id, 'pricelist_id': pricelist_id, 'partner_order_id': partner_order_id,
                    'partner_invoice_id': partner_invoice_id, 'partner_shipping_id': partner_shipping_id}
        order_id = self.pool.get('sale.order').create(cr, uid, new_data)
        
        return self.agregar_pendiente_a_pedido(cr, uid, order_id, pendiente_id, context=context)
    
    
    def agregar_pendiente_a_pedido(self, cr, uid, order_id, pendiente_id, context=None):
        '''
        Recibe el id del pedido (order_id) y el id del titulo pendiente (pendiente_id), agrega al pedido el titulo pendiente
        y transiciona el workflow del titulo pendiente a repedido.
        '''
        pendiente_obj = self.pool.get('product.producto_pendiente')
        pendiente = pendiente_obj.browse(cr, uid, pendiente_id, context=context)
        # name, notes
        product_id = False
        if pendiente.product_id:
            product_id = pendiente.product_id.id
        name = pendiente.name
        notes = False
        if pendiente.notas:
            notes = 'Notas del pedido pendiente.\n' + pendiente.notas
        # uom_id
        uom_ids = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'PCE')], context=context)
        if not uom_ids:
            uom_id = self.pool.get('product.uom').search(cr, uid, [], context=context)[0]
        else:
            uom_id = uom_ids[0]
        
        price_unit = pendiente.price_unit
        
        new_values = {'product_id': product_id, 'notes': notes, 'product_uom_qty': pendiente.cantidad,
                      'name': name, 'order_id': order_id, 'product_uom': uom_id, 'price_unit': price_unit}
        new_ids = self.pool.get('sale.order.line').create(cr, uid, new_values)
        
        # Transicionamos el Producto Pendiente de Activo a Repedido en el workflow.
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'product.producto_pendiente', pendiente_id, 'producto_pendiente_activo_2_repedido', cr)
        return new_ids
        
    def pendiente_state_activo(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'activo'})
        
    def pendiente_state_cancelado(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'cancelado'})
    
    def pendiente_state_repedido(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'repedido'})
        
    
product_producto_pendiente()






