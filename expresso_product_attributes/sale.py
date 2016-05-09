# -*- coding: utf-8 -*-
from openerp import models, fields, api
import logging
from openerp import pooler
from openerp.exceptions import Warning
from actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)


class sale_empresa_logistica(models.Model):

    _name = 'sale.empresa_logistica'
    _description = 'Empresa de Lógistica'
    _rec_name = 'name'

    name = fields.Char(
        'Nombre',
        size=100,
        required=True,
        readonly=False
        )
    _sql_constraints = [
        ('name_no_uniq', 'unique(name)', 'El nombre debe ser unico!')]


# Wizard para preguntar si queremos cerrar o no el pedido.
class pre_cerrar_pedido(models.TransientModel):
    _name = "pre_cerrar_pedido"
    _description = "Pre cerrar pedido"

    @api.multi
    def cerrar_pedido(self):
        self.signal_workflow('order_pedido_2_cerrado')
        return {'type': 'ir.actions.act_window_close'}


class sale_order(models.Model):
    _inherit = 'sale.order'
    # We change the order for name desc to id desc because SO1xxx is ordered
    # after SOxxx
    # TODO remove this, it gives an error on portal_sale update
    # _order = 'id desc'

    @api.model
    def get_user_corresponsal(self):
        user = self.env.user
        if self.user_in_group_with_name(user, "Expresso / Corresponsales"):
            return user
        else:
            return False

    @api.model
    def get_user_expresso(self):
        user = self.env.user
        if self.user_in_group_with_name(user, "Expresso / Corresponsales"):
            if user.customer_partner_id and user.customer_partner_id.user_id:
                return user.customer_partner_id.user_id
        return False

    remote_id = fields.Char(
        'Remote ID',
        size=126,
        copy=False
        )
    fecha_confirmado_corresponsal = fields.Datetime(
        'Date Confirm - Correspondent'
        )
    fecha_valido_expresso = fields.Datetime(
        'Valid Date - Expresso'
        )
    fecha_valido_corresponsal = fields.Datetime(
        'Valid Date - Correspondent'
        )
    fecha_cerrado_expresso = fields.Datetime(
        'Date Closed - Expresso'
        )
    fecha_despachado_expresso = fields.Datetime(
        'Dispatched Date - Expresso'
        )
    fecha_recibido_corresponsal = fields.Datetime(
        'Date Received - Correspondent'
        )
    # Campos para Expresso
    fecha_salida = fields.Date(
        'Fecha de Salida',
        help="Fecha en la que se estima que el pedido va a estar listo"
        )
    forma_envio_id_expresso = fields.Many2one(
        'expresso.forma_envio',
        'Forma de Envío'
        )
    fecha_estimada_entrega = fields.Date(
        'Fecha Estimada de Entrega'
        )
    embarque = fields.Char(
        'Embarque',
        size=100
        )
    empresa_logistica_id = fields.Many2one(
        'sale.empresa_logistica',
        'Empresa de Logística'
        )
    # copias readonly o para vista para corresponsaes
    fecha_salida_corresponsales = fields.Date(
        related='fecha_salida',
        )
    fecha_estimada_entrega_corresponsales = fields.Date(
        related='fecha_estimada_entrega',
        )
    embarque_corresponsales = fields.Char(
        related='embarque',
        )
    empresa_logistica_id_corresponsales = fields.Many2one(
        related="empresa_logistica_id",
        )
    user_expresso_id_corresponsal = fields.Many2one(
        related='user_expresso_id_expresso',
        )
    # otros campos corresponsales
    forma_envio_id_corresponsales = fields.Many2one(
        'expresso.forma_envio',
        'Forma de Envío'
        )
    state_expresso = fields.Selection([
        ('borrador', 'Borrador'),
        ('pendiente_e', 'Pendiente Expresso'),
        ('pendiente_c', 'Pendiente Corresponsal'),
        ('pedido', 'Pedido'),
        ('cerrado', 'Cerrado'),
        ('despachado', 'Despachado'),
        ('recibido', 'Recibido')],
        'Estado',
        readonly=True
        )
    producto_pendiente_ids = fields.One2many(
        'product.producto_pendiente',
        'order_id',
        'Títulos Pendientes'
        )
    current_partner_id_for_filtering = fields.Many2one(
        'res.partner',
        'Current Partner id for Filtering',
        default=lambda self: self.env.user.customer_partner_id,
        )
    user_corresponsal_id_corresponsales = fields.Many2one(
        'res.users',
        'Usuario Corresponsal',
        required=True,
        domain="[('partner_id', '=', current_partner_id_for_filtering)]",
        )
    user_corresponsal_id_expresso = fields.Many2one(
        'res.users',
        'Usuario Corresponsal',
        required=True,
        # TODO habilitar este default que me da error al instalar y entender
        # estos campos "user bla bla bla"
        default=get_user_corresponsal,
        )
    user_expresso_id_expresso = fields.Many2one(
        'res.users',
        'Usuario Expresso',
        # TODO habilitar
        default=get_user_expresso,
        )
    invoice_ids = fields.Many2many(
        'account.invoice',
        'expresso_order_invoice_rel',
        'order_id',
        'invoice_id',
        'Facturas'
        )
    partner_id = fields.Many2one(
        default=lambda self: self.env.user.customer_partner_id
        )
    property_product_pricelist = fields.Many2one(
        default=lambda self: (
            self.env.user.customer_partner_id.property_product_pricelist)
        )

    # TODO entender porque estos dos onchange
    @api.one
    @api.onchange('user_corresponsal_id_corresponsales')
    def onchange_user_corresponsal_id_corresponsales(self):
        self.user_corresponsal_id_expresso = (
            self.user_corresponsal_id_corresponsales)

    @api.one
    @api.onchange('user_corresponsal_id_expresso')
    def onchange_user_corresponsal_id_expresso(self):
        self.user_corresponsal_id_corresponsales = (
            self.user_corresponsal_id_expresso)

    # def write(self, cr, uid, ids, vals, context=None):
    #     if not isinstance(ids, list):
    #         ids = [ids]
        
    #     user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        
    #     fecha_del_workflow = ['fecha_confirmado_corresponsal', 'fecha_valido_expresso', 'fecha_valido_corresponsal',
    #                                   'fecha_cerrado_expresso', 'fecha_despachado_expresso', 'fecha_recibido_corresponsal']
    #     campos_no_controlados = set(['remote_id', 'note', 'state_expresso', 'invoice_ids', 'product_warning'] + fecha_del_workflow)
        
    #     campos_editables_cuando_cerrado = ['order_message_ids', 'embarque', 'empresa_logistica_id', 'remote_id']
        
    #     if 'producto_pendiente_ids' in vals:
    #         if not vals['producto_pendiente_ids']:
    #             campos_no_controlados.add('producto_pendiente_ids')
    #     if 'order_line' in vals:
    #         if not vals['order_line']:
    #             campos_no_controlados.add('order_line')
        
    #     campos_modificados = set(vals.keys())
    #     campos_a_controlar = campos_modificados.difference(campos_no_controlados)
        
    #     #if len(campos_a_controlar) == 0:
    #     #    return super(sale_order, self).write(cr, uid, ids, vals, context=context)
    #     # Pre control
    #     if len(campos_a_controlar) != 0:
    #         for order in self.browse(cr, uid, ids, context=context):
    #             if order.state_expresso:
    #                 # Si el pedido no esta más en borrador, la forma de envio debe estar completada
    #                 if order.state_expresso != 'borrador':
    #                     if 'forma_envio_id_corresponsales' in vals and not vals['forma_envio_id_corresponsales']:
    #                         raise Warning(_('Forma de Envio',
    #                                              'No se puede dejar vacia la forma de envío en este estado.'))
    #                     if 'forma_envio_id_expresso' in vals and not vals['forma_envio_id_expresso']:
    #                         raise Warning(_('Forma de Envio',
    #                                              'No se puede dejar vacia la forma de envío en este estado.'))
                    
                    
    #                 estados_expresso_corresponsales = ['borrador', 'pendiente_e', 'pendiente_c']
    #                 estados_expresso = ['pedido']
                    
    #                 if order.state_expresso in estados_expresso_corresponsales:
    #                     continue
                    
    #                 elif order.state_expresso in estados_expresso:
    #                     if not self.user_in_group_with_name(user, "Expresso / Expresso"):
    #                         if order.state_expresso == 'borrador':
    #                             estado = 'Borrador'
    #                         elif order.state_expresso == 'pendiente_e':
    #                             estado = 'Pendiente Expresso'
    #                         else:
    #                             estado = "Pendiente Corresponsal"
    #                         raise Warning(_('No puede modificar el pedido', 'Solo usuarios del grupo %s puede modificar una orden en el estado %s.' % ( estado)))
    #                 elif order.state_expresso == 'cerrado':
    #                     no_editables_cuando_cerrado = campos_a_controlar.difference(campos_editables_cuando_cerrado)
    #                     if no_editables_cuando_cerrado:
    #                         raise Warning(_('Imposible modificar', 'No se puede modificar la información del pedido de venta en este estado.'))
    #                 else:
    #                     raise Warning(_('Imposible modificar', 'No se puede modificar la información del pedido de venta en este estado.'))
    #     # Ejecutamos el write
    #     vals = self.procesar_valores(vals, context=context)
    #     ret = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        
    #     # Post procesamiento
    #     for order in self.browse(cr, uid, ids, context=context):
    #         if len(campos_a_controlar) == 0:
    #             continue
            
    #         if order.state_expresso:
    #             if order.state_expresso == 'pendiente_e':
    #                 if not self.user_in_group_with_name(user, "Expresso / Expresso"):
    #                     wf_service = netsvc.LocalService("workflow")
    #                     wf_service.trg_validate(uid, 'sale.order', order.id, 'order_pendiente_expresso_2_borrador', cr)
    #             elif order.state_expresso == 'pendiente_c':
    #                 if not self.user_in_group_with_name(user, "Expresso / Expresso"):
    #                     wf_service = netsvc.LocalService("workflow")
    #                     wf_service.trg_validate(uid, 'sale.order', order.id, 'order_pendiente_corresponsales_2_borrador', cr)
    #     return ret

    @api.model
    def create(self, vals):
        new_vals = self.procesar_valores(vals)
        return super(sale_order, self).create(new_vals)

    # TODO ver porque esta cosa horrible
    @api.model
    def procesar_valores(self, vals):
        # Sincronizamos forma_envio_id_expresso y forma_envio_id_corresponsales
        if 'forma_envio_id_expresso' in vals and vals['forma_envio_id_expresso']:
            if 'forma_envio_id_corresponsales' not in vals or not vals['forma_envio_id_corresponsales']:
                vals['forma_envio_id_corresponsales'] = vals['forma_envio_id_expresso']
        elif 'forma_envio_id_corresponsales' in vals and vals['forma_envio_id_corresponsales']:
            if 'forma_envio_id_expresso' not in vals or not vals['forma_envio_id_expresso']:
                vals['forma_envio_id_expresso'] = vals['forma_envio_id_corresponsales']

        # Sincronizamos user_corresponsal_id_expresso y user_corresponsal_id_corresponsales
        if 'user_corresponsal_id_expresso' in vals and vals['user_corresponsal_id_expresso']:
            if 'user_corresponsal_id_corresponsales' not in vals or not vals['user_corresponsal_id_corresponsales']:
                vals['user_corresponsal_id_corresponsales'] = vals['user_corresponsal_id_expresso']
        elif 'user_corresponsal_id_corresponsales' in vals and vals['user_corresponsal_id_corresponsales']:
            if 'user_corresponsal_id_expresso' not in vals or not vals['user_corresponsal_id_expresso']:
                vals['user_corresponsal_id_expresso'] = vals['user_corresponsal_id_corresponsales']
        return vals

    # Cambios de estado
    @api.multi
    def order_state_borrador(self):
        vals = {
            'fecha_confirmado_corresponsal': False,
            'fecha_valido_expresso': False,
            'fecha_valido_corresponsal': False,
            'fecha_cerrado_expresso': False,
            'fecha_despachado_expresso': False,
            'fecha_recibido_corresponsal': False,
            'state_expresso': 'borrador',
        }
        self.write(vals)
        return True

    @api.multi
    def order_state_hacia_borrador(self):
        return True

    @api.multi
    def order_state_pendiente_expresso(self):
        now = fields.Datetime.now()

        for order in self:
            if not order.forma_envio_id_corresponsales:
                raise Warning(
                    'Forma de Envío incompleta!\n'
                    'Para confirmar el pedido debe completar el campo Forma de'
                    ' Envío')

        vals = {
            'fecha_confirmado_corresponsal': now,
            'fecha_valido_expresso': False,
            'fecha_valido_corresponsal': False,
            'fecha_cerrado_expresso': False,
            'fecha_despachado_expresso': False,
            'fecha_recibido_corresponsal': False,
            'state_expresso': 'pendiente_e',
        }
        self.write(vals)
        return True

    @api.multi
    def order_state_pendiente_corresponsal(self):
        now = fields.Datetime.now()
        for order in self():
            if not order.fecha_salida:
                raise Warning(
                    'Fecha de Salida incompleta!\n'
                    'Para confirmar el pedido debe completar el campo Fecha '
                    'de Salida')
            if not order.fecha_estimada_entrega:
                raise Warning(
                    'Fecha Estimada de Entrega incompleta!\n'
                    'Para confirmar el pedido debe completar el campo Fecha '
                    'Estimada de Entrega')
        vals = {
            'fecha_valido_expresso': now,
            'fecha_valido_corresponsal': False,
            'fecha_cerrado_expresso': False,
            'fecha_despachado_expresso': False,
            'fecha_recibido_corresponsal': False,
            'state_expresso': 'pendiente_c',
        }
        self.write(vals)
        return True

    @api.multi
    def order_state_pedido(self):
        now = fields.Datetime.now()
        vals = {
            'fecha_valido_corresponsal': now,
            'fecha_cerrado_expresso': False,
            'fecha_despachado_expresso': False,
            'fecha_recibido_corresponsal': 'pedido',
        }
        self.write(vals)
        return True

    @api.multi
    def order_state_cerrado(self):
        now = fields.Datetime.now()
        vals = {
            'fecha_cerrado_expresso': now,
            'fecha_despachado_expresso': False,
            'fecha_recibido_corresponsal': 'pedido',
        }
        self.write(vals)
        self.crear_pedido_remoto()
        return True

    @api.multi
    def order_state_despachado(self):
        now = fields.Datetime.now()
        for order in self:
            if not order.empresa_logistica_id:
                raise Warning(
                    'Empresa Lógistica incompleta!\n'
                    'Para despachar el pedido debe completar el campo Empresa '
                    'Lógistica')
        vals = {
            'fecha_despachado_expresso': now,
            'fecha_recibido_corresponsal': False,
            'state_expresso': 'despachado',
        }
        self.write(vals)
        return True

    @api.multi
    def order_state_recibido(self):
        now = fields.Datetime.now()
        vals = {
            'fecha_recibido_corresponsal': now,
            'state_expresso': 'recibido',
        }
        self.write(vals)
        return True

    @api.model
    def user_in_group_with_name(self, user, group_name):
        for group in user.groups_id:
            if group.name.lower() == group_name.lower():
                return True
        return False

    @api.model
    def crear_pedido_remoto(self):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.crear_pedido_remoto()


class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    @api.model
    def get_default_uom(self):
        uom = self.env['product.uom'].search([('name', '=', 'PCE')], limit=1)
        if not uom:
            uom = uom.search([], limit=1)
        return uom

    remote_id = fields.Char(
        'Remote ID',
        size=126,
        copy=False,
        )
    price_unit_corresponsales = fields.Float(
        related='price_unit',
        string="Precio unidad",
        store=False
        )
    product_uom = fields.Many2one(
        default=get_default_uom,
        )

    @api.multi
    def product_id_change_inherited(
            self, pricelist, product, partner_id=False,
            product_uom_qty=1):
        super_result = super(sale_order_line, self).product_id_change(
            pricelist, product, partner_id=partner_id)
        result = {}
        if 'value' in super_result:
            if 'name' in super_result['value']:
                result['name'] = super_result['value']['name']
            if 'price_unit' in super_result['value']:
                result['price_unit'] = super_result['value']['price_unit']
                result['price_unit_corresponsales'] = result['price_unit']
        return {'value': result}
