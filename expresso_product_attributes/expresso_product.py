# -*- coding: utf-8 -*-
from openerp import models, fields


class expresso_ciclo(models.Model):

    '''
    Ciclo de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.ciclo'
    _description = 'Ciclo'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False,
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_coleccion(models.Model):

    # Coleccion de los productos de Expresso Bibliogáfico

    _name = 'expresso.coleccion'
    _description = 'Coleccion'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False,
        )
    denomination = fields.Char(
        'Denominación',
        size=50,
        required=True,
        readonly=True)

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_curso(models.Model):

        # Curso de los productos de Expresso Bibliogáfico

    _name = 'expresso.curso'
    _description = 'Curso'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_encuadernacion(models.Model):

    # Encuadernacion de los productos de Expresso Bibliogáfico

    _name = 'expresso.encuadernacion'
    _description = 'Encuadernacion'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_forma_envio(models.Model):

    # Formas de Envio de los productos de Expresso Bibliogáfico

    _name = 'expresso.forma_envio'
    _description = 'Forma de Envio'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True)

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_idioma(models.Model):

    # Idioma de los productos de Expresso Bibliogáfico

    _name = 'expresso.idioma'
    _description = 'Idioma'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=20,
        required=True,
        readonly=True
        )
    idioma_amigo = fields.Boolean('Idioma Amigo')

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_proyecto(models.Model):

    # Proyecto

    _name = 'expresso.proyecto'
    _description = 'Proyecto'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_publico(models.Model):

    # Público Objetivo de los productos de Expresso Bibliogáfico

    _name = 'expresso.publico'
    _description = 'Público Objetivo'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=50,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_situacion(models.Model):

    # Situacion de los productos de Expresso Bibliogáfico

    _name = 'expresso.situacion'
    _description = 'Situación'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True
        )
    permite_pedido = fields.Boolean(
        'Permite Pedido'
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_tipo(models.Model):

    '''
    Tipo de los productos de Expresso Bibliogáfico
    '''
    _name = 'expresso.tipo'
    _description = 'Tipo'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=30,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_valor(models.Model):

    # Valor de los productos de Expresso Bibliogáfico

    _name = 'expresso.valor'
    _description = 'Valor'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=20,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


# Director


class expresso_director(models.Model):

    # Director

    _name = 'expresso.director'
    _description = 'Director'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=50,
        required=True,
        readonly=True
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_materia(models.Model):

    # Materia de los productos de Expresso Bibliogáfico

    _name = 'expresso.materia'
    _description = 'Materia'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=50,
        required=True,
        readonly=True
        )
    director_id = fields.Many2one(
        'expresso.director',
        'Director'
        )
    proyecto_id = fields.Many2one(
        'expresso.proyecto',
        'Proyecto'
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]


class expresso_seleccion(models.Model):

    # Seleccion de los productos de Expresso Bibliogáfico

    _name = 'expresso.seleccion'
    _description = 'Seleccion'
    _rec_name = 'denomination'

    remote_id = fields.Char(
        'Identificador Remoto',
        size=30,
        readonly=True,
        copy=False
        )
    denomination = fields.Char(
        'Denominación',
        size=50,
        required=True,
        readonly=True
        )
    matter_id = fields.Many2one(
        'expresso.materia',
        'Matter'
        )
    project_id = fields.Many2one(
        'expresso.proyecto',
        'Project'
        )

    _sql_constraints = [
        ('remote_id_no_uniq',
            'unique(remote_id)', 'El Identificador Remoto debe ser unico!')]
