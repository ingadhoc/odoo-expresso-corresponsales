# -*- coding: utf-8 -*-

from openerp import models, pooler, api
import logging
from actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)


class actualizador_expresso(models.Model):
    _name = 'expresso.actualizador'
    _description = 'Actualizador'

    @api.model
    def actualizar_todo_threading(
            self, informacion='Actualizador', continuation=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.actualizar_todo_threading(
            informacion=informacion, continuation=continuation)
