# Script modificacion isbn a registros remotos

import os
import datetime
from lxml import etree

base_directory = '/home/damian/Desarrollo/addons/expresso/expresso_product_attributes_data/'
files = ['product_data_1.xml', 'product_data_2.xml', 'product_data_3.xml', 'product_data_4.xml']

for file_name in files:
    xml_file = os.path.dirname(base_directory)
    xml_file = os.path.join(xml_file, file_name)
    
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    openerp = etree.Element('openerp')
    data = etree.SubElement(openerp, 'data')
    
    for record in root[0]:
        isbn = record[0].text
        record_obj_remoto = etree.SubElement(data, 'record')
        record_obj_remoto.set('id', 'expresso_info_objeto_remoto_' + isbn)
        record_obj_remoto.set('model', 'expresso.info_objeto_remoto')
        
        field_id_remoto = etree.SubElement(record_obj_remoto, 'field')
        field_id_remoto.set('name', 'id_remoto')
        field_id_remoto.text = isbn
        
        field_class = etree.SubElement(record_obj_remoto, 'field')
        field_class.set('name', 'class')
        field_class.text = 'product.product'
        
        record_sync = etree.SubElement(data, 'record')
        record_sync.set('id', 'sync_' + isbn)
        record_sync.set('model', 'expresso.sincronizacion_objeto_remoto')
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        field_datetime_creation = etree.SubElement(record_sync, 'field')
        field_datetime_creation.set('name', 'datetime_creation')
        field_datetime_creation.text = now
        
        field_info_objeto_remoto_id = etree.SubElement(record_sync, 'field')
        field_info_objeto_remoto_id.set('name', 'info_objeto_remoto_id')
        field_info_objeto_remoto_id.set('ref', 'expresso_info_objeto_remoto_' + isbn)
    
    xml_file = os.path.dirname(base_directory)
    xml_file = os.path.join(xml_file, 'new_' + file_name)
    t = etree.ElementTree(openerp)
    t.write(xml_file, pretty_print=True)








