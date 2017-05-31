# -*- coding: utf-8 -*-

import MySQLdb
# import time
import traceback
from openerp import models, pooler, api

import logging
_logger = logging.getLogger(__name__)


class Conector_Nickel:

    # Actualizar Clientes

    def update_clients(self, cr, uid, context=None):
        db_host = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_host')
        db_user = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_user')
        db_password = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_password')
        db_name = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_name')


        # db_host = self.pool['ir.config_parameter'].get_param('db_host')
        # db_user = self.pool['ir.config_parameter'].get_param('db_user')
        # db_password = self.pool['ir.config_parameter'].get_param('db_password')
        # db_name = self.pool['ir.config_parameter'].get_param('db_name')
        try:
            db = MySQLdb.connect(
                host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False

        sql = 'SELECT * FROM exp_tblCliente'
        cliente_obj =  pooler.get_pool(cr.dbname).get('nickel_partner')

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                id_remoto = row[0]
                boolean = row[1]
                name = row[2]
                name_2 = row[3]
                country_code = row[4]

                vals = {'remote_id': id_remoto, 'name': name,
                        'booleano': boolean, 'country_code': country_code}
                ids = cliente_obj.search(cr,uid, [('remote_id', '=', id_remoto)],None)
                if ids:
                    cliente_obj.write(cr, uid, ids, vals, None)
                else:
                    ids = cliente_obj.create(cr, uid, vals, None)

        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al procesar los Clientes de Nickel. Error: %s', e)
            return False

        db.close()
        return True

    # Actualizar Facturas
    def update_invoices(self, cr, uid, context=None):
        # db_host = self.env['ir.config_parameter'].get_param('db_host')
        # db_user = self.env['ir.config_parameter'].get_param('db_user')
        # db_password = self.env['ir.config_parameter'].get_param('db_password')
        # db_name = self.env['ir.config_parameter'].get_param('db_name')
        db_host = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_host')
        db_user = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_user')
        db_password = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_password')
        db_name = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_name')
        try:
            db = MySQLdb.connect(
                host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False

        sql = 'SELECT * FROM exp_tblCCEfectos'
        invoice_nikel_obj = pooler.get_pool(cr.dbname).get('nickel_invoice')
        invoice_obj = pooler.get_pool(cr.dbname).get('account.invoice')

        unpaid_invoices = []
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                id_remoto = row[0]
                customer_code = row[1]
                invoice_number = row[2]
                serie = row[3]
                invoice_date = row[4]
                expiration_date = row[5]
                amount = row[6]
                amount = amount / 100
                code_currency = row[7]

                # nickel_cliente_obj = pooler.get_pool(cr.dbname).get('nickel_partner')
                # TODO arreglar esto! deberiamos traer un solo partner, el partner principal
                partner_id = self.env['expresso.info_corresponsal'].search(
                    [('nickel_customer_id.remote_id', '=', customer_code)],
                    limit=1).partner_ids[0]

                invoice_id = invoice_obj.search(
                    cr, uid, [('invoice_number', '=', invoice_number)], None)
                if invoice_id and isinstance(invoice_id, list):
                    invoice_id = invoice_id[0]

                vals = {'remote_id': id_remoto, 'customer_code': customer_code, 'invoice_number': invoice_number,
                        'serie': serie, 'invoice_date': invoice_date, 'expiration_date': expiration_date,
                        'amount': amount, 'code_currency': code_currency, 'partner_id': partner_id,
                        'invoice_id': invoice_id, 'paid': False}
                ids = invoice_nikel_obj.search(
                    cr, uid, [('remote_id', '=', id_remoto)], None)
                if ids:
                    invoice_nikel_obj.write(cr, uid, ids, vals, None)
                else:
                    ids = invoice_nikel_obj.create(cr, uid, vals, None)

                if isinstance(ids, list):
                    unpaid_invoices += ids
                else:
                    unpaid_invoices.append(ids)
        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al procesar las Facturas de Nickel. Error: %s', e)
            return False

        db.close()

        filters = [('id', 'not in', unpaid_invoices), ('paid', '=', False)]
        paid_invoices = invoice_nikel_obj.search(
            cr, uid, filters, None)
        if not isinstance(paid_invoices, list):
            paid_invoices = [paid_invoices]
        vals = {'paid': True}
        invoice_nikel_obj.write(cr, uid, paid_invoices, vals, None)

        invoices_processed = unpaid_invoices + paid_invoices
        invoice_a_procesar = invoice_nikel_obj.get_invoice_asociados(
            cr, uid, invoices_processed, context=context)
        self.recalculate_invoices_fields(
            cr, uid, invoice_a_procesar, context=context)

        return True

    def recalculate_invoices_fields(self, cr, uid, ids, context=None):
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
        for invoice in invoice_obj.browse(cr, uid, ids, None):
            residual = 0.0
            paid = True
            for factura in invoice.nickel_invoice_ids:
                if not factura.paid:
                    residual += factura.amount
                    paid = False
            residual = currency_obj.compute(
                cr, uid, eur_id, usd_id, residual, None)
            invoice_obj.write(
                cr, uid, invoice.id, {'residual_2': residual, 'paid': paid}, None)

    # Actualizar Stock
    def update_stock(self, cr, uid, context=None):
        # db_host = self.env['ir.config_parameter'].get_param('db_host')
        # db_user = self.env['ir.config_parameter'].get_param('db_user')
        # db_password = self.env['ir.config_parameter'].get_param('db_password')
        # db_name = self.env['ir.config_parameter'].get_param('db_name')
        db_host = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_host')
        db_user = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_user')
        db_password = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_password')
        db_name = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_name')
        try:
            db = MySQLdb.connect(
                host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False

        sql = 'SELECT * FROM exp_tblArticuloStock'
        cliente_obj = pooler.get_pool(cr.dbname).get('nickel_partner')

        ean_no_encontrados = []
        try:
            inventry_obj = pooler.get_pool(cr.dbname).get('stock.inventory')
            inventory_id = inventry_obj.create(
                cr, uid, {'name': 'Inventario Nickel'}, None)

            cursor.execute(sql)
            results = cursor.fetchall()
            _logger.info(
                'Hay %s lineas de inventario para procesar.', str(len(results)))
            for row in results:
                id_remoto = row[0]
                ean_separado = row[1]
                ean_compactado = row[2]
                cantidad = row[3]

                location_obj = pooler.get_pool(cr.dbname).get('stock.location')
                location_id = location_obj.search(
                    cr, uid, [('name', '=', 'Stock'), ('usage', '=', 'internal')], None)
                if not location_id:
                    location_id = location_obj.search(
                        cr, uid, [('usage', '=', 'internal')], None)
                if isinstance(location_id, list):
                    location_id = location_id[0]

                product_obj = pooler.get_pool(cr.dbname).get('product.product')
                product_id = product_obj.search(
                    cr, uid, [('default_code', '=', ean_compactado)], None)
                product = product_obj.browse(
                    cr, uid, product_id, None)
                if not product:
                    ean_no_encontrados.append(ean_compactado)
                    continue
                if product and isinstance(product, list):
                    product = product[0]

                inventry_line_obj = pooler.get_pool(cr.dbname).get('stock.inventory.line')
                vals = {'inventory_id': inventory_id,
                        'product_qty': cantidad,
                        'location_id': location_id,
                        'product_id': product.id,
                        'product_uom': product.uom_id.id}
                inventry_line_obj.create(cr, uid, vals, None)

            inventry_obj.action_check(
                cr, uid, [inventory_id], None)
            inventry_obj.action_done(cr, uid, [inventory_id], None)

        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al procesar el Stock de Nickel. Error: %s', e)
            return False

        db.close()
        if ean_no_encontrados:
            _logger.warning('No se encontro %s producto. Los EANs son: %s', str(
                len(ean_no_encontrados)), str(ean_no_encontrados))
        return True

    # Consultar Stock
    def check_stock(self, cr, uid, product_id, context=None):
        # db_host = self.env['ir.config_parameter'].get_param('db_host')
        # db_user = self.env['ir.config_parameter'].get_param('db_user')
        # db_password = self.env['ir.config_parameter'].get_param('db_password')
        # db_name = self.env['ir.config_parameter'].get_param('db_name')
        db_host = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_host')
        db_user = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_user')
        db_password = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_password')
        db_name = pooler.get_pool(cr.dbname).get('ir.config_parameter').get_param(cr, uid, 'db_name')
        if not product_id:
            return False
        try:
            db = MySQLdb.connect(
                host=db_host, user=db_user, passwd=db_password, db=db_name)
            cursor = db.cursor()
        except:
            e = traceback.format_exc()
            _logger.error(
                'Ocurrio un error al conectarse Nickel. Error: %s', e)
            return False

        product_obj = pooler.get_pool(cr.dbname).get('product.product')
        product = product_obj.browse(cr, uid, product_id, None)
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
