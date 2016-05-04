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
    'name': 'Conexión con el sistema Nickel de Expresso Bibliográfico',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    Conexión con el servir Nickel de Expresso Bibliográfico para la actualización
    de información.
    
    Instalar MySQLdb (sudo apt-get install python-mysqldb)
    
    Para que funcione es necesario enlazar los usuarios de Nickel con los de Expresso.
    Para esto ir a "Expresso / Administración / Info. Sync. Corresponsales" y una vez
    que se hayan cargado los usuarios de Nickel, entrar a cada registro y agregarle
    el usuario de Nickel correspondiente.
    """,
    'author': 'ADHOC Sistemas',
    'website': 'http://www.adhocsistemas.com.ar/',
    'depends': ['expresso_product_attributes'],
    'init_xml': [],
    'update_xml': [
            'security/permisos_corresponsales.xml',
            'security/permisos_expresso.xml',
            'nickel_cliente_view.xml',
            'nickel_factura_view.xml',
            'invoice_view.xml',
            'expresso_sync_info_view.xml',
            'product_view.xml',
            'sale_view.xml',
            'wizard/panel_control_actualizacion_view.xml',],
    'demo_xml': [],
    'test':[],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
