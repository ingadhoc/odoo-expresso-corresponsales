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

import time
import datetime
import traceback

import logging
from suds.client import Client
from lxml import objectify # http://lxml.de/objectify.html

from generic_updater import Actualizador_Generico
import configuracion_actualizacion

_logger = logging.getLogger(__name__)

class Actualizador_Titulos_Atributos_Estandard(Actualizador_Generico):
    
    def __init__(self, pooler, url_ws):
        Actualizador_Generico.__init__(self, pooler, url_ws)
        
    # Funciones para tratamiento de objetos estandar
    def procesar_xml_estandar(self, cr, uid,  clase, xml, context=None):
        '''
        A partir de un xml que contiene los tags <id/> y <denomination/>, crea un objeto de la clase parametro con
        estos atributos.
        '''
        try:
            registros = objectify.fromstring(xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al convertir a objeto el xml %s. Error: %s', xml, e)
            return False
        
        if hasattr(registros, 'error'):
            _logger.info('Ningún %s para procesar', clase)
            return False
        for registro in registros.iterchildren():
            id_remoto = registro.id
            denomination = registro.denomination.text
            
            ids_objetos = []
            if id_remoto:
                ids_objetos = self.get_ids_from_id_remoto(cr, uid, clase, id_remoto, context=context)
            elif denomination:
                ids_objetos = self.get_ids_from_denomination(cr, uid, clase, denomination, context=context)
            
            class_obj = self.pooler.get_pool(cr.dbname).get(clase)
            if not ids_objetos:
                class_obj.create(cr, uid, {'id_remoto': id_remoto, 'denomination': denomination })
            else:
                class_obj.write(cr, uid, ids_objetos, {'denomination': denomination })
        _logger.info('%s actualizado correctamente', clase)
        return True



class Actualizador_Titulos_Atributos_Ciclo(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Ciclos '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_ciclos)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                ciclos_xml = cliente.service.listCiclos(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                ciclos_xml = cliente.service.listCiclos().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.ciclo', ciclos_xml, context=context)


class Actualizador_Titulos_Atributos_Coleccion(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Colecciones '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_colecciones)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                colecciones_xml = cliente.service.listColecciones(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                colecciones_xml = cliente.service.listColecciones().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.coleccion', colecciones_xml, context=context)


class Actualizador_Titulos_Atributos_Curso(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Cursos '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_cursos)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                cursos_xml = cliente.service.listCursos(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                cursos_xml = cliente.service.listCursos().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.curso', cursos_xml, context=context)

class Actualizador_Titulos_Atributos_Encuadernacion(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Encuadernaciones '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_encuadernaciones)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                encuadernaciones_xml = cliente.service.listEncuadernaciones(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                encuadernaciones_xml = cliente.service.listEncuadernaciones().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.encuadernacion', encuadernaciones_xml, context=context)


class Actualizador_Titulos_Atributos_Forma_de_Envio(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Formas de Envio '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_formas_envio)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                formas_envio_xml = cliente.service.listFormasEnvio(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                formas_envio_xml = cliente.service.listFormasEnvio().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
            
        return self.procesar_xml_estandar(cr, uid, 'expresso.forma_envio', formas_envio_xml, context=context)


class Actualizador_Titulos_Atributos_Idioma(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Idiomas '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_idiomas)
    
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                idiomas_xml = cliente.service.listIdiomas(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                idiomas_xml = cliente.service.listIdiomas().encode("iso-8859-1").replace('&','&amp;')
            idiomas = objectify.fromstring(idiomas_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        if hasattr(idiomas, 'error'):
            _logger.info('Ningún expresso.idioma para procesar')
            return False
        for idioma in idiomas.iterchildren():
            id_remoto = idioma.id
            try:
                idioma_xml = cliente.service.getIdioma(id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
                idioma = objectify.fromstring(idioma_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                continue
            
            denomination = idioma.denomination.text
            idioma_amigo = False
            if idioma.amigo and idioma.amigo.text == 'S':
                idioma_amigo = True
            
            ids_objetos = self.get_ids_from_id_remoto(cr, uid, 'expresso.idioma', id_remoto, context)
            idioma_obj = self.pooler.get_pool(cr.dbname).get('expresso.idioma')
            if not ids_objetos:
                vals = {'id_remoto': id_remoto, 'denomination': denomination, 'idioma_amigo': idioma_amigo}
                idioma_obj.create(cr, uid, vals, context=context)
            else:
                vals = {'denomination': denomination, 'idioma_amigo': idioma_amigo}
                idioma_obj.write(cr, uid, ids_objetos, vals, context=context)
        _logger.info('expresso.idioma actualizado correctamente')
        return True


class Actualizador_Titulos_Atributos_Proyecto(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Proyectos '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_proyectos)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                proyectos_xml = cliente.service.listProyectos(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                proyectos_xml = cliente.service.listProyectos().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.proyecto', proyectos_xml, context=context)


class Actualizador_Titulos_Atributos_Publico(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Publicos '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_publicos)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                publicos_xml = cliente.service.listPublicos(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                publicos_xml = cliente.service.listPublicos().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.publico', publicos_xml, context=context)


class Actualizador_Titulos_Atributos_Situacion(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Situaciones '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_situaciones)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                situaciones_xml = cliente.service.listSituaciones(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                situaciones_xml = cliente.service.listSituaciones().encode("iso-8859-1").replace('&','&amp;')
            situaciones = objectify.fromstring(situaciones_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        if hasattr(situaciones, 'error'):
            _logger.info('Ningún expresso.situacion para procesar')
            return False
        for situacion_it in situaciones.iterchildren():
            id_remoto = situacion_it.id
            try:
                situacion_xml = cliente.service.getSituacion(id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
                situacion = objectify.fromstring(situacion_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                continue
            
            denomination = situacion.denomination.text
            permite_pedido = False
            if situacion.admitepedidos and situacion.admitepedidos.text == 'S':
                permite_pedido = True
            
            ids_situacion = self.get_ids_from_id_remoto(cr, uid, 'expresso.situacion', id_remoto, context)
            situacion_obj = self.pooler.get_pool(cr.dbname).get('expresso.situacion')
            if not ids_situacion:
                vals = {'id_remoto': id_remoto, 'denomination': denomination, 'permite_pedido': permite_pedido}
                situacion_obj.create(cr, uid, vals, context=context)
            else:
                vals = {'denomination': denomination, 'permite_pedido': permite_pedido}
                situacion_obj.write(cr, uid, ids_situacion, vals, context=context)
        _logger.info('expresso.situacion actualizado correctamente')
        return True


class Actualizador_Titulos_Atributos_Tipo(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Tipos '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_tipos)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                tipos_xml = cliente.service.listTipos(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                tipos_xml = cliente.service.listTipos().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.tipo', tipos_xml, context=context)


class Actualizador_Titulos_Atributos_Valor(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Valores '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_valores)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                valores_xml = cliente.service.listValores(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                valores_xml = cliente.service.listValores().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.valor', valores_xml, context=context)


class Actualizador_Titulos_Atributos_Director(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Directores '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_directores)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                directores_xml = cliente.service.listDirectores(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                directores_xml = cliente.service.listDirectores().encode("iso-8859-1").replace('&','&amp;')
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        return self.procesar_xml_estandar(cr, uid, 'expresso.director', directores_xml, context=context)


class Actualizador_Titulos_Atributos_Materia(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Materias '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_materias)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                materias_xml = cliente.service.listMaterias(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                materias_xml = cliente.service.listMaterias().encode("iso-8859-1").replace('&','&amp;')
            materias = objectify.fromstring(materias_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        if hasattr(materias, 'error'):
            _logger.info('Ningún expresso.materia para procesar')
            return False
        for materia_it in materias.iterchildren():
            id_remoto = materia_it.id
            try:
                materia_xml = cliente.service.getMateria(id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
                materia = objectify.fromstring(materia_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                continue
            
            denomination = materia.denomination.text
            
            id_remoto_director = materia.IDdirector.text
            ids_director = self.get_ids_from_id_remoto(cr, uid, 'expresso.director', id_remoto_director, context=context)
            id_director = False
            if ids_director:
                id_director = ids_director[0]
            
            id_remoto_proyecto = materia.IDproyecto.text
            ids_proyecto = self.get_ids_from_id_remoto(cr, uid, 'expresso.proyecto', id_remoto_proyecto, context=context)
            id_proyecto = False
            if ids_proyecto:
                id_proyecto = ids_proyecto[0]
            
            ids_objetos = self.get_ids_from_id_remoto(cr, uid, 'expresso.materia', id_remoto, context)
            materia_obj = self.pooler.get_pool(cr.dbname).get('expresso.materia')
            if not ids_objetos:
                vals = {'id_remoto': id_remoto, 'denomination': denomination, 'director_id': id_director, 'proyecto_id': id_proyecto}
                materia_obj.create(cr, uid, vals, context=context)
            else:
                vals = {'denomination': denomination, 'director_id': id_director, 'proyecto_id': id_proyecto}
                materia_obj.write(cr, uid, ids_objetos, vals, context=context)
        
        _logger.info('expresso.materia actualizado correctamente')
        return True


class Actualizador_Titulos_Atributos_Seleccion(Actualizador_Titulos_Atributos_Estandard):
    ''' Actualizador de Selecciones '''
    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_selecciones)
        
    def actualizar_registros(self, cr, uid, sync_info, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        from_date = self.get_string_date(sync_info)
        
        try:
            if from_date:
                selecciones_xml = cliente.service.listSelecciones(updated=from_date).encode("iso-8859-1").replace('&','&amp;')
            else:
                selecciones_xml = cliente.service.listSelecciones().encode("iso-8859-1").replace('&','&amp;')
            selecciones = objectify.fromstring(selecciones_xml)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
            return False
        
        if hasattr(selecciones, 'error'):
            _logger.info('Ningún expresso.seleccion para procesar')
            return False
        for seleccion_it in selecciones.iterchildren():
            id_remoto = seleccion_it.id
            try:
                seleccion_xml = cliente.service.getSeleccion(id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
                seleccion = objectify.fromstring(seleccion_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                continue
            
            denomination = seleccion.denomination.text
            
            id_remoto_materia = seleccion.IDmateria.text
            ids_materia = self.get_ids_from_id_remoto(cr, uid, 'expresso.materia', id_remoto_materia, context=context)
            matter_id = False
            if ids_materia:
                matter_id = ids_materia[0]
            
            id_remoto_proyecto = seleccion.IDproyecto.text
            ids_proyecto = self.get_ids_from_id_remoto(cr, uid, 'expresso.proyecto', id_remoto_proyecto, context=context)
            id_proyecto = False
            if ids_proyecto:
                id_proyecto = ids_proyecto[0]
            
            ids_objetos = self.get_ids_from_id_remoto(cr, uid, 'expresso.seleccion', id_remoto, context)
            seleccion_obj = self.pooler.get_pool(cr.dbname).get('expresso.seleccion')
            if not ids_objetos:
                vals = {'id_remoto': id_remoto, 'denomination': denomination, 'matter_id': matter_id, 'proyecto_id': id_proyecto}
                seleccion_obj.create(cr, uid, vals, context=context)
            else:
                vals = {'denomination': denomination, 'matter_id': matter_id, 'proyecto_id': id_proyecto}
                seleccion_obj.write(cr, uid, ids_objetos, vals, context=context)
        _logger.info('expresso.seleccion actualizado correctamente')
        return True






