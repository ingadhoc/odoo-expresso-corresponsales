# -*- coding: utf-8 -*-
from openerp import models, fields


class expresso_info_corresponsal(models.Model):
    _name = 'expresso.info_corresponsal'
    _inherit = 'expresso.info_corresponsal'

    nickel_customer_id = fields.Many2one(
        'nickel_partner',
        'Cliente de Nickel')


class nickel_partner(models.Model):

    # Cliente obtenido desde la base de datos de Nickel
    _name = 'nickel_partner'
    _description = 'Nickel Partner'

    remote_id = fields.Char(
        'Remote ID',
        size=30,
        readonly=True)
    name = fields.Char(
        'Name',
        size=100,
        required=True,
        readonly=True)
    country_code = fields.Char(
        'Country Code',
        size=10,
        readonly=True)
    booleano = fields.Char(
        'Name',
        size=100,
        required=True,
        readonly=True)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['remote_id'] = None
        return super(nickel_partner, self).copy(cr, uid, id, default, context)

    def get_user_desde_id_remoto(self, cr, uid, remote_id, context=None):
        nickel_obj = self.pool.get('nickel_partner')
        id_nickel = nickel_obj.search(
            cr, uid, [('remote_id', '=', remote_id)], context=context)
        if not id_nickel:
            return None
        if isinstance(id_nickel, list):
            id_nickel = id_nickel[0]

        info_corresponsal_obj = self.pool.get('expresso.info_corresponsal')
        id_info_corresponsal = info_corresponsal_obj.search(
            cr, uid, [('nickel_customer_id', '=', id_nickel)], context=context)
        user_id = info_corresponsal_obj.get_users_from_info_corresponsal(
            cr, uid, id_info_corresponsal, context=context)

        if not user_id:
            return None
        if isinstance(user_id, list):
            user_id = user_id[0]
        return user_id

    def get_partner_from_remote_id(self, cr, uid, remote_id, context=None):
        user_id = self.get_user_desde_id_remoto(
            cr, uid, remote_id, context=context)
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, user_id, context=context)
        if not user:
            return None
        if isinstance(user, list):
            user = user[0]

        return user.partner_id.id

    _sql_constraints = [
        ('remote_id_no_uniq', 'unique(remote_id)', 'The Remote ID must be unique!')]
