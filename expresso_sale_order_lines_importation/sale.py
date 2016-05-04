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

import time
import netsvc
from osv import osv, fields

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    def update_order_line_info(self, cr, uid, ids, context=None):
        order_line_obj = self.pool.get('sale.order.line')
        for line in order_line_obj.browse(cr, uid, ids, context=context):
            line_vals = order_line_obj.product_id_change(cr, uid, line.id, line.order_id.pricelist_id.id,
                                line.product_id.id, qty=line.product_uom_qty, uom=line.product_uom.id,
                                partner_id=line.order_id.partner_id.id, context=context)['value']
            order_line_obj.write(cr, uid, line.id, line_vals, context=context)
        return True

sale_order_line()

