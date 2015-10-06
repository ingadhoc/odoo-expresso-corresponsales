# -*- coding: utf-8 -*-

import traceback
import datetime

import logging
from suds.client import Client

_logger = logging.getLogger(__name__)


class Actualizador_Generico:

    def __init__(self, pooler, url_ws):
        self.url_ws = url_ws
        self.pooler = pooler
        self.cliente = None

    def get_partner_ids_from_user_login(self, cr, uid, user_login, context=None):
        '''
        Los usuarios de OpenERP tiene asignado un Partner. Esta función recibe el nombre de login de un usuario
        y retorna el id del Partner asociado.
        '''
        active_user_ids = self.pool.get('res.users').search(
            cr, uid,
            [('login', '=', user_login)], context=context)
        inactive_user_ids = self.pool.get('res.users').search(
            cr, uid,
            [('login', '=', user_login), ('active', '=', False)],
            context=context)
        user_ids = active_user_ids
        user_ids.extend(inactive_user_ids)

        partner_ids = []
        for user_id in user_ids:
            user = self.pooler.get_pool(cr.dbname).get(
                'res.users').browse(cr, uid, user_id, context=context)
            partner_ids.append(user.partner_id.id)

        return partner_ids

    def get_ids_from_id_remoto(self, cr, uid, clase, id_remoto, context=None):
        '''
        Dado el nombre de una clase y un id_remoto retorna el id correspondiente del objeto en OpenERP
        '''
        obj_ids = self.pool.get(clase).search(
            cr, uid, [('id_remoto', '=', id_remoto)], context=context)
        if obj_ids:
            return obj_ids
        else:
            return False

    def get_ids_from_denomination(self, cr, uid, clase, denomination, context=None):
        '''
        Dado el nombre de una clase y una denominación retorna el id correspondiente del objeto en OpenERP
        '''
        obj_ids = self.pool.get(clase).search(
            cr, uid, [('denomination', '=', denomination)], context=context)
        if obj_ids:
            return obj_ids
        else:
            return False

    def get_cliente(self):
        ''' Retorna el cliente para llamar a los Web Services de Expresso '''
        if not self.cliente:
            try:
                self.cliente = Client(self.url_ws)
            except:
                e = traceback.format_exc()
                _logger.error(
                    'Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return None
        return self.cliente

    def get_string_date(self, sync_info):
        from_date = False
        if sync_info:
            year = sync_info.datetime[0:4]
            month = sync_info.datetime[5:7]
            day = sync_info.datetime[8:10]
            from_date = '' + year + month + day
            from_date = self.two_day_less_date(from_date)
        return from_date

    def get_string_datetime(self, sync_info):
        from_date = False
        if sync_info:
            from_date = self.two_day_less_datetime(sync_info.datetime)
        return from_date

    def two_day_less_date(self, dt_str):
        '''
        Usado para descontar 2 dia en la obtención de identificadores remotos en facturas y packings.
        El formato de entrada y salida es %Y%m%d.
        '''
        try:
            dt = datetime.datetime.strptime(dt_str, '%Y%m%d')
        except:
            return dt_str
        two_day = datetime.timedelta(days=2)
        dt = dt - two_day
        return dt.strftime('%Y%m%d')

    def two_day_less_datetime(self, dt_str):
        '''
        '''
        try:
            dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return dt_str
        two_day = datetime.timedelta(days=2)
        dt = dt - two_day
        return dt.strftime('%Y-%m-%d %H:%M:%S')
