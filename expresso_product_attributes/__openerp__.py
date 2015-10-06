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
    'name': 'Atributos para Productos de Expresso Bibliográfico',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Atributos para Productos de Expresso Bibliográfico.
Requiere instalar python-suds 4.1+
- Una vez instalado probar de ir a Corresponsales -> Pedidos -> Nuevo Pedido, si
abre un pedido en vista de formulario esta bien. Sino, ir a Administración ->
Personalización -> Objetos de bajo nivel -> Acciones -> Acciones de Ventana, buscar
'Nuevo Pedido', abrirlo y checkear que en 'Tipo de vista' este asignado 'Formulario'
y que en 'Modo de vista' figure 'form,tree'.
    """,
    'author': 'ADHOC',
    'website': 'www.adhoc.com.ar',
    'depends': ['sale', 'stock'],
    'data': [
            'security/expresso_security.xml',
            'security/ir.model.access.csv',
            'security/permisos_corresponsales.xml',
            'security/permisos_expresso.xml',
            'view/expresso_product_view.xml',
            'view/ir_values_data.xml',
            'view/product_view.xml',
            'view/sale_view.xml',
            'view/sale_workflow.xml',
            'view/invoice_view.xml',
            'view/product_workflow.xml',
            'view/partner_data.xml',
            'view/expresso_sync_info_view.xml',
            'view/res_user_view.xml',
            'view/expresso_packing_view.xml',
            'view/acciones_generales.xml',
            'view/expresso_menu.xml',
            'view/corresponsales_menu.xml',
            'wizard/repedir_pendiente_view.xml',
            'wizard/generar_pendiente_view.xml',
            'wizard/pedir_multi_titulos_view.xml',
            'wizard/panel_control_actualizacion_view.xml',
            'wizard/multi_marcar_para_procesar_view.xml',
            'view/partner_view.xml',
            # TODO borrar si no lo vamos a usar
            # 'data/expresso_sync_info_data.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
