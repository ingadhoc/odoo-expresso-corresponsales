# -*- coding: utf-8 -*-

from openerp import models, pooler, api, _
from ..actualizador.facade_actualizacion import Facade_Actualizacion


class panel_control_update_nickel(models.TransientModel):
    _name = 'panel_control_update_nickel'
    _description = u'Panel de Control de las Actualizaciones de Nickel'

    # Clientes

    @api.model
    def update_partners(self, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        # print facade_actualizacion
        facade_actualizacion.update_partners(self._cr, self._uid, context=context)

    # Facturas
    @api.model
    def update_invoices(self, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        # print facade_actualizacion
        facade_actualizacion.update_invoices(self._cr, self._uid, context=context)

    # Stock
    @api.model
    def update_stock(self, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        # print facade_actualizacion
        facade_actualizacion.update_stock(self._cr, self._uid, context=context)

    # Threading
    @api.model
    def actualizar_todo_threading(self, context=None):
        #expresso_actualizador_obj = pooler.get_pool(cr.dbname).get('expresso_nickel.actualizador_nickel')
        # expresso_actualizador_obj = Facade_Actualizacion
        expresso_actualizador_obj = Facade_Actualizacion(pooler)
        expresso_actualizador_obj.update_todo_threading(
            self._cr, self._uid, context=context)

    @api.model
    def actualizar_todo_threading_2(self, context=None):
        # facade_actualizacion = Facade_Actualizacion
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.update_todo_threading(
            self._cr, self._uid, context=context)
