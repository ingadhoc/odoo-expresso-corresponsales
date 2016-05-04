# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-Today OpenERP SA (<http://www.openerp.com>).
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

{
    'name' : 'Expresso Sale order lines visible for importantion',
    'version': '1.0',
    'author': 'Sistemas ADHOC',
    'website': 'http://www.sistemasadhoc.com.ar/',
    'depends' : ['sale', 'expresso_product_attributes'],
    'category' : 'Sale Management',
    'description': '''This module add 1 menu item, for Sale Order lines.
This views are for allowing users to import order lines.

Actions are created for Sale Order and Sale Order Line so that the lines
are updated as if the product was selected from the views.
This is because when importing the on_change actions are not executed.
    ''',
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : ['menu_items.xml',
                    'wizard/update_sale_order_line_info_view.xml',],
    'active': False,
    'installable': True
}
