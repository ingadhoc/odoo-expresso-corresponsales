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

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = 'account.invoice'
    _order = 'date_invoice desc'
    
    _columns = {
        'id_remoto': fields.integer('Identificador Remoto'),
        'partida': fields.char('Partida', size=50, required=False),
        'aduana': fields.char('Aduana', size=50, required=False),
        'bultos': fields.integer(u'Número de bultos', required=False),
        'pesoneto': fields.float('Peso Neto', required=False),
        'pesobruto': fields.float('Peso Bruto', required=False),
        'origen': fields.char('Origen', size=50, required=False),
        'muestras': fields.boolean('Muestra', required=False),
        
        'numero_factura': fields.char(u'Número', size=50, required=False),
        'packing_id': fields.many2one('expresso.packing', 'Packing', required=False),
        
        #TODO: Ver que hacemos con esto
        'tipo': fields.char('Tipo Factura', size=100, required=False),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(account_invoice, self).copy(cr, uid, id, default, context)

account_invoice()

class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = 'account.invoice.line'
    
    _columns = {
        'id_remoto': fields.integer('Identificador Remoto'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(account_invoice_line, self).copy(cr, uid, id, default, context)

account_invoice_line()
