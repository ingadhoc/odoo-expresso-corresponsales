# -*- coding: utf-8 -*-

from openerp import models, fields


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'
    _order = 'date_invoice desc'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False,
    )
    departure = fields.Char(
        'Departure',
        size=50
    )
    aduana = fields.Char(
        'Aduana',
        size=50
    )
    bultos = fields.Integer(
        'Número de bultos'
    )
    net_weight = fields.Float(
        'Net Weight'
    )
    gross_weight = fields.Float(
        'Gross Weight'
    )
    origin = fields.Char(
        'Origin',
        size=50
    )
    samples = fields.Boolean(
        'Samples'
    )
    invoice_number = fields.Char(
        'Invoice Number',
        size=50
    )
    packing_id = fields.Many2one(
        'expresso.packing',
        'Packing'
    )


class account_invoice_line(models.Model):
    _name = "account.invoice.line"
    _inherit = 'account.invoice.line'

    remote_id = fields.Integer(
        'Remote ID',
        copy=False,
    )
