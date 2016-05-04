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
import pooler
import logging
import threading
import traceback

from actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)

class actualizador_expresso(osv.osv):
    _name = 'expresso.actualizador'
    _description = 'Actualizador'
    
    def actualizar_todo_threading(self, cr, uid, informacion='Actualizador', continuation=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(cr, uid, informacion=informacion, continuation=continuation, context=context)
    
actualizador_expresso()







