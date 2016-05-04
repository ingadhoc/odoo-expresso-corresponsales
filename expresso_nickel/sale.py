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

from osv import osv
from osv import fields
import datetime
import netsvc

from actualizador.conector_nickel import Conector_Nickel

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
        'product_warning':fields.boolean('Warning en Producto', readonly=True)
    }
    
    _defaults = {
        'product_warning': False,
    }
    
    def update_product_warning(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        if not isinstance(ids, list):
            ids = [ids]
        for order in order_obj.browse(cr, uid, ids, context=context):
            product_warning = False
            for line in order.order_line:
                if line.product_warning:
                    product_warning = True
                    break
            order_obj.write(cr, uid, order.id, {'product_warning': product_warning}, context=context)
        return True
    
sale_order()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    _columns = {
        'product_warning':fields.boolean('Warning en Producto',)
    }
    
    _defaults = {
        'product_warning': False,
    }
    
    def create(self, cr, uid, vals, context=None):
        ret = super(sale_order_line, self).create(cr, uid, vals, context=context)
        
        order_obj = self.pool.get('sale.order')
        order_id = vals.get('order_id', False)
        if order_id:
            order_obj.update_product_warning(cr, uid, order_id, context=context)
        return ret
    
    def  write(self, cr, uid, ids, vals, context=None):
        ret = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        
        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        order_id = vals.get('order_id', False)
        if order_id:
            order_obj.update_product_warning(cr, uid, order_id, context=context)
        else:
            if not isinstance(ids, list):
                ids = [ids]
            for line in line_obj.browse(cr, uid, ids, context=context):
                order_obj.update_product_warning(cr, uid, line.order_id.id, context=context)
        return ret
        
    
    def product_id_change_inherited(self, cr, uid, ids, pricelist, product_id, partner_id=False, product_uom_qty=1, context=None):
        result = super(sale_order_line, self).product_id_change_inherited(cr, uid, ids, pricelist, product_id, 
                                                        partner_id=partner_id, product_uom_qty=product_uom_qty, context=context)
        if not product_id:
            return result
        
        warning = self.warning_stock_productos(cr, uid, ids, product_id, product_uom_qty, context=context)
        value = result.get('value', {})
        if warning:
            value['product_warning'] = True
        else:
            value['product_warning'] = False
        return {'value': value, 'warning': warning}
    
    def warning_stock_productos(self, cr, uid, ids, product_id, product_uom_qty, context=None):
        conector_nickel = Conector_Nickel()
        stock = conector_nickel.consultar_stock(cr, uid, product_id, context=context)
        warning = {}
        if not stock:
            product_obj = self.pool.get('product.product')
            product = product_obj.browse(cr, uid, product_id, context=context)
            if not product.situacion_id or product.situacion_id.denominacion in ['AGOTADO', 'DESCATALOGADO', 'NO DISPONIBLE']:
                warning['title'] = u'Estado problematico'
                if product.situacion_id:
                    warning['message'] = u'El Titulo elegido se encuentra en estado "%s"' % product.situacion_id.denominacion
                else:
                    warning['message'] = u'El Titulo elegido no se encuentra disponible'
        else:
            stock = int(stock)
            if stock < product_uom_qty:
                warning['title'] = u'Stock no disponible'
                warning['message'] = u'No se dispone de stock. Solo %s unidades están disponibles.' % str(stock)
        
        return warning
        
sale_order_line()









