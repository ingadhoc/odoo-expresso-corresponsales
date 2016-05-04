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

import time
import decimal_precision as dp

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = 'account.invoice'
    
    def _proxima_fecha_vencimiento(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            proxima_nickel_factura = False
            
            for nickel_factura in invoice.nickel_factura_ids:
                if not nickel_factura.pagado:
                    if not proxima_nickel_factura:
                        proxima_nickel_factura = nickel_factura
                    elif proxima_nickel_factura.fecha_vencimiento > nickel_factura.fecha_vencimiento:
                        proxima_nickel_factura = nickel_factura
            
            if proxima_nickel_factura:
                result[invoice.id] = proxima_nickel_factura.fecha_vencimiento
            else:
                result[invoice.id] = False
        return result
    
    _columns = {
        'nickel_factura_ids': fields.one2many('nickel_factura', 'factura_id', 'Facturas Nickel'),
        'residual_2': fields.float('Importe restante', digits_compute=dp.get_precision('Account'), help="Importe restante a pagar."),
        'pagado': fields.boolean('Pagado', help='Indica si la factura ha sido pagada.'),
        'fecha_vencimiento': fields.function(_proxima_fecha_vencimiento, string='Fecha de Vencimiento', type='date',
                                    help="Fecha del proximo vencimiento."),
    }
    
    _defaults = {
        'pagado': True,
    }
    
account_invoice()
