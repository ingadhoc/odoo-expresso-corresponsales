# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class expresso_generador_productos_pendientes(models.TransientModel):

    _name = "expresso.generador_productos_pendientes"
    _description = "Generar Títulos Pendientes."

    cantidad_disponible = fields.Integer('Cantidad Disponible')
    situacion_id = fields.Many2one(
        'expresso.situacion', 'Situacion', required=True)
    notas = fields.Text('Notas')

    def controlar_generacion_de_pendiente(self, cr, uid, ids, linea, context=None):
        if linea.order_id.state_expresso == 'despachado':
            raise Warning(_('No puede modificar el pedido'))
        if linea.order_id.state_expresso == 'recibido':
            raise Warning(_('No se pueden eliminar Titulos del pedido cuando este esta en el estado %s.' % (
                linea.order_id.state_expresso)))

    @api.one
    def linea_parcial_a_pendientes(self):
        if 'active_id' not in self._context:
            return False

        # cantidad_disponible = self.browse(cr, uid, ids)[0].cantidad_disponible
        if not self.cantidad_disponible:
            return {'type': 'ir.actions.act_window_close'}

        self._context['desde_wizard_pendiente'] = True

        linea = self.env['sale.order.line'].browse(self._context['active_id'])

        self.controlar_generacion_de_pendiente(linea)

        if self.cantidad_disponible > linea.product_uom_qty:
            raise Warning(_('Cantidad disponible muy grande',
                            'La cantidad disponible no peude ser mayor a la cantidad pedida.'))
        elif self.cantidad_disponible < 0:
            raise Warning(_('Cantidad disponible negativa',
                            'La cantidad disponible no peude ser negativa.'))

        name = linea.name
        # product_id
        product_id = False
        if linea.product_id:
            product_id = linea.product_id.id

        # price_unit
        price_unit = linea.price_unit

        # cantidad
        cantidad = linea.product_uom_qty - self.cantidad_disponible

        # partner_id
        partner_id = linea.order_id.partner_id.id

        # order_id
        order_id = linea.order_id.id
        # situacion_id, notas
        # situacion_id = self.browse(cr, uid, ids)[0].situacion_id.id
        # notas = self.browse(cr, uid, ids)[0].notas

        values = {'name': name, 'product_id': product_id,
                  'cantidad': cantidad, 'partner_id': partner_id,
                  'order_id': order_id, 'situacion_id': self.situacion_id.id,
                  'notas': self.notas, 'price_unit': price_unit}
        self.pool.get('product.producto_pendiente').create(values)

        self.env['sale.order.line'].write(
            [linea.id], {'product_uom_qty': self.cantidad_disponible})
        return {'type': 'ir.actions.act_window_close'}

    @api.one
    def linea_entera_a_pendientes(self):
        if 'active_id' not in self._context:
            return False

        self._context['desde_wizard_pendiente'] = True

        linea = self.pool.get('sale.order.line').browse(
            self._context['active_id'])
        self.controlar_generacion_de_pendiente(linea)

        name = linea.name
        # product_id
        product_id = False
        if linea.product_id:
            product_id = linea.product_id.id

        # price_unit
        price_unit = linea.price_unit

        # cantidad
        cantidad = linea.product_uom_qty

        # partner_id
        partner_id = linea.order_id.partner_id.id

        # order_id
        order_id = linea.order_id.id
        values = {'name': name, 'product_id': product_id,
                  'cantidad': cantidad, 'partner_id': partner_id,
                  'order_id': order_id, 'situacion_id': self.situacion_id.id,
                  'notas': self.notas, 'price_unit': price_unit}
        self.env['product.producto_pendiente'].create(
            values)

        self.pool.get('sale.order').write(
            [order_id], {'order_line': [(2, linea.id)]})
        return {'type': 'ir.actions.act_window_close'}
