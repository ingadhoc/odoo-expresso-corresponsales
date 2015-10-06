# -*- coding: utf-8 -*-

from openerp import models


class multi_marcar_para_procesar(models.TransientModel):
    _name = 'multi_marcar_para_procesar'
    _description = 'Marca multiples entradas para reprocesar'

    def multi_marcar_para_procesar(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        if active_ids:
            info_objeto_remoto_obj = self.pool.get(
                'expresso.info_objeto_remoto')
            info_objeto_remoto_obj.marcar_para_procesar(
                cr, uid, active_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
