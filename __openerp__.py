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
    'depends': ['ar_account',  'stock', 'pentaho_reports'],
    'init_xml': [],
    'update_xml': [
                                'data/data_Sequence.xml',
                                'data/data_StockJournal.xml',
                                'data/data_PickingReference.xml',
                                'security/ir.model.access.csv',
                                'security/data_Application.xml',
                                'security/data_Groups.xml',
                                'workflow/workflow_Expedition.xml',
                                'report/internal_move.xml',
                                'report/other_incoming_shipment.xml',
                                'report/other_delivery_order.xml',
                                'report/supplier_claim_realization.xml',
                                'report/customer_claim.xml',
                                'report/product_reservation.xml',
                                'report/delivery_order.xml',
                                'report/supplier_claim.xml',
                                'report/incoming_shipment.xml',
                                'report/customer_claim_realization.xml',
                                'report/outgoing_expedition_list.xml',
                                'report/outgoing_expedition_product_list.xml',
                                'wizard/wizard_cancel_stock_picking.xml',
                                'wizard/wizard_forward_picking.xml',
                                'wizard/wizard_invoice_on_picking.xml',
                                'wizard/wizard_stock_partial_picking.xml',
                                'wizard/wizard_deliver_picking.xml',
                                'wizard/wizard_return_picking.xml',
                                'wizard/wizard_split_picking.xml',
                                'view/view_ResCompany.xml',
                                'view/view_StockJournal.xml', 
                                'view/view_IncomingShipment.xml',
                                'view/view_OtherIncomingShipment.xml',
                                'view/view_SupplierClaimRealization.xml',
                                'view/view_CustomerClaim.xml',
                                'view/view_InternalMoves.xml',
                                'view/view_DeliveryOrder.xml',
                                'view/view_OtherDeliveryOrder.xml',
                                'view/view_SupplierClaim.xml',
                                'view/view_CustomerClaimRealization.xml',
                                'view/view_StockLocation.xml',
                                'view/view_ExpeditionCrewPosition.xml',
                                'view/view_OutgoingExpedition.xml',
                                'view/view_OutgoingDirectPicking.xml',
                                'view/view_IncomingExpedition.xml',
                                'view/view_IncomingDirectPicking.xml',
                                'view/view_ProductReservation.xml',
                                'window_action/waction_IncomingShipment.xml',
                                'window_action/waction_SupplierClaimRealization.xml',
                                'window_action/waction_CustomerClaim.xml',
                                'window_action/waction_InternalMoves.xml',
                                'window_action/waction_DeliveryOrder.xml',
                                'window_action/waction_OtherDeliveryOrder.xml',
                                'window_action/waction_SupplierClaim.xml',
                                'window_action/waction_CustomerClaimRealization.xml',
                                'window_action/waction_ExpeditionCrewPosition.xml',
                                'window_action/waction_OutgoingExpedition.xml',
                                'window_action/waction_OutgoingDirectPicking.xml',
                                'window_action/waction_IncomingExpedition.xml',
                                'window_action/waction_IncomingDirectPicking.xml',
                                'window_action/waction_OtherIncomingShipment.xml',
                                'window_action/waction_ProductReservation.xml',
                                'board/board_IncomingMovement.xml',
                                'board/board_InternalMovement.xml',
                                'board/board_OutgoingMovement.xml',
                                'menu/menu_Warehouse.xml',
                                'menu/menu_Setting.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
