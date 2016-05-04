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

class expresso_repedir_pendiente_pedido_existente(osv.osv_memory):

    _name = "expresso.repedir_pendiente_pedido_existente"
    _description = "Repedir Pendiente en pedido_existente."
    
    _columns = {
        'order_id':fields.many2one('sale.order', 'Order', required=True),
    }
    
    def repedir_pendiente(self, cr, uid, ids, context=None):
        '''
        Llama a agregar_pendiente_a_pedido de la clase product.producto_pendiente para agregar el titulo pendiente
        al pedido seleccionado.
        '''
        if 'active_id' not in context:
            return False
            
        order = self.browse(cr, uid, ids)[0].order_id
        pendiente_id = context['active_id']
        
        estados_permitidos = ['borrador', 'pendiente_c']
        if order.state_expresso not in estados_permitidos:
            raise osv.except_osv('Pedido en estado incorrecto',
                                 'No se le pueden agregar titulos a los Pedidos en estado %s.' % order.state_expresso)
        
        pendiente_obj = pooler.get_pool(cr.dbname).get('product.producto_pendiente')
        pendiente_obj.agregar_pendiente_a_pedido(cr, uid, order.id, pendiente_id, context=context)
        return { 'type': 'ir.actions.act_window_close'}
    
    
expresso_repedir_pendiente_pedido_existente()
        
    
    
    
    
    




