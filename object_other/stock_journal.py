# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields, osv

class stock_journal(osv.osv):
	_name = 'stock.journal'
	_inherit = 'stock.journal'

	_columns =	{
							'default_type' : fields.selection(selection=[('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], string='Default Type'),
							'default_invoice_state' : fields.selection(selection=[('invoiced', 'Invoiced'),('2binvoiced', 'To Be Invoiced'),('none', 'Not Applicable')], string='Default Invoice Type'),
							'default_sequence_id' : fields.many2one(obj='ir.sequence', string='Sequence', domain=[('code','=','stock.picking')]),
							'allow_location_selection' : fields.boolean(string='Allow Location Selection'),
							'allow_dest_location_selection' : fields.boolean(string='Allow Destination Location Selection'),
							'default_location_id' : fields.many2one(obj='stock.location', string='Default Location', domain=[('usage','!=','view')]),
							'default_location_dest_id' : fields.many2one(obj='stock.location', string='Default Destination Location', domain=[('usage','!=','view')]),
							'allowed_location_ids' : fields.many2many(obj='stock.location', rel='stock_journal_location_rel', id1='stock_journal_id', id2='location_id', domain=[('usage','!=','view')]),
							'allowed_location_dest_ids' : fields.many2many(obj='stock.location', rel='stock_journal_location_dest_rel', id1='stock_journal_id', id2='location_id', domain=[('usage','!=','view')]),
							'allowed_return_product' : fields.boolean(string='Allowed Forward Product'),
							'allowed_forward_stock_journal_ids' : fields.many2many(obj='stock.journal', rel='stock_journal_stock_journal_rel', id1='stock_journal1_id', id2='stock_journal2_id'),
							'allowed_account_journal_ids' : fields.many2many(obj='account.journal', rel='stock_journal_account_journal_rel', id1='stock_journal_id', id2='account_journal_id'),
							'stock_journal_return_id' : fields.many2one(string='Return Stock Journal', obj='stock.journal'),
							'allowed_invoicing' : fields.boolean(string='Allow Create Invoice/Refund'),
							'invoice_type' : fields.selection(string='Invoice Type', selection=[('out_invoice','Customer Invoice'),('in_invoice','Supplier Invoice'),('out_refund','Customer Refund'),('in_refund','Supplier Refund')]),
							'invoice_journal_id' : fields.many2one(string='Invoice/Refund Journal', obj='account.journal', domain=['|','|','|',('type','=','sale'),('type','=','sale_refund'),('type','=','purchase'),('type','=','purchase_refund')]),
							'model_name' : fields.char(string='Model Name', size=100),
							'model_view_form' : fields.char(string='Model View Form', size=100),		
							'modul_origin' : fields.char(string='Modul Origin', size=100),							
							'invoice_type_id' : fields.many2one(string='Invoice Type', obj='account.invoice_type'),
							}


stock_journal()




