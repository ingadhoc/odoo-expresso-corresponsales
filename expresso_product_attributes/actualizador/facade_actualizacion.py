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

import datetime
import traceback
import logging
import threading

from actualizador_clientes import Actualizador_Clientes
from actualizador_titulos import Actualizador_Titulos
from actualizador_facturas import Actualizador_Facturas
from actualizador_packing import Actualizador_Packing
from actualizador_pedidos import Actualizador_Pedidos
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Ciclo
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Coleccion
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Curso
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Encuadernacion
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Forma_de_Envio
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Idioma
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Proyecto
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Publico
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Situacion
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Tipo
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Valor
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Director
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Materia
from actualizador_titulos_atributos import Actualizador_Titulos_Atributos_Seleccion

_logger = logging.getLogger(__name__)


class Facade_Actualizacion:

    def __init__(self, pooler):
        self.pooler = pooler

    '''
    Funciones Generales
    '''
    def obtener_ultima_actualizacion(self, cr, uid, obj_class, context=None):
        '''
        Dado
        '''
        sync_info_obj = self.pooler.get_pool(cr.dbname).get('expresso.sync_info')
        filtro = [('class', '=', obj_class)]
        sync_info_ids = sync_info_obj.search(cr, uid, filtro, limit=1, order='datetime desc', context=context)
        
        if not sync_info_ids:
            return None
        
        sync_info = sync_info_obj.browse(cr, uid, sync_info_ids[0], context=context)
        if not sync_info or len(sync_info.datetime) < 19:
            return None
        
        return sync_info
    
    def insertar_info_actualizacion(self, cr, uid, informacion, obj_class, context=None):
        sync_info_obj = self.pooler.get_pool(cr.dbname).get('expresso.sync_info')
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sync_info_value = {'datetime': now, 'informacion': informacion, 'class': obj_class}
        sync_info_obj.create(cr, uid, sync_info_value, context=context)
    
    def insertar_log_entry(self, cr, uid, objeto, informacion='', error_al_procesar=False, mensaje_error='', context=None):
        log_entry_obj = self.pooler.get_pool(cr.dbname).get('expresso.sync_log_entry')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {}
        log_entry['datetime'] = now
        log_entry['objeto'] = objeto
        log_entry['informacion'] = informacion
        log_entry['error_al_procesar'] = error_al_procesar
        log_entry['mensaje_error'] = mensaje_error
        
        log_entry_obj.create(cr, uid, log_entry, context=context)
        
    '''
    Clientes
    '''
    def actualizar_clientes(self, cr, uid, context=None):
        actualizador = Actualizador_Clientes(self.pooler)
        error_al_procesar = False
        mensaje_error = ''
        try:
            actualizador.actualizar_clientes(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los Clientes. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
        self.insertar_log_entry(cr, uid, 'clientes', informacion='', error_al_procesar=error_al_procesar,
                                mensaje_error=mensaje_error, context=context)
    
    '''
    Titulos
    '''
    def obtener_info_objeto_remoto_titulos(self, cr, uid, informacion='', context=None):
        sync_info = self.obtener_ultima_actualizacion(cr, uid, 'product.product', context=context)
        actualizador = Actualizador_Titulos(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto(cr, uid, sync_info, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los registros ISBN. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
        if actualizado:
            self.insertar_info_actualizacion(cr, uid, informacion, 'product.product', context=context)
        
        
    def actualizar_un_titulo(self, cr, uid, info_objeto_id, context=None):
        actualizador = Actualizador_Titulos(self.pooler)
        try:
            actualizador.actualizar_un_libro_desde_info_objeto_id(cr, uid, info_objeto_id, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando el Titulos. Error: %s', e)
    
    def actualizar_titulos(self, cr, uid, context=None):
        actualizador = Actualizador_Titulos(self.pooler)
        error_al_procesar = False
        mensaje_error = ''
        try:
            actualizador.actualizar_libros(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los Titulos. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
        self.insertar_log_entry(cr, uid, 'titulos', informacion='', error_al_procesar=error_al_procesar,
                                mensaje_error=mensaje_error, context=context)
        
    def actualizar_imagenes(self, cr, uid, context=None):
        actualizador = Actualizador_Titulos(self.pooler)
        try:
            actualizador.actualizar_imagenes(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando las imagenes de los Titulos. Error: %s', e)
    
    def obtener_info_objeto_remoto_si_no_presente_titulos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto_si_no_presente(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al obtener los registros ISBN insertados si no presentes. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    def marcar_todos_isbns_para_actualizar(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.marcar_todos_isbns_para_actualizar(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al querer marcar todos los registros ISBN para actualizar. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    '''
    Facturas
    '''
    def obtener_info_objeto_remoto_facturas(self, cr, uid, informacion='', context=None):
        sync_info = self.obtener_ultima_actualizacion(cr, uid, 'account.invoice', context=context)
        actualizador = Actualizador_Facturas(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto(cr, uid, sync_info, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los registros de Facturas. Error: %s', e)
        if actualizado:
            self.insertar_info_actualizacion(cr, uid, informacion, 'account.invoice', context=context)
    
    def obtener_info_objeto_remoto_si_no_presente_facturas(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Facturas(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto_si_no_presente(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los registros de Facturas. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    def marcar_info_objeto_remoto_para_actualizar_facturas(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Facturas(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.marcar_info_objeto_remoto_para_actualizar(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al querer marcar todos los registros de Factura para actualizar. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    
    
    
    
    def actualizar_una_factura(self, cr, uid, info_objeto_id, context=None):
        actualizador = Actualizador_Facturas(self.pooler)
        try:
            actualizador.actualizar_una_factura_desde_info_objeto_id(cr, uid, info_objeto_id, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando la Factura. Error: %s', e)
            
    def actualizar_facturas(self, cr, uid, context=None):
        actualizador = Actualizador_Facturas(self.pooler)
        error_al_procesar = False
        mensaje_error = ''
        try:
            actualizador.actualizar_facturas(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando las Facturas. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
        self.insertar_log_entry(cr, uid, 'facturas', informacion='', error_al_procesar=error_al_procesar,
                                mensaje_error=mensaje_error, context=context)
    '''
    Packing
    '''
    def obtener_info_objeto_remoto_packing(self, cr, uid, informacion='', context=None):
        sync_info = self.obtener_ultima_actualizacion(cr, uid, 'expresso.packing', context=context)
        actualizador = Actualizador_Packing(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto(cr, uid, sync_info, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los registros de Packing. Error: %s', e)
        if actualizado:
            self.insertar_info_actualizacion(cr, uid, informacion, 'expresso.packing', context=context)
    
    def obtener_info_objeto_remoto_si_no_presente_packing(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Packing(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.obtener_info_objeto_remoto_si_no_presente(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando los registros de Packing. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    def marcar_info_objeto_remoto_para_actualizar_packing(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Packing(self.pooler)
        actualizado = False
        try:
            actualizado = actualizador.marcar_info_objeto_remoto_para_actualizar(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al querer marcar todos los registros de Packing para actualizar. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
    
    
    
    
    
    def actualizar_un_packing(self, cr, uid, info_objeto_id, context=None):
        actualizador = Actualizador_Packing(self.pooler)
        try:
            actualizador.actualizar_un_packing_desde_info_objeto_id(cr, uid, info_objeto_id, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando el Packing. Error: %s', e)
    
    def actualizar_packing(self, cr, uid, context=None):
        actualizador = Actualizador_Packing(self.pooler)
        error_al_procesar = False
        mensaje_error = ''
        try:
            actualizador.actualizar_packing(cr, uid, context=context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando las Packings. Error: %s', e)
            error_al_procesar = True
            mensaje_error = e
        self.insertar_log_entry(cr, uid, 'packings', informacion='', error_al_procesar=error_al_procesar,
                                mensaje_error=mensaje_error, context=context)
    
    '''
    Pedidos
    '''
    def crear_pedido_remoto(self, cr, uid, ids, context=None):
        actualizador = Actualizador_Pedidos(self.pooler)
        actualizador.crear_pedido_remoto(cr, uid, ids, context=context)
    
    '''
    Atributos
    '''
    def actualizar_atributos_titulos(self, cr, uid, informacion='', context=None):
        self.actualizar_ciclos(cr, uid, informacion=informacion, context=context)
        self.actualizar_colecciones(cr, uid, informacion=informacion, context=context)
        self.actualizar_cursos(cr, uid, informacion=informacion, context=context)
        self.actualizar_encuadernaciones(cr, uid, informacion=informacion, context=context)
        self.actualizar_formas_de_envio(cr, uid, informacion=informacion, context=context)
        self.actualizar_idiomas(cr, uid, informacion=informacion, context=context)
        self.actualizar_proyectos(cr, uid, informacion=informacion, context=context)
        self.actualizar_publicos(cr, uid, informacion=informacion, context=context)
        self.actualizar_situaciones(cr, uid, informacion=informacion, context=context)
        self.actualizar_tipos(cr, uid, informacion=informacion, context=context)
        self.actualizar_valores(cr, uid, informacion=informacion, context=context)
        self.actualizar_directores(cr, uid, informacion=informacion, context=context)
        self.actualizar_materias(cr, uid, informacion=informacion, context=context)
        self.actualizar_selecciones(cr, uid, informacion=informacion, context=context)
        self.insertar_log_entry(cr, uid, 'atributos', informacion='', error_al_procesar=False, mensaje_error='', context=context)
    
    def actualizar_registro_generico(self, cr, uid, clase, actualizador, informacion='', context=None):
        sync_info = self.obtener_ultima_actualizacion(cr, uid, clase, context=context)
        actualizado = False
        try:
            actualizado = actualizador.actualizar_registros(cr, uid, sync_info, context)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error actualizando la clase %s. Error: %s', clase, e)
        if actualizado:
            self.insertar_info_actualizacion(cr, uid, informacion, clase, context=context)
    '''
    Ciclos
    '''
    def actualizar_ciclos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Ciclo(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.ciclo', actualizador, informacion=informacion, context=context)
    '''
    Colecciones
    '''
    def actualizar_colecciones(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Coleccion(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.coleccion', actualizador, informacion=informacion, context=context)
    '''
    Cursos
    '''
    def actualizar_cursos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Curso(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.curso', actualizador, informacion=informacion, context=context)
    '''
    Encuadernaciones
    '''
    def actualizar_encuadernaciones(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Encuadernacion(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.encuadernacion', actualizador, informacion=informacion, context=context)
    '''
    Formas de Envio
    '''
    def actualizar_formas_de_envio(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Forma_de_Envio(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.forma_envio', actualizador, informacion=informacion, context=context)
    '''
    Idioma
    '''
    def actualizar_idiomas(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Idioma(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.idioma', actualizador, informacion=informacion, context=context)
    '''
    Proyecto
    '''
    def actualizar_proyectos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Proyecto(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.proyecto', actualizador, informacion=informacion, context=context)
    '''
    Publico
    '''
    def actualizar_publicos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Publico(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.publico', actualizador, informacion=informacion, context=context)
    '''
    Situacion
    '''
    def actualizar_situaciones(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Situacion(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.situacion', actualizador, informacion=informacion, context=context)
    '''
    Tipo
    '''
    def actualizar_tipos(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Tipo(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.tipo', actualizador, informacion=informacion, context=context)
    '''
    Valor
    '''
    def actualizar_valores(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Valor(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.valor', actualizador, informacion=informacion, context=context)
    '''
    Director
    '''
    def actualizar_directores(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Director(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.director', actualizador, informacion=informacion, context=context)
    '''
    Materia
    '''
    def actualizar_materias(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Materia(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.materia', actualizador, informacion=informacion, context=context)
    '''
    Seleccion
    '''
    def actualizar_selecciones(self, cr, uid, informacion='', context=None):
        actualizador = Actualizador_Titulos_Atributos_Seleccion(self.pooler)
        self.actualizar_registro_generico(cr, uid, 'expresso.seleccion', actualizador, informacion=informacion, context=context)
    
    
    
    '''
    Threading
    '''
    def actualizar_todo_threading(self, cr, uid, informacion='', continuation=None, context=None):
        _logger.info('Iniciando actualización asincrona.')
        #thread = threading.Thread(target=self.threading_actualizar_clientes, args=(cr.dbname, uid, informacion, continuation, context))
        thread = threading.Thread(target=self.threading_actualizar_clientes, args=(cr.dbname, uid, informacion, continuation, context))
        thread.start()
        return True
    
    def threading_actualizar_clientes(self, db_name, uid, informacion='', continuation=None, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.actualizar_clientes(cr, uid, context=context)
        thread = threading.Thread(target=self.threading_actualizar_atributos_titulos, args=(cr.dbname, uid, informacion, continuation, context))
        cr.commit()
        cr.close()
        thread.start()
    
    def threading_actualizar_atributos_titulos(self, db_name, uid, informacion='', continuation=None, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.actualizar_atributos_titulos(cr, uid, informacion=informacion, context=context)
        thread = threading.Thread(target=self.threading_actualizar_titulos, args=(cr.dbname, uid, informacion, continuation, context))
        cr.commit()
        cr.close()
        thread.start()
        
    def threading_actualizar_titulos(self, db_name, uid, informacion='', continuation=None, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.obtener_info_objeto_remoto_titulos(cr, uid, informacion=informacion, context=context)
        self.actualizar_titulos(cr, uid, context=context)
        thread = threading.Thread(target=self.threading_actualizar_facturas, args=(cr.dbname, uid, informacion, continuation, context))
        cr.commit()
        cr.close()
        thread.start()
    
    def threading_actualizar_facturas(self, db_name, uid, informacion='', continuation=None, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.obtener_info_objeto_remoto_facturas(cr, uid, informacion=informacion, context=context)
        self.actualizar_facturas(cr, uid, context=context)
        thread = threading.Thread(target=self.threading_actualizar_packing, args=(cr.dbname, uid, informacion, continuation, context))
        cr.commit()
        cr.close()
        thread.start()
    
    def threading_actualizar_packing(self, db_name, uid, informacion='', continuation=None, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.obtener_info_objeto_remoto_packing(cr, uid, informacion=informacion, context=context)
        self.actualizar_packing(cr, uid, context=context)
        cr.commit()
        _logger.info('Terminada la actualización asincrona.')
        if continuation:
            continuation(cr, uid, informacion=informacion, context=context)






