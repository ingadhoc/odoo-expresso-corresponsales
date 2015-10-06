# -*- coding: utf-8 -*-

from openerp import models, fields, api


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'
    _order = 'date_invoice desc'

    remote_id = fields.Integer('Remote ID')
    departure = fields.Char('Departure', size=50)
    aduana = fields.Char('Aduana', size=50)
    bultos = fields.Integer('Número de bultos')
    net_weight = fields.Float('Net Weight')
    gross_weight = fields.Float('Gross Weight')
    origin = fields.Char('Origin', size=50)
    samples = fields.Boolean('Samples')
    invoice_number = fields.Char('Invoice Number', size=50)
    packing_id = fields.Many2one('expresso.packing', 'Packing')

    # TODO: Ver que hacemos con esto
    invoice_type = fields.Char('Invoice Type', size=100, required=False)

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        default['remote_id'] = None
        return super(account_invoice, self).copy(default)


class account_invoice_line(models.Model):
    _name = "account.invoice.line"
    _inherit = 'account.invoice.line'

    remote_id = fields.Integer('Remote ID')

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['remote_id'] = None
        return super(account_invoice_line, self).copy(cr, uid, id, default, context)
