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
import pooler

class expresso_info_corresponsal(osv.osv):
    _name = 'expresso.info_corresponsal'
    _inherit = 'expresso.info_corresponsal'
    
    _columns = {
        'nickel_cliente_id': fields.many2one('nickel_cliente', 'Cliente de Nickel', required=False,),
    }
    
expresso_info_corresponsal()

class nickel_cliente(osv.osv):
    '''
    Cliente obtenido desde la base de datos de Nickel
    '''
    _name = 'nickel_cliente'
    _description = 'Cliente de Nickel'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'name':fields.char('Nombre', size=100, required=True, readonly=True),
        'codigo_pais':fields.char('Codigo del Pais', size=10, required=False, readonly=True),
        'booleano':fields.char('Nombre', size=100, required=True, readonly=True),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(nickel_cliente, self).copy(cr, uid, id, default, context)
    
    def get_user_desde_id_remoto(self, cr, uid, id_remoto, context=None):
        nickel_obj = pooler.get_pool(cr.dbname).get('nickel_cliente')
        id_nickel = nickel_obj.search(cr, uid, [('id_remoto', '=', id_remoto)], context=context)
        if not id_nickel:
            return None
        if isinstance(id_nickel, list):
            id_nickel = id_nickel[0]
        
        info_corresponsal_obj = pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        id_info_corresponsal = info_corresponsal_obj.search(cr, uid, [('nickel_cliente_id', '=', id_nickel)], context=context)
        user_id = info_corresponsal_obj.get_users_from_info_corresponsal(cr, uid, id_info_corresponsal, context=context)
        
        if not user_id:
            return None
        if isinstance(user_id, list):
            user_id = user_id[0]
        return user_id
        
        
    def get_partner_desde_id_remoto(self, cr, uid, id_remoto, context=None):
        user_id = self.get_user_desde_id_remoto(cr, uid, id_remoto, context=context)
        users_obj = pooler.get_pool(cr.dbname).get('res.users')
        user = users_obj.browse(cr, uid, user_id, context=context)
        if not user:
            return None
        if isinstance(user, list):
            user = user[0]
        
        return user.partner_id.id
        
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
nickel_cliente()





