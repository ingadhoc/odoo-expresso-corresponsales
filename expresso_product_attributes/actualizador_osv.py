# -*- coding: utf-8 -*-

from openerp import models
from openerp import pooler
import logging

# from expresso_nickel.actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)


class actualizador_expresso(models.Model):
    _name = 'expresso.actualizador'
    _description = 'Actualizador'

    def actualizar_todo_threading(self, cr, uid, informacion='Actualizador', continuation=None, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(
            cr, uid, informacion=informacion, continuation=continuation, context=context)
