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

from osv import osv
from osv import fields

# Ciclo
class expresso_ciclo(osv.osv):
    '''
    Ciclo de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.ciclo'
    _description = 'Ciclo'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True)
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_ciclo()

# Colección
class expresso_coleccion(osv.osv):
    '''
    Coleccion de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.coleccion'
    _description = 'Coleccion'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=50, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_coleccion()

# Curso
class expresso_curso(osv.osv):
    '''
    Curso de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.curso'
    _description = 'Curso'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_curso()

# Encuadernación
class expresso_encuadernacion(osv.osv):
    '''
    Encuadernacion de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.encuadernacion'
    _description = 'Encuadernacion'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_encuadernacion()

# Forma de Envío
class expresso_forma_envio(osv.osv):
    '''
    Formas de Envio de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.forma_envio'
    _description = 'Forma de Envio'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_forma_envio()

# Idioma
class expresso_idioma(osv.osv):
    '''
    Idioma de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.idioma'
    _description = 'Idioma'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=20, required=True, readonly=True),
        'idioma_amigo':fields.boolean('Idioma Amigo', required=False),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_idioma()

# Proyecto
class expresso_proyecto(osv.osv):
    '''
    Proyecto
    '''
    _name = 'expresso.proyecto'
    _description = 'Proyecto'
    _rec_name = 'denominacion'
    
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_proyecto()

# Público Objetivo
class expresso_publico(osv.osv):
    '''
    Público Objetivo de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.publico'
    _description = u'Público Objetivo'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=50, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_publico()

# Situación
class expresso_situacion(osv.osv):
    '''
    Situacion de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.situacion'
    _description = u'Situación'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
        'permite_pedido':fields.boolean('Permite Pedido', required=False),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_situacion()

# Tipo
class expresso_tipo(osv.osv):
    '''
    Tipo de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.tipo'
    _description = 'Tipo'
    _rec_name = 'denominacion'

    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=30, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_tipo()

# Valor
class expresso_valor(osv.osv):
    '''
    Valor de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.valor'
    _description = 'Valor'
    _rec_name = 'denominacion'
	
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion': fields.char(u'Denominación', size=20, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_valor()

# Director
class expresso_director(osv.osv):
    '''
    Director
    '''
    _name = 'expresso.director'
    _description = 'Director'
    _rec_name = 'denominacion'
    
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=50, required=True, readonly=True),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_director()

# Materia
class expresso_materia(osv.osv):
    '''
    Materia de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.materia'
    _description = 'Materia'
    _rec_name = 'denominacion'
    
    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion': fields.char(u'Denominación', size=50, required=True, readonly=True),
        'director_id': fields.many2one('expresso.director', 'Director', required=False),
        'proyecto_id': fields.many2one('expresso.proyecto', 'Proyecto', required=False),
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_materia()

# Seleccion
class expresso_seleccion(osv.osv):
    '''
    Seleccion de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.seleccion'
    _description = 'Seleccion'
    _rec_name = 'denominacion'

    _columns = {
        'id_remoto': fields.char('Identificador Remoto', size=30, required=False, readonly=True),
        'denominacion':fields.char(u'Denominación', size=50, required=True, readonly=True),
        'materia_id':fields.many2one('expresso.materia', 'Materia', required=False),
        'proyecto_id':fields.many2one('expresso.proyecto', 'Proyecto', required=False)
    }
    
    _sql_constraints = [('id_remoto_no_uniq','unique(id_remoto)', 'El Identificador Remoto debe ser unico!')]
    
expresso_seleccion()











