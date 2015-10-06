# -*- coding: utf-8 -*-

from openerp import models, fields


class order_add_message(models.TransientModel):
    _name = 'order.add_message'
    _description = "Add Internal Note"

    message = fields.Text('Mensaje', required=True)

    def action_add(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            return False

        for obj in self.browse(cr, uid, ids, context=context):
            order_id = context['active_id']
            values = {'message': obj.message, 'order_id': order_id}

            order = self.pool.get('sale.order').browse(
                cr, uid, order_id, context=context)
            if isinstance(uid, list):
                uid = uid[0]
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context=context)

            if self.user_in_group_with_name(user, "Expresso / Expresso"):
                values[
                    'user_email'] = order.user_corresponsal_id_expresso.user_email
            elif self.user_in_group_with_name(user, "Expresso / Corresponsales"):
                values[
                    'user_email'] = order.user_expresso_id_expresso.user_email
            else:
                values['user_email'] = False

            new_ids = self.pool.get('sale.order.message').create(
                cr, uid, values, context=context)

        return {'type': 'ir.actions.act_window_close'}

    def user_in_group_with_name(self, user, group_name):
        for group in user.groups_id:
            if group.name.lower() == group_name.lower():
                return True
        return False

