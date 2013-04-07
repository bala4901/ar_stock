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
    'category': 'AR/Stock',
    'complexity': 'easy',
    'website': 'http://andhitiarama.wordpress.com',
    'description': """
    -
    """,
    'author': 'Andhitia Rama & Michael Viriyananda',
    'website': 'http://andhitiarama.wordpress.com',
    'images': [],
    'depends': ['ar_base', 'ar_base_sequence', 'stock', 'pentaho_reports'],
    'init_xml': [],
    'update_xml': [
                                'security/ir.model.access.csv',
                                'data/data_Sequence.xml',
                                'data/data_StockJournal.xml',
                                'data/data_PickingReference.xml',
                                'ar_stock_report.xml',
                                'wizard/wizard_cancel_stock_picking.xml',
                                'wizard/wizard_forward_picking.xml',
                                'view/view_StockJournal.xml', 
                                'view/view_IncomingShipment.xml',
                                'view/view_SupplierClaimRealization.xml',
                                'view/view_CustomerClaim.xml',
                                'view/view_InternalMoves.xml',
                                'view/view_DeliveryOrder.xml',
                                'view/view_SupplierClaim.xml',
                                'view/view_CustomerClaimRealization.xml',
                                'view/view_StockLocation.xml',
                                'view/view_ExpeditionCrewPosition.xml',
                                'view/view_Expedition.xml',
                                'window_action/waction_IncomingShipment.xml',
                                'window_action/waction_SupplierClaimRealization.xml',
                                'window_action/waction_CustomerClaim.xml',
                                'window_action/waction_InternalMoves.xml',
                                'window_action/waction_DeliveryOrder.xml',
                                'window_action/waction_SupplierClaim.xml',
                                'window_action/waction_CustomerClaimRealization.xml',
                                'window_action/waction_ExpeditionCrewPosition.xml',
                                'window_action/waction_Expedition.xml',
                                'menu/menu_Warehouse.xml',
                                'menu/menu_Setting.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
