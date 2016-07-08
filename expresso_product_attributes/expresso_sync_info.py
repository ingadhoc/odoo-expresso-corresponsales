# -*- coding: utf-8 -*-

from openerp import models, fields, api
# import datetime
from openerp import pooler
from actualizador.facade_actualizacion import Facade_Actualizacion


class expresso_info_corresponsal(models.Model):
    # Info Corresponsal

    _name = 'expresso.info_corresponsal'
    _description = u'Información de Usuario'
    _rec_name = 'corresponsal'

    corresponsal = fields.Char(
        'Corresponsale',
        size=50,
        required=True
    )
    user = fields.Char(
        'User',
        size=50,
        required=True
    )
    contrasenia = fields.Char(
        'Password',
        size=50,
        required=True
    )
    partner_ids = fields.One2many(
        'res.partner',
        'info_corresponsal_id',
        u'Partner',
        readonly=True
    )

    @api.multi
    def get_users_from_info_corresponsal(self):
        users = self.env['res.users'].search(
            [('login', 'in', self.mapped('user'))])
        return users


class info_objeto_remoto(models.Model):
    # Info Objeto Remoto

    _name = 'expresso.info_objeto_remoto'
    _description = u'Info Objeto Remoto'
    _rec_name = 'id_remoto'

    id_remoto = fields.Char(
        'Identificador Remoto',
        size=30,
        required=True,
        readonly=True,
        copy=False,
    )
    clase = fields.Char(
        'Class',
        size=50,
        required=True,
        readonly=True
    )
    corresponsal = fields.Many2one(
        'expresso.info_corresponsal',
        'Corresponsal'
    )
    sincronizacion_objeto_remoto_ids = fields.One2many(
        'expresso.sincronizacion_objeto_remoto',
        'info_objeto_remoto_id',
        'Sincronización Objeto Remoto',
        readonly=True
    )
    error_al_procesar = fields.Boolean(
        'Se encontro un error al procesar el Registro',
        readonly=True,
        default=False
    )
    procesado = fields.Boolean(
        'Procesado',
        readonly=True,
        default=False
    )
    datetime = fields.Datetime(
        'Fecha última actualización',
        readonly=True
    )
    datetime_creation = fields.Datetime(
        'Fecha de creación',
        readonly=True,
        default=fields.Datetime.now,
    )

    @api.multi
    def marcar_para_procesar(self):
        for info_objeto_remoto in self.filtered('procesado'):
            vals = {
                'datetime_creation': fields.Datetime.now(),
                'info_objeto_remoto_id': info_objeto_remoto.id
            }
            self.env['expresso.sincronizacion_objeto_remoto'].create(vals)
        return True

    @api.multi
    def procesar(self):
        self.ensure_one()
        if self.procesado:
            return False
        facade_actualizacion = Facade_Actualizacion(pooler)
        if self['clase'] == 'product.product':
            facade_actualizacion.actualizar_un_titulo(self.id)
        elif self['clase'] == 'account.invoice':
            facade_actualizacion.actualizar_una_factura(self.id)
        elif self['clase'] == 'expresso.packing':
            facade_actualizacion.actualizar_un_packing(self.id)
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

    datetime_creation = fields.Datetime(
        'Fecha de creación'
    )
    datetime = fields.Datetime(
        'Fecha de actualización'
    )
    procesado = fields.Boolean(
        'Procesado',
        default=False
    )
    error_al_procesar = fields.Boolean(
        'Se encontro un error al procesar el Registro',
        default=False
    )
    mensaje_error = fields.Text(
        'Mensaje del error'
    )
    info_objeto_remoto_id = fields.Many2one(
        'expresso.info_objeto_remoto',
        'Info Objeto Remoto',
        required=True,
        ondelete='cascade'
    )

    @api.model
    def create(self, vals):
        info_objeto_remoto_id = vals.get('info_objeto_remoto_id')
        if info_objeto_remoto_id:
            info_vals = {
                'error_al_procesar': vals.get('error_al_procesar', False),
                'procesado': vals.get('procesado', False),
            }
            if 'datetime' in vals:
                info_vals['datetime'] = vals['datetime']

            self.env['expresso.info_objeto_remoto'].browse(
                info_objeto_remoto_id).write(info_vals)

        return super(sincronizacion_objeto_remoto, self).create(vals)

    @api.multi
    def write(self, vals):
        info_vals = {}
        if 'procesado' in vals:
            info_vals['procesado'] = vals['procesado']
        if 'error_al_procesar' in vals:
            info_vals['error_al_procesar'] = vals['error_al_procesar']
        if 'datetime' in vals:
            info_vals['datetime'] = vals['datetime']

        if info_vals:
            info_objeto_remoto_id = vals.get('info_objeto_remoto_id', False)

            if info_objeto_remoto_id:
                self.env['expresso.info_objeto_remoto'].browse(
                    info_objeto_remoto_id).write(info_vals)
            else:
                for sync in self:
                    self.info_objeto_remoto_id.write(info_vals)

        return super(sincronizacion_objeto_remoto, self).write(vals)


class expresso_sync_info(models.Model):

    # Información de Sincronización

    _name = 'expresso.sync_info'
    _description = u'Información de Sincronización'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    datetime = fields.Datetime(
        'Fecha de actualización',
        required=True,
        readonly=True
    )
    informacion = fields.Text(
        'Information'
    )
    clase = fields.Char(
        'Class',
        size=50,
        required=True,
        readonly=True
    )


class expresso_sync_log_entry(models.Model):

    # Log de Sincronización

    _name = 'expresso.sync_log_entry'
    _description = u'Log de Sincronización'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    datetime = fields.Datetime(
        'Fecha de actualización',
        required=True,
        readonly=True
    )
    error_al_procesar = fields.Boolean(
        'Error encontrado',
        readonly=True,
        default=False
    )
    mensaje_error = fields.Text(
        'Mensaje del error',
        readonly=True
    )
    informacion = fields.Text(
        'Información',
        readonly=True
    )
    objeto = fields.Selection(
        [('clientes', 'Clientes'),
         ('titulos', 'Titulos'),
         ('atributos', 'Atributos de los Titulos'),
         ('facturas', 'Facturas'),
         ('packings', 'Packings'),
         ('n_clientes', 'Clientes de Nickel'),
         ('n_facturas', 'Facturas de Nickel'),
         ('n_stock', 'Stock de Nickel')],
        'Objeto Actualizado',
        required=True,
        readonly=True
    )
