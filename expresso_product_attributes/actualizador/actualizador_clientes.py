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

import logging
import traceback
from lxml import objectify  # http://lxml.de/objectify.html
from actualizador_generico import Actualizador_Generico

import configuracion_actualizacion

_logger = logging.getLogger(__name__)


class Actualizador_Clientes(Actualizador_Generico):

    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_clientes)

    def actualizar_clientes(self, cr, uid, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
        
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        info_corresponsal_ids = info_corresponsal_obj.search(cr, uid, [], context=context)
        
        clientes_procesados = 0
        
        _logger.info('Hay %s Clientes para procesar', len(info_corresponsal_ids))
        
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = info_corresponsal_obj.browse(cr, uid, info_corresponsal_id, context=context)
            
            try:
                cliente_expresso_xml = cliente.service.getCliente(usuario=info_corresponsal.user,
                                                        password=info_corresponsal.contrasenia).encode("iso-8859-1").replace('&','&amp;')
                cliente_expresso = objectify.fromstring(cliente_expresso_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return False
            
            if hasattr(cliente_expresso, 'error'):
                _logger.error('Error procesando corresponsal %s. Error: %s', info_corresponsal.corresponsal, cliente_expresso.error)
                continue
            
            if self.process_cliente(cr, uid, cliente_expresso, info_corresponsal=info_corresponsal, context=context):
                clientes_procesados += 1
        
        _logger.info('Se procesaron %s Clientes', clientes_procesados)
        
        return True
        
    def process_cliente(self, cr, uid, cliente, info_corresponsal=None, context=None):
        #_logger.info('Procesando cliente %s [id_remoto: %s]', cliente.nombre.text, cliente.id)
        
        id_remoto = cliente.id.text
        login = cliente.usuario.text
        new_password = cliente.password.text
        name = cliente.nombre.text
        comment = cliente.observaciones.text
        vat = cliente.nif.text
        address_street = cliente.direccion.text
        # Remplazo los retorno de linea por puntos ya que los campos donde se van a guardar no son texto sino cadenas de caracteres.
        if address_street:
            address_street = address_street.replace('\n', '. ')
        address_phone = cliente.telefono.text
        if address_phone:
            address_phone = address_phone.replace('\n', '. ')
        address_fax = cliente.fax.text
        if address_fax:
            address_fax = address_fax.replace('\n', '. ')
        address_email = cliente.email.text
        if address_email:
            address_email = address_email.replace('\n', '. ')
        address_name = cliente.contacto.text
        
        # active
        active = True
        # TODO: Sacar esto
        #if cliente.bloqueado == 'N':
        #    active = False
        
        # country_id
        country_id = False
        if cliente.pais:
            country_name = cliente.pais.text.title()
            country_ids = self.pooler.get_pool(cr.dbname).get('res.country').search(cr, uid, [('name', '=', country_name)], context=context)
            if country_ids:
                country_id = country_ids[0]
        
        # groups_id
        groups_id = []
        
        corresponsal_group_ids = self.pooler.get_pool(cr.dbname).get('res.groups').search(cr, uid,
                                                        [('name', '=', 'Expresso / Corresponsales')], context=context)
        if corresponsal_group_ids:
            groups_id.append((4, corresponsal_group_ids[0]))
        
        # Creación de res.partner
        new_values_for_partner = {'remote_id': id_remoto, 'name': name, 'active': active, 'vat': vat, 'comment': comment}
        if info_corresponsal:
            new_values_for_partner['info_corresponsal_id'] = info_corresponsal.id
        
        stored_partner_ids = self.get_ids_from_id_remoto(cr, uid, 'res.partner', id_remoto, context=None)
        # Si no hay ningún res.partner con el id_remoto especificado, puede ser que este alamcenado con el campo active igual a False.
        # En dicho caso no se va a actualizar
        if not stored_partner_ids:
            stored_partner_ids = self.pooler.get_pool(cr.dbname).get('res.partner').search(cr, uid,
                                                                        [('remote_id', '=', id_remoto),('active', '=', False)],
                                                                        context=context)
            if stored_partner_ids:
                return False
        
        if not stored_partner_ids:
            stored_partner_ids = [self.pooler.get_pool(cr.dbname).get('res.partner').create(cr, uid, new_values_for_partner)]
        else:
            self.pooler.get_pool(cr.dbname).get('res.partner').write(cr, uid, stored_partner_ids, new_values_for_partner)
        
        
        # Creación de res.partner.address
        new_values_for_address = {'street': address_street, 'phone': address_phone, 'fax': address_fax, 'email': address_email,
                                  'name': address_name, 'country_id': country_id}
        
        for stored_partner_id in stored_partner_ids:
            # new_values_for_address['partner_id'] = stored_partner_id
            # # stored_address_ids = self.pooler.get_pool(cr.dbname).get('res.partner.address').search(cr, uid,
            # #                                                 [('partner_id', '=', stored_partner_id)], context=context)
            # stored_address_ids = self.pooler.get_pool(cr.dbname).get('res.partner').search(cr, uid,
            #                                                 [('partner_id', '=', stored_partner_id)], context=context)
            #
            # if not stored_address_ids:
            #     # self.pooler.get_pool(cr.dbname).get('res.partner.address').create(cr, uid, new_values_for_address, context=context)
            #     self.pooler.get_pool(cr.dbname).get('res.partner').create(cr, uid, new_values_for_address, context=context)
            # else:
            #     # self.pooler.get_pool(cr.dbname).get('res.partner.address').write(cr, uid, stored_address_ids, new_values_for_address, context=context)
            self.pooler.get_pool(cr.dbname).get('res.partner').write(cr, uid, stored_partner_id, new_values_for_address, context=context)

        # Creación de res.user
        partner_id = False
        if stored_partner_ids:
            partner_id = stored_partner_ids[0]
        
        new_values_for_user = {'remote_id': id_remoto, 'login': login, 'new_password': new_password, 'name': name, 'active': active,
                               'partner_id': partner_id}
        if groups_id:
            new_values_for_user['groups_id'] = groups_id
        
        stored_user_ids = self.get_ids_from_id_remoto(cr, uid, 'res.users', id_remoto, context=None)
        # Si no hay ningún res.user con el id_remoto especificado, puede ser que este alamcenado con el campo active igual a False.
        usr_obj = self.pooler.get_pool(cr.dbname).get('res.users')
        if not stored_user_ids:
            filtros = [('remote_id', '=', id_remoto),('active', '=', False)]
            stored_user_ids = usr_obj.search(cr, uid, filtros, context=context)
            if stored_user_ids:
                return False
        
        if not stored_user_ids:
            stored_user_ids = [usr_obj.create(cr, uid, new_values_for_user, context=context)]
        else:
            usr_obj.write(cr, uid, stored_user_ids, new_values_for_user, context=context)

        return True










