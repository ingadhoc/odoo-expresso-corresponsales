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

from conector_nickel import Conector_Nickel

_logger = logging.getLogger(__name__)

class Facade_Actualizacion:

    def __init__(self, pooler):
        self.pooler = pooler
    
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
        _logger.info('Actualizando Clientes de Nickel')
        conector_nickel = Conector_Nickel()
        conector_nickel.actualizar_clientes(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_clientes', informacion='', error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización de los Clientes de Nickel')
    
    '''
    Facturas
    '''
    def actualizar_facturas(self, cr, uid, context=None):
        _logger.info('Actualizando Facturas de Nickel')
        conector_nickel = Conector_Nickel()
        conector_nickel.actualizar_facturas(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_facturas', informacion='', error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización de las Facturas de Nickel')
    
    '''
    Stock
    '''
    def actualizar_stock(self, cr, uid, context=None):
        _logger.info('Actualizando el Stock desde Nickel')
        conector_nickel = Conector_Nickel()
        conector_nickel.actualizar_stock(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_stock', informacion='', error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización del Stock desde Nickel')
    
    '''
    Threading
    '''
    def actualizar_todo_threading(self, cr, uid, context=None):
        _logger.info('Iniciando actualización asincrona de Nickel.')
        thread = threading.Thread(target=self.threading_actualizar_clientes, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()
        return True
    
    def threading_actualizar_clientes(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.actualizar_clientes(cr, uid, context=context)
        thread = threading.Thread(target=self.threading_actualizar_facturas, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()
    
    def threading_actualizar_facturas(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.actualizar_facturas(cr, uid, context=context)
        thread = threading.Thread(target=self.threading_actualizar_stock, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()
    
    def threading_actualizar_stock(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.actualizar_stock(cr, uid, context=context)
        cr.commit()
        cr.close()
        _logger.info('Terminada la actualización asincrona de Nickel.')





