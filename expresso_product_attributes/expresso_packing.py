# -*- coding: utf-8 -*-

from openerp import models, fields
import openerp.addons.decimal_precision as dp


class expresso_packing(models.Model):
    _name = 'expresso.packing'
    _description = 'Packing'
    _rec_name = 'id_remoto'

    id_remoto = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False,
        )
    date = fields.Datetime(
        'Fecha Orden',
        required=True,
        help='Fecha de la Orden'
        )
    number_of_packages = fields.Integer(
        'Numero de paquetes'
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Corresponsal',
        required=True
        )
    partner_address_id = fields.Many2one(
        'payment.transaction',
        'Address',
        required=True,
        domain="[('partner_id','=', partner_id)]"
        )
    imprimirpeso = fields.Char(
        'Imprimir Peso',
        size=30
        )
    packing_box_ids = fields.One2many(
        'expresso.packing.box',
        'packing_id',
        'Cajas'
        )
    invoice_ids = fields.One2many(
        'account.invoice',
        'packing_id',
        'Facturas'
        )


class expresso_packing_box(models.Model):
    _name = 'expresso.packing.box'
    _description = 'Cajas de Packing'

    name = fields.Char(
        'Nombre',
        size=64,
        copy=False
        )
    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True
        )
    weight = fields.Float(
        'Peso'
        )
    packing_id = fields.Many2one(
        'expresso.packing',
        'Packing',
        required=True
        )
    packing_detail_ids = fields.One2many(
        'expresso.packing.detail',
        'box_id',
        'Detalles'
        )


class expresso_packing_detail(models.Model):
    _name = 'expresso.packing.detail'
    _description = 'Detalle de Packing'

    name = fields.Char(
        'Nombre',
        size=64
        )
    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False,
        )
    product_id = fields.Many2one(
        'product.product',
        'Producto'
        )
    product_qty = fields.Float(
        'Cantidad',
        digits=dp.get_precision('Product UoM'),
        required=True
        )
    weight = fields.Float(
        'Peso'
        )
    box_id = fields.Many2one(
        'expresso.packing.box',
        'Caja',
        required=True
        )
