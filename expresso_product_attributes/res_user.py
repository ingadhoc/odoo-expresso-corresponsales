# -*- coding: utf-8 -*-
from openerp import models, fields


class users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False
    )
