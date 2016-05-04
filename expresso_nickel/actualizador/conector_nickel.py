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

import MySQLdb
import time
import traceback

import pooler
import logging
from osv import osv, fields
import tools

_logger = logging.getLogger(__name__)

db_host = '144.76.16.237'
db_user = 'mydataro'
db_password = 'NewCall02'
db_name = 'data_sync'

class Conector_Nickel:
    
    # Actualizar Clientes
    def actualizar_clientes(self, cr, uid, context=None):
        try:
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False
        
        sql = 'SELECT * FROM exp_tblCliente'
        cliente_obj = pooler.get_pool(cr.dbname).get('nickel_cliente')
        
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                id_remoto = row[0]
                booleano = row[1]
                nombre = row[2]
                nombre_2 = row[3]
                codigo_pais = row[4]
                
                vals = {'id_remoto': id_remoto, 'name': nombre, 'booleano': booleano, 'codigo_pais': codigo_pais}
                ids = cliente_obj.search(cr, uid, [('id_remoto', '=', id_remoto)], context=context)
                if ids:
                    cliente_obj.write(cr, uid, ids, vals, context=context)
                else:
                    ids = cliente_obj.create(cr, uid, vals, context=context)
            
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al procesar los Clientes de Nickel. Error: %s', e)
            return False
        
        db.close()
        return True
    
    
    # Actualizar Facturas
    def actualizar_facturas(self, cr, uid, context=None):
        try:
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False
        
        sql = 'SELECT * FROM exp_tblCCEfectos'
        factura_obj = pooler.get_pool(cr.dbname).get('nickel_factura')
        invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        
        facturas_impagas = []
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                id_remoto = row[0]
                codigo_cliente = row[1]
                numero_factura = row[2]
                serie = row[3]
                fecha_factura = row[4]
                fecha_vencimiento = row[5]
                importe = row[6]
                importe = importe / 100
                codigo_divisa = row[7]
                
                nickel_cliente_obj = pooler.get_pool(cr.dbname).get('nickel_cliente')
                partner_id = nickel_cliente_obj.get_partner_desde_id_remoto(cr, uid, codigo_cliente, context=context)
                
                factura_id = invoice_obj.search(cr, uid, [('numero_factura', '=', numero_factura)], context=context)
                if factura_id and isinstance(factura_id, list):
                    factura_id = factura_id[0]
                
                vals = {'id_remoto': id_remoto, 'codigo_cliente': codigo_cliente, 'numero_factura': numero_factura,
                        'serie': serie, 'fecha_factura': fecha_factura, 'fecha_vencimiento': fecha_vencimiento,
                        'importe': importe, 'codigo_divisa': codigo_divisa, 'partner_id': partner_id,
                        'factura_id': factura_id, 'pagado': False}
                ids = factura_obj.search(cr, uid, [('id_remoto', '=', id_remoto)], context=context)
                if ids:
                    factura_obj.write(cr, uid, ids, vals, context=context)
                else:
                    ids = factura_obj.create(cr, uid, vals, context=context)
                
                if isinstance(ids, list):
                    facturas_impagas += ids
                else:
                    facturas_impagas.append(ids)
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al procesar las Facturas de Nickel. Error: %s', e)
            return False
        
        db.close()
        
        filtros = [('id', 'not in', facturas_impagas), ('pagado', '=', False)]
        facturas_pagadas = factura_obj.search(cr, uid, filtros, context=context)
        if not isinstance(facturas_pagadas, list):
            facturas_pagadas = [facturas_pagadas]
        vals = {'pagado': True}
        factura_obj.write(cr, uid, facturas_pagadas, vals, context=context)
        
        facturas_procesadas = facturas_impagas + facturas_pagadas
        invoice_a_procesar = factura_obj.get_invoice_asociados(cr, uid, facturas_procesadas, context=context)
        self.recalcular_campos_facturas(cr, uid, invoice_a_procesar, context=context)
        
        return True
    
    def recalcular_campos_facturas(self, cr, uid, ids, context=None):
        _logger.info('Recalculando el importe residual de las Facturas.')
        
        currency_obj = pooler.get_pool(cr.dbname).get('res.currency')
        eur_id = currency_obj.search(cr, uid, [('name', '=', 'EUR')])
        if isinstance(eur_id, list):
            eur_id = eur_id[0]
        usd_id = currency_obj.search(cr, uid, [('name', '=', 'USD')])
        if isinstance(usd_id, list):
            usd_id = usd_id[0]
        
        invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        # Si descomentamos la siguiente linea entonces se recalcula el valor pero en todas las facturas
        #ids = invoice_obj.search(cr, uid, [], context=context)
        for invoice in invoice_obj.browse(cr, uid, ids, context=context):
            residual = 0.0
            pagado = True
            for factura in invoice.nickel_factura_ids:
                if not factura.pagado:
                    residual += factura.importe
                    pagado = False
            residual = currency_obj.compute(cr, uid, eur_id, usd_id, residual, context=context)
            invoice_obj.write(cr, uid, invoice.id, {'residual_2': residual, 'pagado': pagado}, context=context)
    
    
    # Actualizar Stock
    def actualizar_stock(self, cr, uid, context=None):
        try:
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False
        
        sql = 'SELECT * FROM exp_tblArticuloStock'
        cliente_obj = pooler.get_pool(cr.dbname).get('nickel_cliente')
        
        ean_no_encontrados = []
        try:
            inventry_obj = pooler.get_pool(cr.dbname).get('stock.inventory')
            inventory_id = inventry_obj.create(cr , uid, {'name': 'Inventario Nickel'}, context=context)
            
            cursor.execute(sql)
            results = cursor.fetchall()
            _logger.info('Hay %s lineas de inventario para procesar.', str(len(results)))
            for row in results:
                id_remoto = row[0]
                ean_separado = row[1]
                ean_compactado = row[2]
                cantidad = row[3]
                
                location_obj = pooler.get_pool(cr.dbname).get('stock.location')
                location_id = location_obj.search(cr, uid, [('name', '=', 'Stock'), ('usage', '=', 'internal')], context=context)
                if not location_id:
                    location_id = location_obj.search(cr, uid, [('usage', '=', 'internal')], context=context)
                if isinstance(location_id, list):
                    location_id = location_id[0]
                
                product_obj = pooler.get_pool(cr.dbname).get('product.product')
                product_id = product_obj.search(cr, uid, [('default_code', '=', ean_compactado)], context=context)
                product = product_obj.browse(cr, uid, product_id, context=context)
                if not product:
                    ean_no_encontrados.append(ean_compactado)
                    continue
                if product and isinstance(product, list):
                    product = product[0]
                
                inventry_line_obj = pooler.get_pool(cr.dbname).get('stock.inventory.line')
                vals = {'inventory_id' : inventory_id,
                        'product_qty' : cantidad,
                        'location_id' : location_id,
                        'product_id' : product.id, 
                        'product_uom' : product.uom_id.id}
                inventry_line_obj.create(cr, uid, vals, context=context)
            
            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)
            
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al procesar el Stock de Nickel. Error: %s', e)
            return False
        
        db.close()
        if ean_no_encontrados:
            _logger.warning('No se encontro %s producto. Los EANs son: %s', str(len(ean_no_encontrados)), str(ean_no_encontrados))
        return True

    
    # Consultar Stock
    def consultar_stock(self, cr, uid, product_id, context=None):
        if not product_id:
            return False
        try:
            db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error('Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False
        
        product_obj = pooler.get_pool(cr.dbname).get('product.product')
        product = product_obj.browse(cr, uid, product_id, context=context)
        if not product:
            return False
        if isinstance(product, list):
            product = product[0]
        
        sql = 'SELECT * FROM exp_tblArticuloStock WHERE strEan13="%s"' % product.default_code
        cursor.execute(sql)
        row = cursor.fetchall()
        if not row:
            return False
        cantidad = row[0][3]
        return cantidad







