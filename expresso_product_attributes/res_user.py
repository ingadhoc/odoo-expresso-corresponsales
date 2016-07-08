# -*- coding: utf-8 -*-
from openerp import models, fields


class users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False
    )
    customer_partner_id = fields.Many2one(
        'res.partner',
        'Client',
        help='It would be the customer wich with this user will operate'
    )
