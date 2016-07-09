# -*- coding: utf-8 -*-
from openerp import models, fields


class expresso_info_corresponsal(models.Model):
    _name = 'expresso.info_corresponsal'
    _inherit = 'expresso.info_corresponsal'

    nickel_customer_id = fields.Many2one(
        'nickel_partner',
        'Cliente de Nickel'
    )


class nickel_partner(models.Model):

    # Cliente obtenido desde la base de datos de Nickel
    _name = 'nickel_partner'
    _description = 'Nickel Partner'

    remote_id = fields.Char(
        'Remote ID',
        size=30,
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        'Name',
        size=100,
        required=True,
        readonly=True
    )
    country_code = fields.Char(
        'Country Code',
        size=10,
        readonly=True
    )
    booleano = fields.Char(
        'Name',
        size=100,
        required=True,
        readonly=True
    )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'The Remote ID must be unique!')]
