# -*- coding: utf-8 -*-
from openerp import models

# from actualizador.facade_actualizacion import Facade_Actualizacion


class panel_control_actualizacion(models.Model):
    _name = 'expresso.panel_control_actualizacion'
    _description = 'Panel de Control de las Actualizaciones'

    ''' Clientes '''

    def actualizar_clientes(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        print facade_actualizacion
        facade_actualizacion.update_clients(cr, uid, context=context)
        return True

    ''' Atributos de Titulos '''

    def actualizar_atributos_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_atributos_titulos(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    ''' Titulos '''

    def obtener_info_objeto_remoto_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_titulos(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    def actualizar_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_titulos(cr, uid, context=context)
        return True

    def actualizar_imagenes(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_imagenes(cr, uid, context=context)
        return True

    ''' Facturas '''

    def obtener_info_objeto_remoto_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_facturas(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    def actualizar_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_facturas(cr, uid, context=context)
        return True

    def obtener_info_objeto_remoto_si_no_presente_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_facturas(cr, uid,
                                                                                informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    def marcar_info_objeto_remoto_para_actualizar_facturas(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.marcar_info_objeto_remoto_para_actualizar_facturas(cr, uid,
                                                                                informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    ''' Packings '''

    def obtener_info_objeto_remoto_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_packing(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    def actualizar_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_packing(cr, uid, context=context)
        return True

    def obtener_info_objeto_remoto_si_no_presente_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_packing(cr, uid,
                                                                               informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    def marcar_info_objeto_remoto_para_actualizar_packing(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.marcar_info_objeto_remoto_para_actualizar_packing(cr, uid,
                                                                               informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    ''' Threading '''

    def actualizar_todo_threading(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.actualizar_todo_threading(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    ''' Obtener ISBNs si no presentes '''

    def obtener_info_objeto_remoto_si_no_presente_titulos(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.obtener_info_objeto_remoto_si_no_presente_titulos(cr, uid,
                                                                               informacion='Panel de Control de las Actualizaciones', context=context)
        return True

    ''' Marcar todos los ISBNs para actualizar '''

    def marcar_todos_isbns_para_actualizar(self, cr, uid, ids=None, context=None):
        facade_actualizacion = self.pool.get('Facade_Actualizacion')
        facade_actualizacion.marcar_todos_isbns_para_actualizar(
            cr, uid, informacion='Panel de Control de las Actualizaciones', context=context)
        return True

