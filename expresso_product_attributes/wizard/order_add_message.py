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

from osv import fields, osv
from mail.mail_message import truncate_text

class order_add_message(osv.osv_memory):
    _name = 'order.add_message'
    _description = "Add Internal Note"

    _columns = {
        'message': fields.text('Mensaje', required=True),
    }

    def action_add(self, cr, uid, ids, context=None):
        if 'active_id' not in context:
            return False
        
        for obj in self.browse(cr, uid, ids, context=context):
            order_id = context['active_id']
            values = {'message': obj.message, 'order_id': order_id}
            
            order = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
            if isinstance(uid, list):
                uid = uid[0]
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            
            if self.user_in_group_with_name(user, "Expresso / Expresso"):
                values['user_email'] = order.user_corresponsal_id_expresso.user_email
            elif self.user_in_group_with_name(user, "Expresso / Corresponsales"):
                values['user_email'] = order.user_expresso_id_expresso.user_email
            else:
                values['user_email'] = False
            
            new_ids = self.pool.get('sale.order.message').create(cr, uid, values, context=context)
            
        return { 'type': 'ir.actions.act_window_close'}
    
    def user_in_group_with_name(self, user, group_name):
        for group in user.groups_id:
            if group.name.lower() == group_name.lower():
                return True
        return False
order_add_message()


