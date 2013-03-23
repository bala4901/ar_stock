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
from datetime import datetime
from tools.translate import _

class stock_picking(osv.osv):
	_name = 'stock.picking'
	_inherit = 'stock.picking'

	def default_name(self, cr, uid, context={}):
		"""
	
		"""
		return '-'
	
	def default_create_time(self, cr, uid, context={}):
		"""
	
		"""
		return datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
	
	def default_create_user_id(self, cr, uid, context={}):
		"""
	
		"""
		return uid
	
	
	def default_stock_journal_id(self, cr, uid, context={}):
		"""
	
		"""
		if not context:
			context = {}
		
		stock_journal = context.get('stock_journal', False)
		stock_journal_id = False

		if stock_journal:			
			obj_stock_journal = self.pool.get('stock.journal')
			stock_journal_ids = obj_stock_journal.search(cr, uid, [('name','=',stock_journal)])
			if stock_journal_ids : stock_journal_id = stock_journal_ids[0]
		
		return stock_journal_id
	
	def default_location_id(self, cr, uid, context={}):
		"""
		"""
		obj_stock_journal = self.pool.get('stock.journal')
	
		stock_journal_id = self.default_stock_journal_id(cr, uid, context)
		if not stock_journal_id : return False
	
		stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
	
		return stock_journal.default_location_id and  stock_journal.default_location_id.id or False
	
	def default_location_dest_id(self, cr, uid, context={}):
		"""
	
		"""
		obj_stock_journal = self.pool.get('stock.journal')
	
		stock_journal_id = self.default_stock_journal_id(cr, uid, context)
		if not stock_journal_id : return False
	
		stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
	
		return stock_journal.default_location_dest_id and  stock_journal.default_location_dest_id.id or False		
	
	def default_invoice_state(self, cr, uid, context={}):
		"""
	
		"""
		obj_stock_journal = self.pool.get('stock.journal')
	
		stock_journal_id = self.default_stock_journal_id(cr, uid, context)
		if not stock_journal_id : return False
	
		stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
	
		return stock_journal.default_invoice_state
	
	_columns =	{
							'create_user_id' : fields.many2one(obj='res.users', string='Created By', readonly=True),
							'create_time' : fields.datetime(string='Creation Time', readonly=True),
							'confirm_user_id' : fields.many2one(obj='res.users', string='Confirmed By', readonly=True),
							'confirm_time' : fields.datetime(string='Confimation Time', readonly=True),							
							'process_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'process_time' : fields.datetime(string='Processed Time', readonly=True),		
							'cancel_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'cancel_time' : fields.datetime(string='Cancelled Time', readonly=True),									
							'cancel_description' : fields.text(string='Cancel Description', readonly=True),
							}				
	
	_defaults =	{
							'name' : default_name,
							'stock_journal_id' : default_stock_journal_id,
							'location_id' : default_location_id,
							'location_dest_id' : default_location_dest_id,
							'invoice_state' : default_invoice_state,
							'create_user_id' : default_create_user_id,
							'create_time' : default_create_time,
							}

	def onchange_stock_journal_id(self, cr, uid, ids, stock_journal_id):
		value = {}
		domain = {}
		warning = {}
	
		obj_stock_journal = self.pool.get('stock.journal')
	
		if stock_journal_id:
			stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
			val =	{
						'type' : stock_journal.default_type,
						'invoice_status' : stock_journal.default_invoice_state,
						}
			value.update(val)
		
		return {'value' : value, 'domain' : domain, 'warning' : warning}
	
	def create_sequence(self, cr, uid, id):
		"""
	
		"""
		obj_sequence = self.pool.get('ir.sequence')
	
		picking = self.browse(cr, uid, [id])[0]
	
		if not picking.stock_journal_id.default_sequence_id:
			raise osv.except_osv('Warning!', 'There is no sequence defined')
			return False
		
		sequence_id = picking.stock_journal_id.default_sequence_id.id
		sequence = obj_sequence.next_by_id(cr, uid, sequence_id)
		self.write(cr, uid, [id], {'name' : sequence})
	
		return True
	
	def action_confirm(self, cr, uid, ids, context=None):
		for id in ids:
			if not self.create_sequence(cr, uid, id):
				return False
				
		val =	{
					'confirm_user_id' : uid,
					'confirm_time' : datetime.today().strftime('%Y-%m-%d %H:%M:%S')
					}
					
		self.write(cr, uid, ids, val)
			
		return super(stock_picking, self).action_confirm(cr, uid, ids, context)
	
	def action_process(self, cr, uid, ids, context=None):
		if context is None : context = {}
		context = dict(context, active_ids=ids, active_model=context.get('inherit_model', self._name))
		partial_id = self.pool.get('stock.partial.picking').create(cr, uid, {}, context=context)
		return {
		    'name':_('Products to Process'),
		    'view_mode': 'form',
		    'view_id': False,
		    'view_type': 'form',
		    'res_model': 'stock.partial.picking',
		    'res_id': partial_id,
		    'type': 'ir.actions.act_window',
		    'nodestroy': True,
		    'target': 'new',
		    'domain': '[]',
		    'context': context,
		}		
		
	def action_done(self, cr, uid, ids, context=None):
		val =	{
					'process_user_id' : uid,
					'process_time' : datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
					}
					
		self.write(cr, uid, ids, val)
		
		return super(stock_picking, self).action_done(cr, uid, ids, context)
		
	def action_cancel(self, cr, uid, ids, context=None):
		val =	{
					'cancel_user_id' : uid,
					'cancel_time' : datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
					}
					
		self.write(cr, uid, ids, val)
		
		return super(stock_picking, self).action_cancel(cr, uid, ids, context)	
		
	def copy(self, cr, uid, id, default=None, context=None):
		if default is None:
			default = {}
		
		default = default.copy()
		
		res	=	{
					'create_user_id' : uid,
					'create_time' : datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
					'confirm_user_id' : False,
					'confirm_time' : False,
					'process_user_id' : False,
					'process_time' : False,
					'cancel_time' : False,
					'cancel_user_id' : False,
					'cancel_description' : False,
					}
					
		default.update(res)
		
		return super(stock_picking, self).copy(cr, uid, id, default, context)
					
		
		
	
					
		

			
		
		
		


stock_picking()




