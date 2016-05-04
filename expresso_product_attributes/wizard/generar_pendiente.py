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

import pooler
from osv import osv, fields
import netsvc

class expresso_generador_productos_pendientes(osv.osv_memory):

    _name = "expresso.generador_productos_pendientes"
    _description = "Generar Títulos Pendientes."
    
    _columns = {
        'cantidad_disponible':fields.integer('Cantidad Disponible', required=False),
        'situacion_id':fields.many2one('expresso.situacion', 'Situacion', required=True),
        'notas': fields.text('Notas', required=False),
    }
    
    def controlar_generacion_de_pendiente(self, cr, uid, ids, linea, context=None):
        titulo = 'No puede modificar el pedido'
        mensaje = 'No se pueden eliminar Titulos del pedido cuando este esta en el estado %s.'
        if linea.order_id.state_expresso == 'despachado':
            raise osv.except_osv(titulo, mensaje % 'Despachado')
        if linea.order_id.state_expresso == 'recibido':
            raise osv.except_osv(titulo, mensaje % 'Recibido')
        
    
    def linea_parcial_a_pendientes(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            return False
        
        cantidad_disponible = self.browse(cr, uid, ids)[0].cantidad_disponible
        if not cantidad_disponible:
            return { 'type': 'ir.actions.act_window_close'}
        
        context['desde_wizard_pendiente'] = True
        
        linea = self.pool.get('sale.order.line').browse(cr, uid, context['active_id'], context=context)
        
        self.controlar_generacion_de_pendiente(cr, uid, ids, linea, context=context)
        
        if cantidad_disponible > linea.product_uom_qty:
            raise osv.except_osv('Cantidad disponible muy grande',
                                 'La cantidad disponible no peude ser mayor a la cantidad pedida.')
        elif cantidad_disponible < 0:
            raise osv.except_osv('Cantidad disponible negativa',
                                 'La cantidad disponible no peude ser negativa.')
        
        name = linea.name
        # product_id
        product_id = False
        if linea.product_id:
            product_id = linea.product_id.id
        
        # price_unit
        price_unit = linea.price_unit
        
        # cantidad
        cantidad = linea.product_uom_qty - cantidad_disponible
        
        # partner_id
        partner_id = linea.order_id.partner_id.id
        
        #order_id
        order_id = linea.order_id.id
        # situacion_id, notas
        situacion_id = self.browse(cr, uid, ids)[0].situacion_id.id
        notas = self.browse(cr, uid, ids)[0].notas
        
        values = {'name': name, 'product_id': product_id, 'cantidad': cantidad, 'partner_id': partner_id,
                  'order_id': order_id, 'situacion_id': situacion_id, 'notas': notas, 'price_unit': price_unit}
        new_ids = self.pool.get('product.producto_pendiente').create(cr, uid, values, context=context)
        
        self.pool.get('sale.order.line').write(cr, uid, [linea.id], {'product_uom_qty': cantidad_disponible}, context=context)
        return { 'type': 'ir.actions.act_window_close'}
    
    
    
    
    
    def linea_entera_a_pendientes(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            return False
        
        context['desde_wizard_pendiente'] = True
        
        linea = self.pool.get('sale.order.line').browse(cr, uid, context['active_id'], context=context)
        self.controlar_generacion_de_pendiente(cr, uid, ids, linea, context=context)
        
        name = linea.name
        # product_id
        product_id = False
        if linea.product_id:
            product_id = linea.product_id.id
        
        # price_unit
        price_unit = linea.price_unit
        
        # cantidad
        cantidad = linea.product_uom_qty
        
        # partner_id
        partner_id = linea.order_id.partner_id.id
        
        #order_id
        order_id = linea.order_id.id
        # situacion_id, notas
        situacion_id = self.browse(cr, uid, ids)[0].situacion_id.id
        notas = self.browse(cr, uid, ids)[0].notas
        
        values = {'name': name, 'product_id': product_id, 'cantidad': cantidad, 'partner_id': partner_id,
                  'order_id': order_id, 'situacion_id': situacion_id, 'notas': notas, 'price_unit': price_unit}
        new_ids = self.pool.get('product.producto_pendiente').create(cr, uid, values, context=context)
        
        self.pool.get('sale.order').write(cr, uid, [order_id], {'order_line': [(2, linea.id)]}, context=context)
        #self.pool.get('sale.order.line').unlink(cr, uid, [linea.id], context=context)
        return { 'type': 'ir.actions.act_window_close'}
    
expresso_generador_productos_pendientes()
        
    
    
    
    
    




