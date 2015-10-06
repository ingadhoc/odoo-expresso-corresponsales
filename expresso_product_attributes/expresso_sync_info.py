# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp import pooler
import datetime
# from actualizador.facade_actualizacion import Facade_Actualizacion


class expresso_info_corresponsal(models.Model):
    # Info Corresponsal

    _name = 'expresso.info_corresponsal'
    _description = u'Información de Usuario'
    _rec_name = 'corresponsal'

    corresponsal = fields.Char(
        'Corresponsale',
        size=50,
        required=True)
    user = fields.Char(
        'User',
        size=50,
        required=True)
    contrasenia = fields.Char(
        'Password',
        size=50,
        required=True)
    partner_ids = fields.One2many(
        'res.partner',
        'info_corresponsal_id',
        u'Partner',
        readonly=True)

    def get_users_from_info_corresponsal(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]

        users_obj = pooler.get_pool(cr.dbname).get('res.users')
        user_ids = []
        for info_corresponsal in self.browse(cr, uid, ids, context=context):
            search_ids = users_obj.search(
                cr, uid, [('login', '=', info_corresponsal.user)], context=context)

            if not search_ids:
                continue

            if isinstance(search_ids, list):
                user_ids += search_ids
            else:
                user_ids.append(search_ids)
        return user_ids


class info_objeto_remoto(models.Model):
    # Info Objeto Remoto

    _name = 'expresso.info_objeto_remoto'
    _description = u'Info Objeto Remoto'
    _rec_name = 'id_remoto'

    id_remoto = fields.Char(
        'Identificador Remoto',
        size=30,
        required=True,
        readonly=True)

    clase = fields.Char(
        'Class',
        size=50,
        required=True,
        readonly=True)
    corresponsal = fields.Many2one(
        'expresso.info_corresponsal',
        u'Corresponsal')
    sincronizacion_objeto_remoto_ids = fields.One2many(
        'expresso.sincronizacion_objeto_remoto',
        'info_objeto_remoto_id',
        'Sincronización Objeto Remoto',
        readonly=True)
    error_al_procesar = fields.Boolean(
        'Se encontro un error al procesar el Registro',
        readonly=True, default=False)
    procesado = fields.Boolean('Procesado', readonly=True, default=False)
    datetime = fields.Datetime(
        'Fecha última actualización',
        readonly=True)
    datetime_creation = fields.Datetime(
        'Fecha de creación',
        readonly=True,
        default='datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")')

    def marcar_para_procesar(self, cr, uid, ids, context=None):
        if not ids:
            return False

        info_objeto_remoto_list = self.browse(cr, uid, ids, context=context)
        if not isinstance(info_objeto_remoto_list, list):
            info_objeto_remoto_list = [info_objeto_remoto_list]

        for info_objeto_remoto in info_objeto_remoto_list:
            if not info_objeto_remoto.procesado:
                continue

            sinc_obj = self.pool.get('expresso.sincronizacion_objeto_remoto')

            vals = {}
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals['datetime_creation'] = now
            vals['info_objeto_remoto_id'] = info_objeto_remoto.id
            sinc_obj.create(cr, uid, vals, context=context)
        return True

    def procesar(self, cr, uid, ids, context=None):
        if not ids:
            return False
        info_objeto_remoto = self.browse(cr, uid, ids, context=context)
        if not info_objeto_remoto:
            return False
        if isinstance(info_objeto_remoto, list):
            info_objeto_remoto = info_objeto_remoto[0]
        if info_objeto_remoto.procesado:
            return False
        facade_actualizacion = Facade_Actualizacion(pooler)
        if info_objeto_remoto['class'] == 'product.product':
            facade_actualizacion.actualizar_un_titulo(
                cr, uid, info_objeto_remoto.id, context=context)
        elif info_objeto_remoto['class'] == 'account.invoice':
            facade_actualizacion.actualizar_una_factura(
                cr, uid, info_objeto_remoto.id, context=context)
        elif info_objeto_remoto['class'] == 'expresso.packing':
            facade_actualizacion.actualizar_un_packing(
                cr, uid, info_objeto_remoto.id, context=context)
        else:
            return False
        return True


class sincronizacion_objeto_remoto(models.Model):

    '''
    Sincronización Objeto Remoto
    '''
    _name = 'expresso.sincronizacion_objeto_remoto'
    _description = u'Sincronización Objeto Remoto'
    _rec_name = 'info_objeto_remoto_id'
    _order = 'datetime_creation desc'

    datetime_creation = fields.Datetime(u'Fecha de creación')
    datetime = fields.Datetime(
        'Fecha de actualización')
    procesado = fields.Boolean('Procesado', default=False)
    error_al_procesar = fields.Boolean(
        'Se encontro un error al procesar el Registro', default=False)
    mensaje_error = fields.Text(u'Mensaje del error')
    info_objeto_remoto_id = fields.Many2one(
        'expresso.info_objeto_remoto',
        u'Info Objeto Remoto',
        required=True,
        ondelete='cascade')

    def create(self, cr, uid, vals, context=None):
        info_objeto_remoto_id = vals.get('info_objeto_remoto_id')
        if info_objeto_remoto_id:
            info_objeto_obj = self.pool.get('expresso.info_objeto_remoto')

            info_vals = {}
            info_vals['error_al_procesar'] = vals.get(
                'error_al_procesar', False)
            info_vals['procesado'] = vals.get('procesado', False)
            if 'datetime' in vals:
                info_vals['datetime'] = vals['datetime']

            info_objeto_obj.write(
                cr, uid, info_objeto_remoto_id, info_vals, context=context)

        return super(sincronizacion_objeto_remoto, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        info_vals = {}
        if 'procesado' in vals:
            info_vals['procesado'] = vals['procesado']
        if 'error_al_procesar' in vals:
            info_vals['error_al_procesar'] = vals['error_al_procesar']
        if 'datetime' in vals:
            info_vals['datetime'] = vals['datetime']

        if info_vals:
            info_objeto_obj = self.pool.get('expresso.info_objeto_remoto')
            info_objeto_remoto_id = vals.get('info_objeto_remoto_id', False)

            if info_objeto_remoto_id:
                info_objeto_obj.write(
                    cr, uid, info_objeto_remoto_id, info_vals, context=context)
            else:
                sinc_obj = self.pool.get(
                    'expresso.sincronizacion_objeto_remoto')
                if not isinstance(ids, list):
                    ids = [ids]
                for sincronizacion in sinc_obj.browse(cr, uid, ids, context=context):
                    info_objeto_obj.write(
                        cr, uid, sincronizacion.info_objeto_remoto_id.id, info_vals, context=context)

        return super(sincronizacion_objeto_remoto, self).write(cr, uid, ids, vals, context=context)


class expresso_sync_info(models.Model):

    # Información de Sincronización

    _name = 'expresso.sync_info'
    _description = u'Información de Sincronización'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    datetime = fields.Datetime(
        'Fecha de actualización',
        required=True, readonly=True)
    informacion = fields.Text(u'Information')

    clase = fields.Char('Class', size=50, required=True, readonly=True)


class expresso_sync_log_entry(models.Model):

    # Log de Sincronización

    _name = 'expresso.sync_log_entry'
    _description = u'Log de Sincronización'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    datetime = fields.Datetime(
        u'Fecha de actualización', required=True, readonly=True)
    error_al_procesar = fields.Boolean(
        'Error encontrado', readonly=True, default=False)
    mensaje_error = fields.Text(u'Mensaje del error', readonly=True)
    informacion = fields.Text(u'Información', readonly=True)
    objeto = fields.Selection(
        (('clientes', u'Clientes'),
         ('titulos', u'Titulos'),
         ('atributos', u'Atributos de los Titulos'),
         ('facturas', u'Facturas'),
         ('packings', u'Packings'),
         ('n_clientes', u'Clientes de Nickel'),
         ('n_facturas', u'Facturas de Nickel'),
         ('n_stock', u'Stock de Nickel'),),
        u'Objeto Actualizado', required=True, readonly=True)
