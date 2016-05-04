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
    'author': 'ADHOC Sistemas',
    'website': 'http://www.adhocsistemas.com.ar/',
    'depends': ['sale'],
    'init_xml': [],
    'update_xml': [
            'security/expresso_security.xml',
            'security/ir.model.access.csv',
            'security/permisos_corresponsales.xml',
            'security/permisos_expresso.xml',
            
            'wizard/order_add_message_view.xml',
            
            'expresso_product_view.xml',
            'ir_values_data.xml',
            'product_view.xml',
            'sale_view.xml',
            'sale_workflow.xml',
            'invoice_view.xml',
            'product_workflow.xml',
            'partner_data.xml',
            'expresso_sync_info_view.xml',
            'expresso_sync_info_data.xml',
            'res_user_view.xml',
            'expresso_packing_view.xml',
            
            'acciones_generales.xml',
            
            'expresso_menu.xml',
            'corresponsales_menu.xml',
            
            'wizard/repedir_pendiente_view.xml',
            'wizard/generar_pendiente_view.xml',
            'wizard/pedir_multi_titulos_view.xml',
            'wizard/panel_control_actualizacion_view.xml',
            'wizard/multi_marcar_para_procesar_view.xml',
            
            'report/sale_report_view.xml',
            'sale_report.xml',
            'partner_view.xml',],
    'demo_xml': [],
    'test':[],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
