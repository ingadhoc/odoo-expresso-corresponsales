# -*- coding: utf-8 -*-


from openerp import pooler
from openerp import models, fields, _
from openerp.exceptions import Warning


class expresso_repedir_pendiente_pedido_existente(models.TransientModel):

    _name = "expresso.repedir_pendiente_pedido_existente"
    _description = "Repedir Pendiente en pedido_existente."

    order_id = fields.Many2one('sale.order', 'Order', required=True)

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
            raise Warning(_('Pedido en estado incorrecto',
                            'No se le pueden agregar titulos a los Pedidos en estado %s.' % (order.state_expresso)))

        pendiente_obj = pooler.get_pool(cr.dbname).get(
            'product.producto_pendiente')
        pendiente_obj.agregar_pendiente_a_pedido(
            cr, uid, order.id, pendiente_id, context=context)
        return {'type': 'ir.actions.act_window_close'}
