# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import logging
import datetime
import netsvc
import pooler

from actualizador.facade_actualizacion import Facade_Actualizacion

_logger = logging.getLogger(__name__)

# Empresa de Lógistica
class sale_empresa_logistica(osv.osv):
    '''
    '''
    _name = 'sale.empresa_logistica'
    _description = u'Empresa de Lógistica'
    _rec_name = 'name'
	
    _columns = {
        'name': fields.char('Nombre', size=100, required=True, readonly=False),
    }
    
    _sql_constraints = [('name_no_uniq','unique(name)', 'El nombre debe ser unico!')]
    
sale_empresa_logistica()

# Wizard para preguntar si queremos cerrar o no el pedido.
class pre_cerrar_pedido(osv.osv_memory):
    _name = "pre_cerrar_pedido"
    _description = "Pre cerrar pedido."
    
    def cerrar_pedido(self, cr, uid, ids, context=None):
        if 'active_id' in context and context['active_id'] and 'active_model' in context and context['active_model'] == 'sale.order':
            order = self.pool.get('sale.order').browse(cr, uid, context['active_id'], context=context)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'sale.order', context['active_id'], 'order_pedido_2_cerrado', cr)
        return { 'type': 'ir.actions.act_window_close'}

# Mensaje de Pedido
class sale_order_message(osv.osv):
    '''
    Mensajes que se envian entre el corresponsal y expresso en relacion a un pedido.
    '''
    _name = 'sale.order.message'
    _description = 'Mensaje'
    _rec_name = 'creation_date'
    _order = 'creation_date desc'
    
    def _get_display_text(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for message in self.browse(cr, uid, ids, context=context):
            msg_txt = (message.user_id.name or '/') + ' (' + message.creation_date + '):\n\t'
            msg_txt += (message.message or '')
            result[message.id] = msg_txt
        return result
    
    _columns = {
        'message': fields.text('Mensaje', required=True),
        'creation_date': fields.datetime('Fecha', required=True),
        'order_id': fields.many2one('sale.order', 'Pedido', required=True),
        'user_id': fields.many2one('res.users', 'Usuario'),
        'display_text': fields.function(_get_display_text, method=True, type='text', size="512", string='Display Text'),
        'user_email': fields.char('Email usuario', size=100,),
    }
    
    _defaults = {
        'creation_date': lambda self, cr, uid, context=False: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_id': lambda self, cr, uid, context=False: self.get_current_user_id(cr, uid, context=context),
    }
    
    def get_current_user_id(self, cr, uid, context=None):
        user_id = uid
        if isinstance(user_id, list):
            user_id = user_id[0]
        return user_id
    
sale_order_message()

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    # We change the order for name desc to id desc because SO1xxx is ordered after SOxxx
    _order = 'id desc'
    
    def get_default_partner_from_user(self, cr, uid, context=None):
        if isinstance(uid, list):
            uid = uid[0]
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.partner_id:
            return user.partner_id.id
        else:
            return False
        
    def onchange_user_corresponsal_id_corresponsales(self, cr, uid, ids, user_id):
        return {'value': {'user_corresponsal_id_expresso': user_id}}
    
    def onchange_user_corresponsal_id_expresso(self, cr, uid, ids, user_id):
        return {'value': {'user_corresponsal_id_corresponsales': user_id}}
    
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=126,),
        
        # Datetime de las transiciones del Workflow
        'fecha_confirmado_corresponsal': fields.datetime('Fecha Confirmado - Corresponsal', required=False),
        'fecha_valido_expresso': fields.datetime('Fecha Valido - Expresso', required=False),
        'fecha_valido_corresponsal': fields.datetime('Fecha Valido - Corresponsal', required=False),
        'fecha_cerrado_expresso': fields.datetime('Fecha Cerrado - Expresso', required=False),
        'fecha_despachado_expresso': fields.datetime('Fecha Despachado - Expresso', required=False),
        'fecha_recibido_corresponsal': fields.datetime('Fecha Recibido - Corresponsal', required=False),
        
        # Campos para Expresso
        'fecha_salida': fields.date('Fecha de Salida', required=False,
                                    help="Fecha en la que se estima que el pedido va a estar listo"),
        'forma_envio_id_expresso': fields.many2one('expresso.forma_envio', u'Forma de Envío', required=False,),
        'fecha_estimada_entrega': fields.date('Fecha Estimada de Entrega', required=False,),
        'embarque': fields.char('Embarque', size=100,),
        'empresa_logistica_id': fields.many2one('sale.empresa_logistica', u'Empresa de Logística',),
        
        # Campos para Corresponsales
        'fecha_salida_corresponsales': fields.related('fecha_salida', type="date", string="Fecha de Salida", store=False,
                                                      help="Fecha en la que se estima que el pedido va a estar listo"),
        'forma_envio_id_corresponsales': fields.many2one('expresso.forma_envio', u'Forma de Envío', required=False),
        'fecha_estimada_entrega_corresponsales': fields.related('fecha_estimada_entrega', type="date",
                                                                string="Fecha Estimada de Entrega", store=False),
        'embarque_corresponsales': fields.related('embarque', type="char", string="Embarque", store=False),
        'empresa_logistica_id_corresponsales': fields.related('empresa_logistica_id', type="many2one", relation="sale.empresa_logistica",
                                                           string=u'Empresa de Logística', store=False),
        
        # Estados
        'state_expresso': fields.selection((('borrador', 'Borrador'),
                                            ('pendiente_e', 'Pendiente Expresso'),
                                            ('pendiente_c', 'Pendiente Corresponsal'),
                                            ('pedido', 'Pedido'),
                                            ('cerrado', 'Cerrado'),
                                            ('despachado', 'Despachado'),
                                            ('recibido', 'Recibido')), 'Estado', readonly=True),
        
        'producto_pendiente_ids' : fields.one2many('product.producto_pendiente', 'order_id', u'Títulos Pendientes'),
        'order_message_ids' : fields.one2many('sale.order.message', 'order_id', 'Mensajes'),
        
        # Campo con el partner al cual apunta el usuario actual. Se usa para el domain de otros campos.
        'current_partner_id_for_filtering': fields.many2one('res.partner', 'Current Partner id for Filtering',),
        # Usuarios asociados al pedido
        'user_corresponsal_id_corresponsales': fields.many2one('res.users', 'Usuario Corresponsal', required=True,
                domain="[('partner_id', '=', current_partner_id_for_filtering)]"),
        'user_corresponsal_id_expresso': fields.many2one('res.users', 'Usuario Corresponsal', required=True),
        
        'user_expresso_id_expresso': fields.many2one('res.users', 'Usuario Expresso', required=False),
        'user_expresso_id_corresponsal': fields.related('user_expresso_id_expresso', type="many2one",
                                                        relation="res.users",
                                                        string="Usuario Expresso", store=False),
        
        # Facturas asociadas
        'invoice_ids':fields.many2many('account.invoice','expresso_order_invoice_rel', 'order_id', 'invoice_id',
                                       'Facturas', required=False),        
    }
    
    _defaults = {
        'partner_id': lambda self, cr, uid, context=False: self.get_partner_id_from_user(cr, uid, context=context),
        'partner_invoice_id': lambda self, cr, uid, context=False: self.get_partner_invoice_id_from_user(cr, uid, context=context),
        'partner_order_id': lambda self, cr, uid, context=False: self.get_partner_order_id_from_user(cr, uid, context=context),
        'partner_shipping_id': lambda self, cr, uid, context=False: self.get_partner_shipping_id_from_user(cr, uid, context=context),
        'pricelist_id': lambda self, cr, uid, context=False: self.get_pricelist_id_from_user(cr, uid, context=context),
        'current_partner_id_for_filtering': lambda self, cr, uid, context=False: self.get_default_partner_from_user(cr, uid, context=context),
        'user_corresponsal_id_corresponsales': lambda self, cr, uid, context=False: self.get_user_corresponsal(cr, uid, context=context),
        'user_corresponsal_id_expresso': lambda self, cr, uid, context=False: self.get_user_corresponsal(cr, uid, context=context),
        'user_expresso_id_expresso': lambda self, cr, uid, context=False: self.get_user_expresso(cr, uid, context=context),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        ''' Si se copia un pedido el id_remoto debe ser seteado a None '''
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(sale_order, self).copy(cr, uid, id, default, context)
    
    def get_partner_id_from_user(self, cr, uid, context=None):
        ''' Retorna el Partner asociado al usuario logueado '''
        user = self.get_user(cr, uid, context=context)
        if user:
            return user.partner_id.id
        else:
            return False
    
    def get_partner_invoice_id_from_user(self, cr, uid, context=None):
        partner_id = self.get_partner_id_from_user(cr, uid, context=context)
        if not partner_id:
            return False
        addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice'])
        if not addr:
            return False
        return addr['invoice']
    
    def get_partner_order_id_from_user(self, cr, uid, context=None):
        partner_id = self.get_partner_id_from_user(cr, uid, context=context)
        if not partner_id:
            return False
        addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact'])
        if not addr:
            return False
        return addr['contact']
    
    def get_partner_shipping_id_from_user(self, cr, uid, context=None):
        partner_id = self.get_partner_id_from_user(cr, uid, context=context)
        if not partner_id:
            return False
        addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])
        if not addr:
            return False
        return addr['delivery']
    
    def get_pricelist_id_from_user(self, cr, uid, context=None):
        user = self.get_user(cr, uid, context=context)
        pricelist_id = user.partner_id.property_product_pricelist and user.partner_id.property_product_pricelist.id or False
        return pricelist_id
    
    def get_user_corresponsal(self, cr, uid, context=None):
        user = self.get_user(cr, uid, context=context)
        if self.user_in_group_with_name(user, "Expresso / Corresponsales"):
            return user.id
        else:
            return False
    
    def get_user_expresso(self, cr, uid, context=None):
        user = self.get_user(cr, uid, context=context)
        if self.user_in_group_with_name(user, "Expresso / Corresponsales"):
            if user.partner_id and user.partner_id.user_id:
                return user.partner_id.user_id.id
        return False
    
    
    def get_user(self, cr, uid, context=None):
        ''' Retorna el Usuario logueado '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if isinstance(user, list):
            user = user[0]
        return user
    
    def write(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        
        fecha_del_workflow = ['fecha_confirmado_corresponsal', 'fecha_valido_expresso', 'fecha_valido_corresponsal',
                                      'fecha_cerrado_expresso', 'fecha_despachado_expresso', 'fecha_recibido_corresponsal']
        campos_no_controlados = set(['id_remoto', 'note', 'state_expresso', 'invoice_ids', 'product_warning'] + fecha_del_workflow)
        
        campos_editables_cuando_cerrado = ['order_message_ids', 'embarque', 'empresa_logistica_id', 'id_remoto']
        
        if 'producto_pendiente_ids' in vals:
            if not vals['producto_pendiente_ids']:
                campos_no_controlados.add('producto_pendiente_ids')
        if 'order_line' in vals:
            if not vals['order_line']:
                campos_no_controlados.add('order_line')
        
        campos_modificados = set(vals.keys())
        campos_a_controlar = campos_modificados.difference(campos_no_controlados)
        
        #if len(campos_a_controlar) == 0:
        #    return super(sale_order, self).write(cr, uid, ids, vals, context=context)
        # Pre control
        if len(campos_a_controlar) != 0:
            for order in self.browse(cr, uid, ids, context=context):
                if order.state_expresso:
                    # Si el pedido no esta más en borrador, la forma de envio debe estar completada
                    if order.state_expresso != 'borrador':
                        if 'forma_envio_id_corresponsales' in vals and not vals['forma_envio_id_corresponsales']:
                            raise osv.except_osv('Forma de Envio',
                                                 'No se puede dejar vacia la forma de envío en este estado.')
                        if 'forma_envio_id_expresso' in vals and not vals['forma_envio_id_expresso']:
                            raise osv.except_osv('Forma de Envio',
                                                 'No se puede dejar vacia la forma de envío en este estado.')
                    
                    titulo = 'No puede modificar el pedido'
                    mensaje = 'Solo usuarios del grupo %s puede modificar una orden en el estado %s.'
                    
                    estados_expresso_corresponsales = ['borrador', 'pendiente_e', 'pendiente_c']
                    estados_expresso = ['pedido']
                    
                    titulo_no_modificable = 'Imposible modificar'
                    mensaje_no_modificable = 'No se puede modificar la información del pedido de venta en este estado.'
                    if order.state_expresso in estados_expresso_corresponsales:
                        continue
                    
                    elif order.state_expresso in estados_expresso:
                        if not self.user_in_group_with_name(user, "Expresso / Expresso"):
                            if order.state_expresso == 'borrador':
                                estado = 'Borrador'
                            elif order.state_expresso == 'pendiente_e':
                                estado = 'Pendiente Expresso'
                            else:
                                estado = "Pendiente Corresponsal"
                            raise osv.except_osv(titulo, mensaje % ('Expresso / Expresso', estado))
                    elif order.state_expresso == 'cerrado':
                        no_editables_cuando_cerrado = campos_a_controlar.difference(campos_editables_cuando_cerrado)
                        if no_editables_cuando_cerrado:
                            raise osv.except_osv(titulo_no_modificable, mensaje_no_modificable)
                    else:
                        raise osv.except_osv(titulo_no_modificable, mensaje_no_modificable)
        # Ejecutamos el write
        vals = self.procesar_valores(vals, context=context)
        ret = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        
        # Post procesamiento
        for order in self.browse(cr, uid, ids, context=context):
            if len(campos_a_controlar) == 0:
                continue
            
            if order.state_expresso:
                mensaje = "El pedido ha vuelto a estado borrador como consecuencia de los cambios en el mismo."
                if order.state_expresso == 'pendiente_e':
                    if not self.user_in_group_with_name(user, "Expresso / Expresso"):
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'sale.order', order.id, 'order_pendiente_expresso_2_borrador', cr)
                elif order.state_expresso == 'pendiente_c':
                    if not self.user_in_group_with_name(user, "Expresso / Expresso"):
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'sale.order', order.id, 'order_pendiente_corresponsales_2_borrador', cr)
        
        return ret
    
    def create(self, cr, uid, vals, context=None):
        new_vals = self.procesar_valores(vals, context=context)
        return super(sale_order, self).create(cr, uid, new_vals, context=context)
    
    def procesar_valores(self, vals, context=None): 
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
    def order_state_borrador(self, cr, uid, ids, context=None):
        vals = {}
        vals['fecha_confirmado_corresponsal'] = False
        vals['fecha_valido_expresso'] = False
        vals['fecha_valido_corresponsal'] = False
        vals['fecha_cerrado_expresso'] = False
        vals['fecha_despachado_expresso'] = False
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'borrador'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    def order_state_hacia_borrador(self, cr, uid, ids, context=None):
        return True
    
    def order_state_pendiente_expresso(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for order in self.browse(cr, uid, ids, context=context):
            if not order.forma_envio_id_corresponsales:
                raise osv.except_osv('Forma de Envío incompleta', 'Para confirmar el pedido debe completar el campo Forma de Envío')
        
        vals = {}
        vals['fecha_confirmado_corresponsal'] = now
        vals['fecha_valido_expresso'] = False
        vals['fecha_valido_corresponsal'] = False
        vals['fecha_cerrado_expresso'] = False
        vals['fecha_despachado_expresso'] = False
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'pendiente_e'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    def order_state_pendiente_corresponsal(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in self.browse(cr, uid, ids, context=context):
            if not order.fecha_salida:
                raise osv.except_osv('Fecha de Salida incompleta', 'Para confirmar el pedido debe completar el campo Fecha de Salida')
            if not order.fecha_estimada_entrega:
                raise osv.except_osv('Fecha Estimada de Entrega incompleta',
                                     'Para confirmar el pedido debe completar el campo Fecha Estimada de Entrega')
        
        vals = {}
        vals['fecha_valido_expresso'] = now
        vals['fecha_valido_corresponsal'] = False
        vals['fecha_cerrado_expresso'] = False
        vals['fecha_despachado_expresso'] = False
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'pendiente_c'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    def order_state_pedido(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals = {}
        vals['fecha_valido_corresponsal'] = now
        vals['fecha_cerrado_expresso'] = False
        vals['fecha_despachado_expresso'] = False
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'pedido'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    def order_state_cerrado(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals = {}
        vals['fecha_cerrado_expresso'] = now
        vals['fecha_despachado_expresso'] = False
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'cerrado'
        self.write(cr, uid, ids, vals, context=context)
        
        self.crear_pedido_remoto(cr, uid, ids, context=context)
        
        return True
    
    def order_state_despachado(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in self.browse(cr, uid, ids):
            if not order.empresa_logistica_id:
                raise osv.except_osv('Empresa Lógistica incompleta', 'Para despachar el pedido debe completar el campo Empresa Lógistica')
        
        vals = {}
        vals['fecha_despachado_expresso'] = now
        vals['fecha_recibido_corresponsal'] = False
        vals['state_expresso'] = 'despachado'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    def order_state_recibido(self, cr, uid, ids, context=None):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals = {}
        vals['fecha_recibido_corresponsal'] = now
        vals['state_expresso'] = 'recibido'
        self.write(cr, uid, ids, vals, context=context)
        return True
    
    
    def user_in_group_with_name(self, user, group_name):
        for group in user.groups_id:
            if group.name.lower() == group_name.lower():
                return True
        return False
    
    def crear_pedido_remoto(self, cr, uid, ids, context=None):
        facade_actualizacion = Facade_Actualizacion(pooler)
        facade_actualizacion.crear_pedido_remoto(cr, uid, ids, context=context)
        #actualizador_obj = self.pool.get('expresso.actualizar_bd_incremental')
        #actualizador_obj.crear_pedido_remoto(cr, uid, ids, context=context)
        
sale_order()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=126,),
        'price_unit_corresponsales': fields.related('price_unit', type="float", string="Precio unidad", store=False),
    }
    
    _defaults = {
        'product_uom': lambda self, cr, uid, context=False: self.get_default_uom(cr, uid, context=context),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['id_remoto'] = None
        return super(sale_order_line, self).copy(cr, uid, id, default, context)
    
    def user_in_group_with_name(self, user, group_name):
        for group in user.groups_id:
            if group.name.lower() == group_name.lower():
                return True
        return False
    
    def get_default_uom(self, cr, uid, context=None):
        uom_id = self.pool.get('product.uom').search(cr, uid, [('name', '=', 'PCE')], context=context)
        if not uom_id:
            uom_id = self.pool.get('product.uom').search(cr, uid, [], context=context)
        if isinstance(uom_id, list):
            uom_id = uom_id[0]
        return uom_id    
    
    def product_id_change_inherited(self, cr, uid, ids, pricelist, product, partner_id=False, product_uom_qty=1, context=None):
        super_result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, partner_id=partner_id,
                                                                      context=context)
        result = {}
        if 'value' in super_result:
            if 'name' in super_result['value']:
                result['name'] = super_result['value']['name']
            if 'price_unit' in super_result['value']:
                result['price_unit'] = super_result['value']['price_unit']
                result['price_unit_corresponsales'] = result['price_unit']
        return {'value': result}
    
sale_order_line()









