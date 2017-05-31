# -*- coding: utf-8 -*-

import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)


class expresso_info_corresponsal(models.Model):
    _name = 'expresso.info_corresponsal'
    _inherit = 'expresso.info_corresponsal'

    nickel_customer_id = fields.Many2one(
        'nickel_partner',
        'Nickel Client'
    )
