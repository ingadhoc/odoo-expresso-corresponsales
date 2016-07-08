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
import time
import datetime
import traceback

import logging
from lxml import objectify  # http://lxml.de/objectify.html

from generic_updater import Actualizador_Generico
import configuracion_actualizacion

_logger = logging.getLogger(__name__)


class Actualizador_Facturas(Actualizador_Generico):

    def __init__(self, pooler):
        Actualizador_Generico.__init__(self, pooler, configuracion_actualizacion.url_facturas)
        
    def obtener_registros_facturas(self, cr, uid, sync_info, context=None):
        return self.obtener_info_objeto_remoto(cr, uid, sync_info, context=context)
    
    def obtener_info_objeto_remoto(self, cr, uid, sync_info, context=None):
        _logger.info('Obteniendo nuevos registros de Facturas.')
        
        cliente = self.get_cliente()
        if not cliente:
            return False
        
        from_date = self.get_string_date(sync_info)
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        info_corresponsal_ids = info_corresponsal_obj.search(cr, uid, [], context=context)
        
        facturas_agregadas = 0
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = info_corresponsal_obj.browse(cr, uid, info_corresponsal_id, context=context)
            try:
                if from_date:
                    facturas_xml = cliente.service.listFacturas(usuario=info_corresponsal.user,
                                                                password=info_corresponsal.contrasenia,
                                                                updated=from_date).encode("iso-8859-1").replace('&','&amp;')
                else:
                    facturas_xml = cliente.service.listFacturas(usuario=info_corresponsal.user,
                                                                password=info_corresponsal.contrasenia).encode(
                                                                                "iso-8859-1").replace('&','&amp;')
                facturas = objectify.fromstring(facturas_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return False
                
            if hasattr(facturas, 'error'):
                #_logger.info('No hay nuevos registros de Facturas.')
                continue
            
            for factura_it in facturas.iterchildren():
                facturas_agregadas += 1
                id_remoto = factura_it.id
                
                info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
                sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
                
                filtros = [('id_remoto', '=', id_remoto), ('clase', '=', 'account.invoice')]
                info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
                
                if not info_objeto_ids:
                    vals = {}
                    vals['id_remoto'] = id_remoto
                    vals['clase'] = 'account.invoice'
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
                else:
                    vals = {}
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_obj.write(cr, uid, info_objeto_ids, vals, context=context)
                
                if not isinstance(info_objeto_ids, list):
                    info_objeto_ids = [info_objeto_ids]
                
                for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                    if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                        vals = {}
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        vals['datetime_creation'] = now
                        vals['info_objeto_remoto_id'] = info_objeto.id
                        sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos registros de Facturas para procesar', str(facturas_agregadas))
        return True
    
    def actualizar_una_factura_desde_info_objeto_id(self, cr, uid, info_objeto_id, context=None):
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        filtros = [('info_objeto_remoto_id.id', '=', info_objeto_id), ('procesado', '=', False)]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        sincronizacion_objeto = sinc_obj.browse(cr, uid, sinc_a_procesar, context=context)
        
        if not sincronizacion_objeto:
            return False
        if isinstance(sincronizacion_objeto, list):
            sincronizacion_objeto = sincronizacion_objeto[0]
        return self.actualizar_una_factura(cr, uid, sincronizacion_objeto, context=context)
    
    
    def actualizar_una_factura(self, cr, uid, sincronizacion, context=None):
        cliente = self.get_cliente()
        if not cliente:
            return False
            
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        # Se obtiene la factura desde el WS y se convierte en objeto
        id_remoto = sincronizacion.info_objeto_remoto_id.id_remoto
        
        if not sincronizacion.info_objeto_remoto_id.corresponsal.id:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = 'No se encuentra Corresponsal definido para este registro de Factura.'
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        info_corresponsal = info_corresponsal_obj.browse(cr, uid, sincronizacion.info_objeto_remoto_id.corresponsal.id, context=context)
        
        try:
            factura_xml = cliente.service.getFactura(usuario=info_corresponsal.user,
                                                     password=info_corresponsal.contrasenia,
                                                     id=id_remoto).encode("iso-8859-1").replace('&','&amp;')
            factura = objectify.fromstring(factura_xml)
        # Si hay se marca el error en el registro
        except:
            e = traceback.format_exc()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = e
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        
        # Si se devolvio 'error' en el atributo del objeto entonces se marca el error en el registro
        if hasattr(factura, 'error'):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = factura.error
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return False
        
        # Se procesa la factura y se marca el registro como procesado y se indica que no necesita ser reprocesado
        ret = self.process_factura(cr, uid, factura, info_corresponsal, sincronizacion.id, context=context)
        if ret:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = False
            sinc_obj.write(cr, uid, sincronizacion.id, vals, context=context)
            return True
        else:
            return False
    
    
    def actualizar_facturas(self, cr, uid, context=None):
        _logger.info('Procesando Facturas')
        cliente = self.get_cliente()
        if not cliente:
            return None
        
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        filtros = [('procesado', '=', False), ('info_objeto_remoto_id.clase', '=', 'account.invoice')]
        sinc_a_procesar = sinc_obj.search(cr, uid, filtros, context=context)
        
        # Cantidad de facturas procesadas correctamente
        facturas_procesadas = 0
        # Cantidad de iteraciones del bucle
        iteraciones = 0
        
        for sincronizacion in sinc_obj.browse(cr, uid, sinc_a_procesar, context=context):
            # Para no bloquear tanto el trafico de internet
            time.sleep(1)
            # Si se itero un cierto numero de veces entonces se publica un mensaje en el log
            iteraciones += 1
            if iteraciones % configuracion_actualizacion.invoice_frequency_print_working == 0:
                _logger.info('Procesando Facturas')
                
            # Si se itero un cierto numero de veces entonces se sale del bucle
            if iteraciones > configuracion_actualizacion.invoice_update_quantity:
                break
            ret = self.actualizar_una_factura(cr, uid, sincronizacion, context=context)
            if ret:
                facturas_procesadas += 1
        
        _logger.info('Se procesaron finalmente %s Facturas', facturas_procesadas)
    
    
    def process_factura(self, cr, uid, factura, info_corresponsal, sincronizacion_id, context=None):
        #_logger.info('Procesando factura [id_remoto: %s]', str(factura.id))
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        
        id_remoto = factura.id
        partida = factura.partida.text
        aduana = factura.aduana.text
        bultos = factura.bultos.text
        pesoneto = factura.pesoneto.text
        pesobruto = factura.pesobruto.text
        origen = factura.origen.text
        muestras = False
        if factura.muestras and factura.muestras.text == 'Y':
            muestras = True
        total = factura.total
        numero_factura = factura.numero.text
        tipo = factura.tipo.text
        
        # date_invoice
        date_invoice = False
        if factura.fecha and len(str(factura.fecha.text)) == 8:
            date_invoice = str(factura.fecha.text)[0:4] + '-' + str(factura.fecha.text)[4:6] + '-' + str(factura.fecha.text)[6:8]
        
        # currency_id
        currency_id = False
        
        # Por default currency_id es la moneda de la compañía.
        company_id = self.pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [], context=context)
        if isinstance(company_id, list):
            company_id = company_id[0]
        if company_id:
            company = self.pooler.get_pool(cr.dbname).get('res.company').browse(cr, uid, company_id, context=context)
            currency_id = company.currency_id.id
        
        # Si la factura especifica una divisa, se utiliza esta.
        if factura.divisa and len(str(factura.divisa.text)) >= 4:
            currency_name = str(factura.divisa.text)[1:4]
            if currency_name == 'USA':
                currency_name = 'USD'
            
            currency_ids = self.pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid,
                                                                                      [('name', '=', currency_name)],
                                                                                      context=context)
            if currency_ids:
                currency_id = currency_ids[0]
        
        # Si todo falla, se setea a dolares norteamericanos.
        if not currency_id:
            usd_currency_id = self.pooler.get_pool(cr.dbname).get('res.currency').search(cr, uid, [('name', '=', 'USD')], context=context)
            if isinstance(usd_currency_id, list):
                usd_currency_id = usd_currency_id[0]
            currency_id = usd_currency_id
        
        # partner_id
        partner_id = False
        partner_ids = self.get_partner_ids_from_user_login(cr, uid, info_corresponsal.user, context=None)
        if partner_ids:
            partner_id = partner_ids[0]
        if not partner_id:
            error = 'Tratando de guardar una factura [id_remoto: %s] no se encontro el res.partner %s asociado al usuario %s.' % \
                    (str(id_remoto), factura.nombre.text, info_corresponsal.user)
            #_logger.error(error)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = error
            sinc_obj.write(cr, uid, sincronizacion_id, vals, context=context)
            return None
        # address_invoice_id
        # address_invoice_id = False
        # address_invoice_ids = self.pooler.get_pool(cr.dbname).get('res.partner.address').search(cr, uid,
        #                                                 [('partner_id', '=', partner_id), ('street', '=', factura.direccion)],
        #                                                 context=context)
        # if address_invoice_ids:
        #     address_invoice_id = address_invoice_ids[0]
        # if not address_invoice_id:
        #     address_invoice_ids = self.pooler.get_pool(cr.dbname).get('res.partner.address').search(cr, uid,
        #                                                 [('partner_id', '=', partner_id)], context=context)
        #     if address_invoice_ids:
        #         address_invoice_id = address_invoice_ids[0]
        #     if not address_invoice_id:
        #         error = 'Tratando de guardar una factura [id_remoto: %s] no se encontro ningun res.partner.address del res.partner %s.' % (str(id_remoto), factura.nombre.text)
        #         #_logger.error(error)
        #         now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #         vals = {}
        #         vals['datetime'] = now
        #         vals['procesado'] = True
        #         vals['error_al_procesar'] = True
        #         vals['mensaje_error'] = error
        #         sinc_obj.write(cr, uid, sincronizacion_id, vals, context=context)
        #         return None
        # account_id
        account_id = False
        if partner_id:
            partner = self.pooler.get_pool(cr.dbname).get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner.property_account_payable_id:
                account_id = partner.property_account_payable_id.id
        if not account_id:
            error = 'Tratando de guardar una factura [id_remoto: %s] no se encontro el account.account (account_payable)' \
                    ' del res.partner %s.' % (id_remoto, partner.name)
            #_logger.error(error)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vals = {}
            vals['datetime'] = now
            vals['procesado'] = True
            vals['error_al_procesar'] = True
            vals['mensaje_error'] = error
            sinc_obj.write(cr, uid, sincronizacion_id, vals, context=context)
            return None
        # packing_id
        packing_id = False
        if factura.packing:
            packing_ids = self.get_ids_from_id_remoto(cr, uid, 'expresso.packing', factura.packing, context=context)
            if packing_ids:
                packing_id = packing_ids[0]
        # Persist account.invoice
        new_data = {'remote_id': id_remoto, 'date_invoice': date_invoice, 'currency_id': currency_id,
                    # 'address_invoice_id': address_invoice_id, 'partner_id': partner_id, 'account_id': account_id,
                    'partner_id': partner_id, 'account_id': account_id,
                    'partida': partida, 'aduana': aduana, 'bultos': bultos, 'pesoneto': pesoneto, 'pesobruto': pesobruto,
                    'origen': origen, 'packing_id': packing_id, 'muestras': muestras, 'numero_factura': numero_factura,
                    'tipo': tipo}
        stored_invoice_ids = self.get_ids_from_id_remoto(cr, uid, 'account.invoice', id_remoto, context=context)
        if not stored_invoice_ids:
            stored_invoice_ids = [self.pooler.get_pool(cr.dbname).get('account.invoice').create(cr, uid, new_data, context=context)]
        else:
            self.pooler.get_pool(cr.dbname).get('account.invoice').write(cr, uid, stored_invoice_ids, new_data, context=context)
        # Process the objects caja attached to the object invoice
        #invoices = self.pooler.get_pool(cr.dbname).get('account.invoice').browse(cr, uid, stored_invoice_ids, context=context)
        
        if not factura.detalle or not factura.detalle.linea:
            return stored_invoice_ids
        for stored_invoice_id in stored_invoice_ids:
            for linea in factura.detalle.linea:
                self.process_linea(cr, uid, stored_invoice_id, account_id, linea, context=context)
        # gastos
        if factura.gastos:
            for stored_invoice_id in stored_invoice_ids:
                self.generar_linea_gastos(cr, uid, stored_invoice_id, account_id, factura.gastos, context=context)
                
        #for stored_invoice_id in stored_invoice_ids:
        #    ctrl_invoice = self.pooler.get_pool(cr.dbname).get('account.invoice').browse(cr, uid, stored_invoice_id, context=context)
        #    if ctrl_invoice.amount_total != total:
        #        _logger.warning('Procesando la factura [id: %s] el total calculado (%s) no coincide con el total recibido (%s).',
        #                              stored_invoice_id, ctrl_invoice.amount_total, total)
        
        return stored_invoice_ids
    
    
    
    def process_linea(self, cr, uid, invoice_id, account_id, linea, context=None):
        id_remoto = linea.id
        quantity = linea.ejemplares
        price_unit = linea.importe
        
        # product_id
        product_id = False
        product_ids = self.pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [('isbn', '=', linea.isbn)], context=context)
        if product_ids:
            product_id = product_ids[0]
            if len(product_ids) > 1:
                _logger.warning('Hay mas de un producto con ISBN %s. Los productos son: %s',
                                    str(linea.isbn), str([p.name for p in product_ids]))
        
        if not product_id:
            product_ids = self.pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [], context=context)
            if product_ids:
                product_id = product_ids[0]
        
        # name
        name = linea.concepto.text
        if not name:
            if product_id:
                product = self.pooler.get_pool(cr.dbname).get('product.product').browse(cr, uid, product_id, context=context)
                name = product.name
            else:
                name = 'Producto no especificado'
        
        # Persistir o crear un nuevo stock.move
        new_values = {'id_remoto': id_remoto, 'product_id': product_id, 'quantity': quantity, 'price_unit': price_unit,
                      'invoice_id': invoice_id, 'account_id': account_id, 'name': name}
        
        stored_line_ids = self.get_ids_from_id_remoto(cr, uid, 'account.invoice.line', id_remoto, context=context)
        if not stored_line_ids:
            stored_line_ids = [self.pooler.get_pool(cr.dbname).get('account.invoice.line').create(cr, uid, new_values, context=context)]
        else:
            self.pooler.get_pool(cr.dbname).get('account.invoice.line').write(cr, uid, stored_line_ids, new_values, context=context)
        
        return stored_line_ids
    
    
    
    def generar_linea_gastos(self, cr, uid, invoice_id, account_id, gastos, context=None):
        id_remoto = None
        quantity = 1
        price_unit = gastos
        name = 'Gastos generales'
        
        new_values = {'id_remoto': id_remoto, 'quantity': quantity, 'price_unit': price_unit,
                      'invoice_id': invoice_id, 'account_id': account_id, 'name': name}
        
        stored_gastos_ids = self.pooler.get_pool(cr.dbname).get('account.invoice.line').search(cr, uid,
                                                                        [('invoice_id', '=', invoice_id), ('name', '=', name)],
                                                                        context=context)
        
        # Si al menos una linea de 'Gastos generales' no tiene id_remoto entonces no hay que crear uno nuevo.
        for stored_gasto_id in stored_gastos_ids:
            stored_gastos = self.pooler.get_pool(cr.dbname).get('account.invoice.line').browse(cr, uid, stored_gasto_id, context=context)
            if stored_gastos.id_remoto == 0:
                break
            stored_gastos_ids = []
        
        if not stored_gastos_ids:
            stored_gastos_ids = [self.pooler.get_pool(cr.dbname).get('account.invoice.line').create(cr, uid, new_values, context=context)]
        else:
            self.pooler.get_pool(cr.dbname).get('account.invoice.line').write(cr, uid, stored_gastos_ids, new_values, context=context)
        
        return stored_gastos_ids






    

    #
    def obtener_info_objeto_remoto_si_no_presente(self, cr, uid, context=None):
        _logger.info('Obteniendo todos los registros de Facturas.')
        cliente = self.get_cliente()
        if not cliente:
            return False
        
        info_corresponsal_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_corresponsal')
        info_corresponsal_ids = info_corresponsal_obj.search(cr, uid, [], context=context)
        
        facturas_agregadas = 0
        lista_facturas_agregadas = []
        for info_corresponsal_id in info_corresponsal_ids:
            info_corresponsal = info_corresponsal_obj.browse(cr, uid, info_corresponsal_id, context=context)
            try:
                facturas_xml = cliente.service.listFacturas(usuario=info_corresponsal.user,
                                                            password=info_corresponsal.contrasenia).encode(
                                                                            "iso-8859-1").replace('&','&amp;')
                facturas = objectify.fromstring(facturas_xml)
            except:
                e = traceback.format_exc()
                _logger.error('Ocurrio un error al conectarse al web services %s. Error: %s', self.url_ws, e)
                return False
        
            if hasattr(facturas, 'error'):
                #_logger.info('No hay nuevos registros de Facturas.')
                continue
            
            for factura_it in facturas.iterchildren():
                id_remoto = factura_it.id
                
                info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
                sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
                
                filtros = [('id_remoto', '=', id_remoto), ('clase', '=', 'account.invoice')]
                info_objeto_ids = info_objeto_obj.search(cr, uid, filtros, context=context)
                
                if not info_objeto_ids:
                    vals = {}
                    vals['id_remoto'] = id_remoto
                    vals['clase'] = 'account.invoice'
                    vals['corresponsal'] = info_corresponsal.id
                    info_objeto_ids = info_objeto_obj.create(cr, uid, vals, context=context)
                    
                    facturas_agregadas += 1
                    lista_facturas_agregadas.append(id_remoto)
                    
                    if not isinstance(info_objeto_ids, list):
                        info_objeto_ids = [info_objeto_ids]
                
                    for info_objeto in info_objeto_obj.browse(cr, uid, info_objeto_ids, context=context):
                        if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                            vals = {}
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            vals['datetime_creation'] = now
                            vals['info_objeto_remoto_id'] = info_objeto.id
                            sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se agregaron %s nuevos registros de Facturas para procesar', str(facturas_agregadas))
        _logger.info('Los registros agregados son: %s', str(lista_facturas_agregadas))
        return True
    
    
    
    def marcar_info_objeto_remoto_para_actualizar(self, cr, uid, context=None):
        '''
        Marca todos los registros de la base de datos para ser procesados.
        '''
        _logger.info('Marcando registos de Facturas para reprocesar')
        
        info_objeto_obj = self.pooler.get_pool(cr.dbname).get('expresso.info_objeto_remoto')
        sinc_obj = self.pooler.get_pool(cr.dbname).get('expresso.sincronizacion_objeto_remoto')
        
        all_info_objeto_remoto_ids = info_objeto_obj.search(cr, uid, [('clase', '=', 'account.invoice')], context=context)
        
        registro_agregados = 0
        iteracion = 0
        for info_objeto in info_objeto_obj.browse(cr, uid, all_info_objeto_remoto_ids, context=context):
            iteracion += 1
            if iteracion % configuracion_actualizacion.frequency_registro_reprocesar == 0:
                _logger.info('Marcando registos de Facturas para reprocesar')
            
            isbn = info_objeto.id_remoto
            if not info_objeto.sincronizacion_objeto_remoto_ids or info_objeto.procesado:
                registro_agregados += 1
                vals = {}
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                vals['datetime_creation'] = now
                vals['info_objeto_remoto_id'] = info_objeto.id
                sinc_obj.create(cr, uid, vals, context=context)
        
        _logger.info('Se marcaron %s registos de Facturas para reprocesar', str(registro_agregados))
        return True









