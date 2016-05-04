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
import decimal_precision as dp

class expresso_packing(osv.osv):
    _name = 'expresso.packing'
    _description = 'Packing'
    _rec_name = 'id_remoto'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'date': fields.datetime('Fecha Orden', required=True, help='Fecha de la Orden'),
        'number_of_packages': fields.integer('Numero de paquetes'),
        'partner_id': fields.many2one('res.partner', 'Corresponsal', required=True),
        'address_id': fields.many2one('res.partner.address', u'Dirección', required=True,
                                      domain="[('partner_id','=', partner_id)]"),
        'imprimirpeso': fields.char('Imprimir Peso', size=30, required=False),
        
        'packing_box_ids' : fields.one2many('expresso.packing.box', 'packing_id', 'Cajas'),
        'invoice_ids' : fields.one2many('account.invoice', 'packing_id', 'Facturas'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(expresso_packing, self).copy(cr, uid, id, default, context)
        
expresso_packing()

class expresso_packing_box(osv.osv):
    _name = 'expresso.packing.box'
    _description = 'Cajas de Packing'
    
    _columns = {
        'name': fields.char('Nombre', size=64),
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'weight': fields.float('Peso'),
        'packing_id': fields.many2one('expresso.packing', 'Packing', required=True),
        
        'packing_detail_ids' : fields.one2many('expresso.packing.detail', 'box_id', 'Detalles'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(expresso_packing_box, self).copy(cr, uid, id, default, context)
        
expresso_packing_box()

class expresso_packing_detail(osv.osv):
    _name = 'expresso.packing.detail'
    _description = 'Detalle de Packing'
    
    _columns = {
        'name': fields.char('Nombre', size=64),
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'product_id': fields.many2one('product.product', 'Producto', required=False, domain=[('type','<>','service')]),
        'product_qty': fields.float('Cantidad', digits_compute=dp.get_precision('Product UoM'), required=True),
        'weight': fields.float('Peso'),
        'box_id': fields.many2one('expresso.packing.box', 'Caja', required=True),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(expresso_packing_detail, self).copy(cr, uid, id, default, context)
        
expresso_packing_detail()










