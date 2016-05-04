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

import netsvc

from osv import fields, osv
import pooler

class multi_marcar_para_procesar(osv.osv_memory):
    _name = 'multi_marcar_para_procesar'
    _description = 'Marca multiples entradas para reprocesar'
    
    def multi_marcar_para_procesar(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        if active_ids:
            info_objeto_remoto_obj = self.pool.get('expresso.info_objeto_remoto')
            info_objeto_remoto_obj.marcar_para_procesar(cr, uid, active_ids, context=context)
        return { 'type': 'ir.actions.act_window_close'}
    
multi_marcar_para_procesar()










