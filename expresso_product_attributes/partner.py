# -*- coding: utf-8 -*-


from openerp import models, fields


class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    remote_id = fields.Integer('Remote ID')
    associated_user_ids = fields.One2many(
        'res.users', 'partner_id', 'Associate Members')
    info_corresponsal_id = fields.Many2one(
        'expresso.info_corresponsal', 'User Info')

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['remote_id'] = None
        return super(res_partner, self).copy(cr, uid, id, default, context)


# class res_partner_address(models.Model):
#     _name = 'res.partner.address'
#     _inherit = 'res.partner.address'

#     def name_get(self, cr, user, ids, context=None):
#         ret = super(res_partner_address, self).name_get(
#             cr, user, ids, context=context)
#         ret2 = []
#         for pair in ret:
#             name = pair[1]
#             if len(name) <= 40:
#                 trunc = name
#             else:
#                 trunc = ' '.join(name[:40 + 1].split(' ')[0:-1]) + '...'
#             ret2.append((pair[0], trunc))
#         return ret2
