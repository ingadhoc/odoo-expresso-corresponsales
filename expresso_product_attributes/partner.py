# -*- coding: utf-8 -*-


from openerp import models, fields


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False
    )
    associated_user_ids = fields.One2many(
        'res.users',
        'partner_id',
        'Associate Members'
    )
    info_corresponsal_id = fields.Many2one(
        'expresso.info_corresponsal',
        'User Info'
    )
