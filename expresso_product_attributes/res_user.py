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

class users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'
    
    _columns = {
        'id_remoto': fields.integer('Identificador Remoto'),
        'partner_id': fields.many2one('res.partner', 'Cliente', required=False),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(users, self).copy(cr, uid, id, default, context)
        
users()

