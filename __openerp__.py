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
    'name': 'AR - Stock',
    'version': '1.1',
    'author': 'Andhitia Rama',
    'category': 'Andhitia Rama/Base',
    'complexity': 'easy',
    'website': 'http://andhitiarama.wordpress.com',
    'description': """
    Modul warna
    """,
    'author': 'Andhitia Rama',
    'website': 'http://andhitiarama.wordpress.com',
    'images': [],
    'depends': ['ar_base', 'ar_base_sequence', 'stock'],
    'init_xml': [],
    'update_xml': [
                                'security/ir.model.access.csv',
                                'data/data_StockJournal.xml',
                                'wizard/wizard_cancel_stock_picking.xml',
                                'view/view_StockJournal.xml', 
                                'view/view_IncomingShipment.xml',
                                'view/view_SupplierClaimRealization.xml',
                                'view/view_StockLocation.xml',
                                'view/view_ExpeditionCrewPosition.xml',
                                'window_action/waction_IncomingShipment.xml',
                                'window_action/waction_ExpeditionCrewPosition.xml',
                                'menu/menu_Warehouse.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
