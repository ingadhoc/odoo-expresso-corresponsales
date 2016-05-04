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

import netsvc

from osv import fields, osv
import pooler

class pedir_multi_titulos(osv.osv_memory):
    _name = 'pedir_multi_titulos'
    _description = 'Pedir Multiples Titulos'
    
    _columns = {
        'linea_ids': fields.many2many('pedido_multi_titulo.linea', string='Títulos'),
        'order_id':fields.many2one('sale.order', 'Pedido', required=False),
    }
    
    def view_init(self, cr, uid, fields, context=None):
        '''
        This function checks for precondition before wizard executes
        '''
        #if context is None:
        #    context = {}
        #product_obj = self.pool.get('product.product')
        #for product in product_obj.browse(cr, uid, context.get('active_ids', []), context=context):
        #    if lead.state in ['done', 'cancel']:
        #        raise osv.except_osv(_("Warning !"), _("Closed/Cancelled Leads can not be converted into Opportunity"))
        return {'product_ids': context.get('active_ids', [])}
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(pedir_multi_titulos, self).default_get(cr, uid, fields, context=context)        
        
        linea_ids = []
        for product_id in context.get('active_ids', []):
            vals = {'product_id': product_id, 'cantidad': 1}
            linea_id = pooler.get_pool(cr.dbname).get('pedido_multi_titulo.linea').create(cr, uid, vals, context=context)
            linea_ids.append(linea_id)
        res.update({'linea_ids': linea_ids})
        return res
    
    
    def a_pedido_existente(self, cr, uid, ids, context=None):
        '''
        Controla que se haya seleccionado un pedido en el campo order_id. Agrega al pedido las lineas especificadas en
        el campo linea_ids. Pasa a la proxima pantalla del wizard.
        '''
        order = self.browse(cr, uid, ids)[0].order_id
        if not order:
            raise osv.except_osv('Pedido no especificado',
                                 'Se debe especificar un pedido existente para anexar los nuevos titulos.')
        
        for linea in self.browse(cr, uid, ids)[0].linea_ids:
            self.agregar_titulo_a_pedido(cr, uid, order.id, linea, context=context)
        
        context['order_id'] = order.id
        view_res = self.pool.get('ir.ui.view').search(cr, uid,
                    [('name','=','pedir_multi_titulos.3'),('model','=','pedir_multi_titulos')])
        result = {'view_type' : 'form',
                  'view_mode' : 'form',
                  'view_id' : view_res,
                  'res_model' : 'pedir_multi_titulos',
                  'type' : 'ir.actions.act_window',
                  'target' : 'new',
                  'context' : context,}
        
        return result
    
    
    def a_nuevo_pedido(self, cr, uid, ids, context=None):
        '''
        Primero se crea una nueva orden y luego se itera en todas las lineas del wizard para poblar el pedido con las
        lineas del pedido.
        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if isinstance(user, list):
            user = user[0]
        
        if not user.partner_id:
            raise osv.except_osv('No tiene Cliente asociado',
                                 'Usted no tiene ningún Cliente asociado y por lo tanto no se puede realizar esta acción' +
                                 ' por favor asignese un Cliente en el panel de administración de usuarios.')
        
        partner_id = user.partner_id.id
        
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
        
        new_ids =[]
        for linea in self.browse(cr, uid, ids)[0].linea_ids:
            self.agregar_titulo_a_pedido(cr, uid, order_id, linea, context=context)
            
        context['order_id'] = order_id
        view_res = self.pool.get('ir.ui.view').search(cr, uid,
                    [('name','=','pedir_multi_titulos.2'),('model','=','pedir_multi_titulos')])
        result = {'view_type' : 'form',
                  'view_mode' : 'form',
                  'view_id' : view_res,
                  'res_model' : 'pedir_multi_titulos',
                  'type' : 'ir.actions.act_window',
                  'target' : 'new',
                  'context' : context,}
        return result
        
    
    def agregar_titulo_a_pedido(self, cr, uid, order_id, linea, context=None):
        '''
        Recibe el id del pedido (order_id) y la linea, del tipo pedido_multi_titulo.linea. Agrega la linea
        al pedido.
        '''
        #product = product_obj.browse(cr, uid, linea.product_id.id, context=context)
        product = linea.product_id
        # name_get retorna una lista con pares cuyo primer valor es el id y el segundo el nombre, por eso el acceso [0][1]
        product_obj = self.pool.get('product.product')
        name = product_obj.name_get(cr, uid, [product.id], context=context)[0][1]
        
        product_uom_qty = linea.cantidad
        
        uom_ids = pooler.get_pool(cr.dbname).get('product.uom').search(cr, uid, [('name', '=', 'PCE')], context=context)
        if not uom_ids:
            uom_id = pooler.get_pool(cr.dbname).get('product.uom').search(cr, uid, [], context=context)[0]
        else:
            uom_id = uom_ids[0]
        
        price_unit = product.list_price
        
        new_values = {'product_id': product.id, 'product_uom_qty': product_uom_qty, 'name': name,
                      'product_uom': uom_id, 'price_unit': price_unit}
        new_values_order = {'order_line': [(0, 0, new_values)] }
        new_ids = pooler.get_pool(cr.dbname).get('sale.order').write(cr, uid, order_id, new_values_order)
        
        return new_ids
    
    
    def ir_al_pedido(self, cr, uid, ids, context=None):
        '''
        Redirecciona al cliente hacia la vista del pedido cuyo id esta en el context (context['order_id'])
        '''
        result = {'view_type' : 'form',
                  'view_mode' : 'form',
                  'res_model' : 'sale.order',
                  'type' : 'ir.actions.act_window',
                  'context' : context,}
        
        if 'order_id' in context:
            result['res_id'] = context['order_id']
        
        return result
    
pedir_multi_titulos()



class pedido_multi_titulo_linea(osv.osv):
    _name = 'pedido_multi_titulo.linea'
    _description = 'Linea Pedido Multiple de Títulos'
    _rec_name = 'product_id'
	
    _columns = {
        'product_id': fields.many2one('product.product', 'Producto', required=True),
        'cantidad': fields.integer('Cantidad', required=True),
    }
    
pedido_multi_titulo_linea()









