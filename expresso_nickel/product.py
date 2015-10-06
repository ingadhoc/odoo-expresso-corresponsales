# -*- coding: utf-8 -*-

import logging
from openerp import models, fields

_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    qty_available_2 = fields.Float(
        related='qty_available',
        string="Quantity Available 2")
