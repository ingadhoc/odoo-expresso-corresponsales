# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp import netsvc
_logger = logging.getLogger(__name__)


class product_product(models.Model):
    # Titulo de Expresso Bibliografico

    _name = 'product.product'
    _inherit = 'product.product'

    author = fields.Char('Autor', size=64, readonly=False)
    isbn = fields.Char('ISBN', size=30, readonly=False)
    editorial = fields.Char(
        'Editorial', size=64, readonly=False)
    idioma_id = fields.Many2one('expresso.idioma', 'Idioma')
    encuadernacion_id = fields.Many2one(
        'expresso.encuadernacion', 'Encuadernacion')
    coleccion_id = fields.Many2one(
        'expresso.coleccion', 'Coleccion')
    volumen = fields.Char('Volumen', size=10, readonly=False)
    numero_paginas = fields.Integer('Número de Páginas')
    anio_edicion = fields.Integer('Año de Edición')
    numero_edicion = fields.Char(
        'Número de Edición', size=10, readonly=False)
    situacion_id = fields.Many2one('expresso.situacion', 'Situacion')
    matter_id = fields.Many2one('expresso.materia', 'Materia')
    proyecto_id = fields.Many2one(
        'expresso.proyecto', 'Proyecto')
    sinopsis = fields.Text('Sinopsis')
    recomendado = fields.Boolean('Recomendado')
    edad_recomendada_min = fields.Integer('Edad Mínima Recomendada')
    edad_recomendada_max = fields.Integer('Edad Máxima Recomendada')
    imagen = fields.Binary('Imagen', filters=None)
    precio_dolares = fields.Float('Precio en Dolares')

    valor_ids = fields.Many2many(
        'expresso.valor',
        'expresso_product_valor_rel',
        'product_id', 'valor_id', 'Valores')
    seleccion_ids = fields.Many2many(
        'expresso.seleccion',
        'expresso_product_seleccion_rel',
        'product_id', 'seleccion_id', 'Selecciones')
    ciclo_id = fields.Many2one('expresso.ciclo', 'Ciclo')
    curso_id = fields.Many2one('expresso.curso', 'Curso')
    tipo_id = fields.Many2one('expresso.tipo', 'Tipo')
    publico_id = fields.Many2one(
        'expresso.publico', 'Público Objetivo')
    soporte = fields.Char('Soporte', size=50, readonly=False)
    alto = fields.Integer('Alto')
    ancho = fields.Integer('Ancho')
    espesor = fields.Integer('Espesor')
    peso = fields.Integer('Peso')
    # =d que usan las bibliotecas para identificar las temáticas de los libros
    materia_cdu = fields.Char(
        'Materia CDU', size=64, readonly=False)
    caratula = fields.Char(
        'Caratula', size=300, readonly=False)

    @api.one
    @api.onchange('matter_id')
    def onchange_product_materia(self):
        if self.matter_id:
            self.proyecto_id = self.matter_id.proyecto_id.id
        else:
            self.product_id = False


# Producto Pendiente

class product(models.Model):
    _name = 'product.producto_pendiente'
    _description = 'Título Pendiente'
    _order = 'create_date desc'

    name = fields.Char('Descripcion', size=256)
    product_id = fields.Many2one('product.product', 'Título')
    quantity = fields.Integer('Quantity')
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    order_id = fields.Many2one('sale.order', string='Pedido', required=True)
    situacion_id = fields.Many2one(
        'expresso.situacion', 'Situacion')
    notas = fields.Text('Notas')
    state = fields.Selection([
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('repedido', 'Repedido')], 'Estado', readonly=True)
    price_unit = fields.Float(
        'Unit Price',
        required=True, digits_compute=dp.get_precision('Sale Price'))

    def pendiente_a_nuevo_pedido(self, cr, uid, pendiente_id, context=None):
        '''
        Crea un nuevo pedido y llama a agregar_pendiente_a_pedido para agregar el titulo pendiente al nuevo pedido creado.
        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if isinstance(user, list):
            user = user[0]

        if not user.partner_id:
            raise Warning(_('No tiene Cliente asociado',
                            'Usted no tiene ningún Cliente asociado y por lo tanto no se puede realizar esta acción' +
                            ' por favor asignese un Cliente en el panel de administración de usuarios.'))

        partner_id = user.partner_id.id

        if isinstance(pendiente_id, list):
            pendiente_id = pendiente_id[0]

        # pricelist_id
        pricelist_id = False

        company_id = self.pool.get('res.company').search(
            cr, uid, [], context=context)
        if isinstance(company_id, list):
            company_id = company_id[0]
        if company_id:
            company = self.pool.get('res.company').browse(
                cr, uid, company_id, context=context)
            pricelist_id = company.partner_id.property_product_pricelist.id

        if not pricelist_id:
            any_pricelist_id = self.pool[
                'product.pricelist'].search(cr, uid, [], context=context)
            if isinstance(any_pricelist_id, list):
                any_pricelist_id = any_pricelist_id[0]

            if any_pricelist_id:
                pricelist_id = any_pricelist_id
            else:
                _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ninguna lista de precios ' +
                              '(product.pricelist) para asociarle.', str(remote_id))
                return
        # partner_order_id, partner_invoice_id, partner_shipping_id
        partner_order_id = False
        partner = self.pool.get('res.partner').browse(
            cr, uid, partner_id, context=context)
        partner_order_id = partner.address[0].id
        partner_invoice_id = partner_order_id
        partner_shipping_id = partner_order_id

        if not partner_order_id:
            _logger.error('Tratando de guardar un pedido [id_remoto: %s] no se encontro ningun partner_order_id ' +
                          'para asociarle.', str(remote_id))
            return

        new_data = {'partner_id': partner_id, 'pricelist_id': pricelist_id, 'partner_order_id': partner_order_id,
                    'partner_invoice_id': partner_invoice_id, 'partner_shipping_id': partner_shipping_id}
        order_id = self.pool.get('sale.order').create(cr, uid, new_data)

        return self.agregar_pendiente_a_pedido(cr, uid, order_id, pendiente_id, context=context)

    def agregar_pendiente_a_pedido(self, cr, uid, order_id, pendiente_id, context=None):
        '''
        Recibe el id del pedido (order_id) y el id del titulo pendiente (pendiente_id), agrega al pedido el titulo pendiente
        y transiciona el workflow del titulo pendiente a repedido.
        '''
        pendiente_obj = self.pool.get('product.producto_pendiente')
        pendiente = pendiente_obj.browse(
            cr, uid, pendiente_id, context=context)
        # name, notes
        product_id = False
        if pendiente.product_id:
            product_id = pendiente.product_id.id
        name = pendiente.name
        notes = False
        if pendiente.notas:
            notes = 'Notas del pedido pendiente.\n' + pendiente.notas
        # uom_id
        uom_ids = self.pool.get('product.uom').search(
            cr, uid, [('name', '=', 'PCE')], context=context)
        if not uom_ids:
            uom_id = self.pool.get('product.uom').search(
                cr, uid, [], context=context)[0]
        else:
            uom_id = uom_ids[0]

        price_unit = pendiente.price_unit

        new_values = {'product_id': product_id, 'notes': notes, 'product_uom_qty': pendiente.quantity,
                      'name': name, 'order_id': order_id, 'product_uom': uom_id, 'price_unit': price_unit}
        new_ids = self.pool.get('sale.order.line').create(cr, uid, new_values)

        # Transicionamos el Producto Pendiente de Activo a Repedido en el
        # workflow.
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(
            uid, 'product.producto_pendiente', pendiente_id, 'producto_pendiente_activo_2_repedido', cr)
        return new_ids

    def pendiente_state_activo(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'activo'})

    def pendiente_state_cancelado(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'cancelado'})

    def pendiente_state_repedido(self, cr, uid, ids):
        return self.write(cr, uid, ids, {'state': 'repedido'})
