# -*- coding: utf-8 -*-


from openerp import models, fields


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False
    )
    # TODO ver si borramos este campo y en realidad usamos el padre
    info_corresponsal_id = fields.Many2one(
        'expresso.info_corresponsal',
        'User Info'
    )
