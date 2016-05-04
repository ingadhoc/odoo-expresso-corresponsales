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

import logging
from osv import osv, fields

_logger = logging.getLogger(__name__)

class expresso_info_corresponsal(osv.osv):
    _name = 'expresso.info_corresponsal'
    _inherit = 'expresso.info_corresponsal'
    _columns = {
        'nickel_cliente_id':fields.many2one('nickel_cliente', 'Cliente Nickel', required=False),
    }

expresso_info_corresponsal()







