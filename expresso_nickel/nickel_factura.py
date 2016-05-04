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

class nickel_factura(osv.osv):
    '''
    Cliente obtenido desde la base de datos de Nickel
    '''
    _name = 'nickel_factura'
    _description = 'Facturas de Nickel'
    _order = 'fecha_vencimiento asc'

    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        
        'codigo_cliente': fields.char('Codigo Cliente', size=50, required=False, readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente', required=False),
        
        'numero_factura': fields.char('Numero de Factura', size=50, required=False, readonly=True),
        'factura_id': fields.many2one('account.invoice', 'Factura', required=False),
        
        'serie': fields.char('Serie', size=50, required=False, readonly=True),
        'fecha_factura': fields.date('Fecha de Facturacion', required=False),
        'fecha_vencimiento': fields.date('Fecha de Vencimiento', required=False),
        'importe': fields.float('Importe', required=False),
        'codigo_divisa': fields.char('Codigo de la divisa', size=10, required=False, readonly=True),
        
        'pagado': fields.boolean('Pagado', required=False),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(nickel_factura, self).copy(cr, uid, id, default, context)
    
    def get_invoice_asociados(self, cr, uid, ids, context=None):
        invoice_ids = []
        for factura_nickel in self.browse(cr, uid, ids, context=context):
            if factura_nickel.factura_id:
                invoice_ids.append(factura_nickel.factura_id.id)
        return invoice_ids
    
    _defaults = {
        'pagado': False,
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
    
nickel_factura()



