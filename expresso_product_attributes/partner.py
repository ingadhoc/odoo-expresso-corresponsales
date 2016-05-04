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

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    _columns = {
        'id_remoto': fields.integer('Identificador Remoto'),
        'associated_user_id': fields.one2many('res.users', 'partner_id', 'Usuario Associado.'),
        'info_corresponsal_id': fields.many2one('expresso.info_corresponsal', u'Información de Usuario', required=False),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(res_partner, self).copy(cr, uid, id, default, context)

res_partner()


class res_partner_address(osv.osv):
    _name = 'res.partner.address'
    _inherit = 'res.partner.address'
    
    def name_get(self, cr, user, ids, context=None):
        ret = super(res_partner_address, self).name_get(cr, user, ids, context=context)
        ret2 = []
        for pair in ret:
            name = pair[1]
            if len(name) <= 40:
                trunc = name
            else:
                trunc = ' '.join(name[:40+1].split(' ')[0:-1]) + '...'
            ret2.append((pair[0], trunc))
        return ret2
        
res_partner_address()


















