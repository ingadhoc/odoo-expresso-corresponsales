# -*- coding: utf-8 -*-
from openerp import models, fields
# from openerp.exceptions import Warning


class sale_empresa_logistica(models.Model):

    _name = 'sale.empresa_logistica'
    _description = 'Empresa de Logistica'
    _rec_name = 'name'

    name = fields.Char(
        'Nombre',
        size=100,
        required=True,
        readonly=False
    )
    _sql_constraints = [
        ('name_no_uniq', 'unique(name)', 'El nombre debe ser unico!')]
