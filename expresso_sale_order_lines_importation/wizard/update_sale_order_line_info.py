# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-Today OpenERP SA (<http://www.openerp.com>).
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
from tools.translate import _

class update_sale_order_line_info_line(osv.osv_memory):
    _name = 'update_sale_order_line_info_line'
    _description = 'Update Order Line Information from Line'

    def update_information(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        if active_ids:
            order_line_obj = self.pool.get('sale.order.line')
            order_line_obj.update_order_line_info(cr, uid, active_ids, context=context)
        return { 'type': 'ir.actions.act_window_close'}
        
update_sale_order_line_info_line()


class update_sale_order_line_info_order(osv.osv_memory):
    _name = 'update_sale_order_line_info_order'
    _description = 'Update Order Line Information from Order'

    def update_information(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        if active_ids:
            order_obj = self.pool.get('sale.order')
            order_line_obj = self.pool.get('sale.order.line')
            
            order_line_ids = []
            for order in order_obj.browse(cr, uid, active_ids, context=context):
                for line in order.order_line:
                    order_line_ids.append(line.id)
            order_line_obj.update_order_line_info(cr, uid, order_line_ids, context=context)
        return { 'type': 'ir.actions.act_window_close'}
        
update_sale_order_line_info_order()

