# -*- coding: utf-8 -*-
from openerp import models, fields


class users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    remote_id = fields.Integer('Remote ID')
    # partner_id = fields.Many2one('res.partner', 'Client')

    # def copy(self, cr, uid, id, default=None, context=None):
    #     if default is None:
    #         default = {}
    #     default['remote_id'] = None
    #     return super(users, self).copy(cr, uid, id, default, context)
