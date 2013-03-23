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
							'default_sequence_id' : fields.many2one(obj='ir.sequence', string='Sequence'),
							'default_location_id' : fields.many2one(obj='stock.location', string='Default Location', domain=[('usage','!=','view')]),
							'default_location_dest_id' : fields.many2one(obj='stock.location', string='Default Destination Location', domain=[('usage','!=','view')]),
							'allowed_location_ids' : fields.many2many(obj='stock.location', rel='stock_journal_location_rel', id1='stock_journal_id', id2='location_id', domain=[('usage','!=','view')]),
							'allowed_location_dest_ids' : fields.many2many(obj='stock.location', rel='stock_journal_location_dest_rel', id1='stock_journal_id', id2='location_id', domain=[('usage','!=','view')]),
							}


stock_journal()




