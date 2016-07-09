# -*- coding: utf-8 -*-
from openerp import models, fields, api
from actualizador.conector_nickel import Conector_Nickel


class sale_order(models.Model):
    _inherit = 'sale.order'

    # product_warning = fields.Boolean(
    #     'Product Warning',
    #     readonly=True, default=False)

    @api.one
    def update_product_warning(self):
        # order_obj = self.pool['sale.order']
        # if not isinstance(list):
        #     ids = [ids]
        # for order in order_obj.browse():
        product_warning = False
        for line in self.order_line:
            if line.product_warning:
                product_warning = True
                break
        self.write(
            {'product_warning': product_warning})
        return True


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    product_warning = fields.Boolean('Product Warning', default=False)

    def create(self, cr, uid, vals, context=None):
        ret = super(sale_order_line, self).create(
            cr, uid, vals, context=context)

        order_obj = self.pool.get('sale.order')
        order_id = vals.get('order_id', False)
        if order_id:
            order_obj.update_product_warning(
                cr, uid, order_id, context=context)
        return ret

    def write(self, cr, uid, ids, vals, context=None):
        ret = super(sale_order_line, self).write(
            cr, uid, ids, vals, context=context)

        order_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        order_id = vals.get('order_id', False)
        if order_id:
            order_obj.update_product_warning(
                cr, uid, order_id, context=context)
        else:
            if not isinstance(ids, list):
                ids = [ids]
            for line in line_obj.browse(cr, uid, ids, context=context):
                order_obj.update_product_warning(
                    cr, uid, line.order_id.id, context=context)
        return ret

    @api.multi
    def product_id_change_inherited(self, pricelist, product_id, partner_id=False, product_uom_qty=1):
        result = super(sale_order_line, self).product_id_change_inherited(pricelist, product_id,
                                                                          partner_id=partner_id, product_uom_qty=product_uom_qty)
        if not product_id:
            return result

        warning = self.warning_stock_product(
            product_id, product_uom_qty)
        value = result.get('value', {})
        if warning:
            value['product_warning'] = True
        else:
            value['product_warning'] = False
        return {'value': value, 'warning': warning}

    @api.multi
    def warning_stock_product(self, product_id, product_uom_qty):
        conector_nickel = Conector_Nickel()
        stock = conector_nickel.check_stock(
            product_id)
        warning = {}
        if not stock:
            product_obj = self.env['product.product']
            product = product_obj.browse(product_id)
            if not product.situacion_id or product.situacion_id.denomination in ['AGOTADO', 'DESCATALOGADO', 'NO DISPONIBLE']:
                warning['title'] = u'State problematic'
                if product.situacion_id:
                    warning[
                        'message'] = u'The title chosen is in a state "%s"' % product.situacion_id.denomination
                else:
                    warning[
                        'message'] = u'The title chosen is not available'
        else:
            stock = int(stock)
            if stock < product_uom_qty:
                warning['title'] = u'Stock not available'
                warning[
                    'message'] = u'There is no stock. Only %s units are available.' % str(stock)

        return warning
