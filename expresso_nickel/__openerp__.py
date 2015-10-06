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


{
    'name': 'Nickel connection to the system Expresso Bibliográfico',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    Nickel connection with Expresso Bibliográfico server to upgrade
     information.
     MySQLdb installed (sudo apt-get install python-mysqldb)
    
     To make it work you need to link users Nickel with Expresso.
     To do this go to "Expresso / Administration / Info. Sync. Correspondents" and once
     Nickel users have been loaded, enter each record and add
     Nickel corresponding user.
    """,
    'author': 'ADHOC',
    'website': 'www.adhoc.com.ar',
    'depends': ['expresso_product_attributes'],
    'data': [
            'security/ir.model.access.csv',
            'view/nickel_cliente_view.xml',
            'view/nickel_factura_view.xml',
            'view/invoice_view.xml',
            'view/expresso_sync_info_view.xml',
            # 'view/product_view.xml',
            # 'view/sale_view.xml',
            'view/backup_data.xml',
            'wizard/panel_control_actualizacion_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
