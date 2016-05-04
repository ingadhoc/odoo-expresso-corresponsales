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

import pooler

from osv import osv, fields

from ..actualizador.facade_actualizacion import Facade_Actualizacion

class panel_control_actualizacion_nickel(osv.osv):
    _name = 'panel_control_actualizacion_nickel'
    _description = u'Panel de Control de las Actualizaciones de Nickel'
    
    ''' Clientes '''
    def actualizar_clientes(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_clientes(cr, uid, context=context)
    
    ''' Facturas '''
    def actualizar_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_facturas(cr, uid, context=context)
    
    ''' Stock '''
    def actualizar_stock(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_stock(cr, uid, context=context)
    
    ''' Threading '''
    def actualizar_todo_threading(self, cr, uid, ids=None, context=None):
        #expresso_actualizador_obj = pooler.get_pool(cr.dbname).get('expresso_nickel.actualizador_nickel')
        expresso_actualizador_obj = self.pool.get('expresso_nickel.actualizador')
        expresso_actualizador_obj.actualizar_todo_threading(self, cr, uid, ids=ids, context=context)
    
    def actualizar_todo_threading_2(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(cr, uid, context=context)

panel_control_actualizacion_nickel()










