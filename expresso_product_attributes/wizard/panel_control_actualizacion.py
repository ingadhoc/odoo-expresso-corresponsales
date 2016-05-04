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
import datetime

from osv import osv, fields

from ..actualizador.facade_actualizacion import Facade_Actualizacion

class panel_control_actualizacion(osv.osv):
    _name = 'expresso.panel_control_actualizacion'
    _description = u'Panel de Control de las Actualizaciones'
    
    ''' Clientes '''
    def actualizar_clientes(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_clientes(cr, uid, context=context)
        return True
        
    ''' Atributos de Titulos '''
    def actualizar_atributos_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_atributos_titulos(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    ''' Titulos '''
    def obtener_info_objeto_remoto_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_titulos(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    def actualizar_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_titulos(cr, uid, context=context)
        return True
        
    def actualizar_imagenes(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_imagenes(cr, uid, context=context)
        return True
        
    ''' Facturas '''
    def obtener_info_objeto_remoto_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_facturas(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    def actualizar_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_facturas(cr, uid, context=context)
        return True
    
    def obtener_info_objeto_remoto_si_no_presente_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_facturas(cr, uid,
                informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    def marcar_info_objeto_remoto_para_actualizar_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.marcar_info_objeto_remoto_para_actualizar_facturas(cr, uid,
                informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    ''' Packings '''
    def obtener_info_objeto_remoto_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_packing(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    def actualizar_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_packing(cr, uid, context=context)
        return True
    
    def obtener_info_objeto_remoto_si_no_presente_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_packing(cr, uid,
                informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    def marcar_info_objeto_remoto_para_actualizar_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.marcar_info_objeto_remoto_para_actualizar_packing(cr, uid,
                informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    ''' Threading '''
    def actualizar_todo_threading(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    
    
    
    ''' Obtener ISBNs si no presentes '''
    def obtener_info_objeto_remoto_si_no_presente_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_titulos(cr, uid,
                informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    ''' Marcar todos los ISBNs para actualizar '''
    def marcar_todos_isbns_para_actualizar(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.marcar_todos_isbns_para_actualizar(cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True
    
    marcar_todos_isbns_para_actualizar

panel_control_actualizacion()










