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
        active_user_ids = self.pooler.get_pool(cr.dbname).get('res.users').search(cr, uid,
                                                        [('login', '=', user_login)], context=context)
        inactive_user_ids = self.pooler.get_pool(cr.dbname).get('res.users').search(cr, uid,
                                                        [('login', '=', user_login),('active', '=', False)], context=context)
        user_ids = active_user_ids
        user_ids.extend(inactive_user_ids)
        
        partner_ids = []
        for user_id in user_ids:
            user = self.pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, user_id, context=context)
            partner_ids.append(user.partner_id.id)
        
        return partner_ids
    
    def get_ids_from_id_remoto(self, cr, uid, clase, id_remoto, context=None):
        '''
        Dado el nombre de una clase y un id_remoto retorna el id correspondiente del objeto en OpenERP
        '''
        obj_ids = self.pooler.get_pool(cr.dbname).get(clase).search(cr, uid, [('id_remoto', '=', id_remoto)], context=context)
        if obj_ids:
            return obj_ids
        else:
            return False
    
    def get_ids_from_denominacion(self, cr, uid, clase, denominacion, context=None):
        '''
        Dado el nombre de una clase y una denominación retorna el id correspondiente del objeto en OpenERP
        '''
        obj_ids = self.pooler.get_pool(cr.dbname).get(clase).search(cr, uid, [('denominacion', '=', denominacion)], context=context)
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
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
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









