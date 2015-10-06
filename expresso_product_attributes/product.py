# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class product_product(models.Model):
    # Titulo de Expresso Bibliografico

    _name = 'product.product'
    _inherit = 'product.product'

    default_code = fields.Char(
        string='EAN'
        )
    autor = fields.Char(
        'Autor',
        size=64,
        readonly=False
        )
    isbn = fields.Char(
        'ISBN',
        size=30,
        readonly=False
        )
    editorial = fields.Char(
        'Editorial',
        size=64,
        readonly=False
        )
    idioma_id = fields.Many2one(
        'expresso.idioma',
        'Idioma'
        )
    encuadernacion_id = fields.Many2one(
        'expresso.encuadernacion',
        'Encuadernacion'
        )
    coleccion_id = fields.Many2one(
        'expresso.coleccion',
        'Coleccion'
        )
    volumen = fields.Char(
        'Volumen',
        size=10,
        readonly=False
        )
    numero_paginas = fields.Integer(
        'Número de Páginas'
        )
    anio_edicion = fields.Integer(
        'Año de Edición'
        )
    numero_edicion = fields.Char(
        'Número de Edición',
        size=10,
        readonly=False
        )
    situacion_id = fields.Many2one(
        'expresso.situacion',
        'Situacion'
        )
    matter_id = fields.Many2one(
        'expresso.materia',
        'Materia'
        )
    proyecto_id = fields.Many2one(
        'expresso.proyecto',
        'Proyecto'
        )
    sinopsis = fields.Text(
        'Sinopsis'
        )
    recomendado = fields.Boolean(
        'Recomendado'
        )
    edad_recomendada_min = fields.Integer(
        'Edad Mínima Recomendada'
        )
    edad_recomendada_max = fields.Integer(
        'Edad Máxima Recomendada'
        )
    imagen = fields.Binary(
        'Imagen',
        filters=None
        )
    precio_dolares = fields.Float(
        'Precio en Dolares'
        )
    valor_ids = fields.Many2many(
        'expresso.valor',
        'expresso_product_valor_rel',
        'product_id',
        'valor_id',
        'Valores',
        )
    seleccion_ids = fields.Many2many(
        'expresso.seleccion',
        'expresso_product_seleccion_rel',
        'product_id',
        'seleccion_id',
        'Selecciones'
        )
    ciclo_id = fields.Many2one(
        'expresso.ciclo',
        'Ciclo'
        )
    curso_id = fields.Many2one(
        'expresso.curso',
        'Curso'
        )
    tipo_id = fields.Many2one(
        'expresso.tipo',
        'Tipo'
        )
    publico_id = fields.Many2one(
        'expresso.publico',
        'Público Objetivo'
        )
    soporte = fields.Char(
        'Soporte',
        size=50,
        readonly=False
        )
    alto = fields.Integer(
        'Alto'
        )
    ancho = fields.Integer(
        'Ancho'
        )
    espesor = fields.Integer(
        'Espesor'
        )
    peso = fields.Integer(
        'Peso'
        )
    # =d que usan las bibliotecas para identificar las temáticas de los libros
    materia_cdu = fields.Char(
        'Materia CDU',
        size=64,
        readonly=False
        )
    caratula = fields.Char(
        'Caratula',
        size=300,
        readonly=False
        )

    @api.one
    @api.onchange('matter_id')
    def onchange_product_materia(self):
        self.proyecto_id = self.matter_id.proyecto_id.id


class product(models.Model):
    _name = 'product.producto_pendiente'
    _description = 'Título Pendiente'
    _order = 'create_date desc'

    name = fields.Char(
        'Descripcion',
        size=256
        )
    product_id = fields.Many2one(
        'product.product',
        'Título'
        )
    quantity = fields.Integer(
        'Quantity'
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Cliente',
        required=True
        )
    order_id = fields.Many2one(
        'sale.order',
        string='Pedido',
        required=True
        )
    situacion_id = fields.Many2one(
        'expresso.situacion',
        'Situacion'
        )
    notas = fields.Text(
        'Notas'
        )
    state = fields.Selection([
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('repedido', 'Repedido')],
        'Estado',
        readonly=True
        )
    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits=dp.get_precision('Sale Price')
        )

    @api.multi
    def pendiente_a_nuevo_pedido(self):
        '''
        Crea un nuevo pedido y llama a agregar_pendiente_a_pedido para agregar
        el titulo pendiente al nuevo pedido creado.
        '''
        self.ensure_one()
        partner = self.env.user.partner_id

        if not partner:
            raise Warning(
                'No tiene Cliente asociado!\n',
                'Usted no tiene ningún Cliente asociado y por lo tanto no se '
                'puede realizar esta acción, por favor asignese un Cliente en '
                'el panel de administración de usuarios.')

        # company = self.env.user.company_id
        # pricelist = company.partner_id.property_product_pricelist
        pricelist = partner.property_product_pricelist

        if not pricelist:
            raise Warning('No se encontro ninguna lista  de precios')

        # partner_order_id, partner_invoice_id, partner_shipping_id
        # partner_order_id = False
        # partner_order_id = partner.address[0].id
        # partner_invoice_id = partner_order_id
        # partner_shipping_id = partner_order_id

        vals = {
            'partner_id': partner.id,
            'pricelist_id': pricelist.id,
            # 'partner_order_id': partner.id,
            # 'partner_invoice_id': partner_invoice_id,
            # 'partner_shipping_id': partner_shipping_id
            }
        order = self.env['sale.order'].create(vals)
        return self.agregar_pendiente_a_pedido(order)

    def agregar_pendiente_a_pedido(self, order):
        '''
        Recibe el id del pedido (order_id) y el id del titulo pendiente
        (pendiente_id), agrega al pedido el titulo pendiente
        y transiciona el workflow del titulo pendiente a repedido.
        '''
        self.ensure_one()

        # uom_id
        uom = self.env['product.uom'].search([('name', '=', 'PCE')], limit=1)
        if not uom:
            uom = self.env['product.uom'].search([], limit=1)

        price_unit = self.price_unit

        vals = {
            'product_id': self.product_id and self.product_id.id or False,
            'notes': (
                self.notas and
                'Notas del pedido pendiente.\n' + self.notas or False),
            'product_uom_qty': self.quantity,
            'name': self.name,
            'order_id': order.id,
            'product_uom': uom.id,
            'price_unit': price_unit
            }

        lines = self.env['sale.order.line'].create(vals)

        self.action_pendiente_state_repedido()
        return lines

    @api.multi
    def action_action_pendiente_state_repedido(self):
        return self.write({'state': 'activo'})

    @api.multi
    def action_pendiente_state_cancelado(self):
        return self.write({'state': 'cancelado'})

    @api.multi
    def action_pendiente_state_repedido(self):
        return self.write({'state': 'repedido'})
