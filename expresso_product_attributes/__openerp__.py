# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
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
    'name': 'Atributos para Productos de Expresso Bibliográfico',
    'version': '9.0.1.0.0',
    'category': 'Tools',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'depends': ['sale', 'stock'],
    'data': [
            # 'security/expresso_security.xml',
            # 'security/ir.model.access.csv',
            'security/permisos_expresso.xml',
            'view/expresso_product_view.xml',
            'view/product_view.xml',
            'view/sale_empresa_logistica_view.xml',
            'view/sale_order_view.xml',
            # 'view/ir_values_data.xml',
            # 'view/sale_workflow.xml',
            'view/invoice_view.xml',
            # 'view/product_workflow.xml',
            'view/expresso_sync_info_view.xml',
            'view/expresso_packing_view.xml',
            # menus y accions
            'view/acciones_generales.xml',
            'view/expresso_menu.xml',
            'wizard/repedir_pendiente_view.xml',
            'wizard/generar_pendiente_view.xml',
            'wizard/panel_control_actualizacion_view.xml',
            'wizard/multi_marcar_para_procesar_view.xml',
    ],
    'demo': [
        'demo/users_demo.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
