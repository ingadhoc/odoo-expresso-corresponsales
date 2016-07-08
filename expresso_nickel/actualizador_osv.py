# -*- coding: utf-8 -*-
from openerp import models,pooler, api
import logging
import threading
import traceback

from actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)


class update_nickel(models.Model):
    _name = 'expresso_nickel.update_nickel'
    _description = 'Actualizador Nickel'

    def update_todo_threading(self, cr, uid, ids=None, context=None):
        def continuation_actualizar_expreso_nickel_threading(cr, uid, informacion='Actualizador', context=None):
            facade_actualizacion = Facade_Actualizacion(pooler)
            facade_actualizacion.actualizar_todo_threading(
                cr, uid, context=context)

        _logger.info('update_nickel.update_todo_threading')
        expresso_actualizador_obj = self.pool.get.get('expresso.actualizador')
        expresso_actualizador_obj.update_todo_threading(
            cr, uid, informacion='Actualizador', continuation=continuation_actualizar_expreso_nickel_threading, context=context)
        return True

    def actualizar_expreso_nickel_threading(self, cr, uid, ids=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(
            cr, uid, informacion='Actualizador', context=context)
