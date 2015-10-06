# -*- coding: utf-8 -*-

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
        log_entry_obj = self.pool.get('expresso.sync_log_entry')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = {}
        log_entry['datetime'] = now
        log_entry['objeto'] = objeto
        log_entry['informacion'] = informacion
        log_entry['error_al_procesar'] = error_al_procesar
        log_entry['mensaje_error'] = mensaje_error

        log_entry_obj.create(cr, uid, log_entry, context=context)

    # Clientes
    def update_partners(self, cr, uid, context=None):
        _logger.info('Actualizando Clientes de Nickel')
        conector_nickel = Conector_Nickel(pooler)
        conector_nickel.update_partners(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_clientes', informacion='',
                                error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización de los Clientes de Nickel')

    # Facturas
    def update_invoices(self, cr, uid, context=None):
        _logger.info('Actualizando Facturas de Nickel')
        conector_nickel = Conector_Nickel(pooler)
        conector_nickel.update_invoices(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_facturas', informacion='',
                                error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización de las Facturas de Nickel')

    # Stock
    def update_stock(self, cr, uid, context=None):
        _logger.info('Actualizando el Stock desde Nickel')
        conector_nickel = Conector_Nickel(pooler)
        conector_nickel.update_stock(cr, uid, context=context)
        self.insertar_log_entry(cr, uid, 'n_stock', informacion='',
                                error_al_procesar=False, mensaje_error='', context=context)
        _logger.info('Se finalizo la actualización del Stock desde Nickel')

    # Threading
    def update_todo_threading(self, cr, uid, context=None):
        _logger.info('Iniciando actualización asincrona de Nickel.')
        thread = threading.Thread(
            target=self.threading_actualizar_clientes, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()
        return True

    def threading_update_partners(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.update_partners(cr, uid, context=context)
        thread = threading.Thread(
            target=self.threading_update_invoices, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()

    def threading_update_invoices(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.update_invoices(cr, uid, context=context)
        thread = threading.Thread(
            target=self.threading_update_stock, args=(cr.dbname, uid, context))
        cr.commit()
        cr.close()
        thread.start()

    def threading_update_stock(self, db_name, uid, context=None):
        db, pool = self.pooler.get_db_and_pool(db_name)
        cr = db.cursor()
        self.update_stock(cr, uid, context=context)
        cr.commit()
        cr.close()
        _logger.info('Terminada la actualización asincrona de Nickel.')
