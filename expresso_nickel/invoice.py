# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'

    @api.one
    def _next_expiration_date(self):
        nickel_next_bill = False
        for nickel_invoice in self.nickel_invoice_ids:
            if not nickel_invoice.paid:
                if not nickel_next_bill:
                    nickel_next_bill = nickel_invoice
                elif nickel_next_bill.expiration_date > nickel_invoice.expiration_date:
                    nickel_next_bill = nickel_invoice

        if nickel_next_bill:
            self.expiration_date = nickel_next_bill.fecha_vencimiento
        else:
            self.expiration_date = False

    nickel_invoice_ids = fields.One2many(
        'nickel_invoice',
        'invoice_id',
        'Nickel Invoice')
    residual_2 = fields.Float(
        'Residual',
        digits_compute=dp.get_precision('Account'),
        help="Importe restante a pagar.")
    paid = fields.Boolean(
        'Paid',
        help='Indica si la factura ha sido pagada.',
        default=False)
    expiration_date = fields.Date(
        string='Expiration Date',
        compute='_next_expiration_date',
        help="Fecha del proximo vencimiento.")
