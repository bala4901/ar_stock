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
import netsvc

class stock_picking(osv.osv):
	_name = 'stock.picking'
	_inherit = 'stock.picking'

	def default_name(self, cr, uid, context={}):
		"""

		"""
		return '/'

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
		
	def selection_picking_reference(self, cr, uid, context={}):
		obj_model = self.pool.get('ir.model')
		
		model_ids = obj_model.search(cr, uid, [])
		selection_result = []
		
		if model_ids:
			res = obj_model.read(cr, uid, model_ids,  ['model', 'name'])
			return [(r['model'], r['name']) for r in res] +  [('','')]
		else:
			return []
			

	_columns =	{
							'picking_reference_id' : fields.reference(string='Reference', selection=selection_picking_reference, readonly=True, size=256),
							'create_user_id' : fields.many2one(obj='res.users', string='Created By', readonly=True),
							'create_time' : fields.datetime(string='Creation Time', readonly=True),
							'confirm_user_id' : fields.many2one(obj='res.users', string='Confirmed By', readonly=True),
							'confirm_time' : fields.datetime(string='Confimation Time', readonly=True),							
							'process_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'process_time' : fields.datetime(string='Processed Time', readonly=True),		
							'cancel_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'cancel_time' : fields.datetime(string='Cancelled Time', readonly=True),									
							'cancel_description' : fields.text(string='Cancel Description', readonly=True),
							'allowed_location_id' : fields.related(string='Allowed Location Ids', f1='stock_journal_id',f2='allowed_location_ids', type='many2many', obj='stock.location'),			
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
		x = []
		y = []

		obj_stock_journal = self.pool.get('stock.journal')

		if stock_journal_id:
			stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
			
			val =	{
						'type' : stock_journal.default_type,
						'invoice_status' : stock_journal.default_invoice_state,
						}
			value.update(val)
			if stock_journal.allowed_location_ids:
				for location in stock_journal.allowed_location_ids:
					x.append(location.id)
					
			if stock_journal.allowed_location_dest_ids:
				for dest_location in stock_journal.allowed_location_dest_ids:
					y.append(dest_location.id)
					
			if x and y:
				domain = {'location_id': [('id','in',x)] ,'location_dest_id': [('id','in',y)] }
			elif x and not y:
				domain = {'location_id': [('id','in',x)],'location_dest_id': [('id','=',0)] }
			elif y and not x:
				domain = {'location_id': [('id','=',0)],'location_dest_id': [('id','in',y)] }
			else:
				domain = {'location_id': [('id','=',0)],'location_dest_id': [('id','=',0)] }
					
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
		
	def create(self, cr, uid, vals, context=None):
		vals.update({'name' : 'xxx'})
	
		new_id = super(stock_picking, self).create(cr, uid, vals, context)
		
		if not self.create_sequence(cr, uid, new_id):
			return False
			
		return new_id
	
	def do_partial(self, cr, uid, ids, partial_datas, context=None):
		""" Makes partial picking and moves done.
		@param partial_datas : Dictionary containing details of partial picking
				          like partner_id, address_id, delivery_date,
				          delivery moves with product_id, product_qty, uom
		@return: Dictionary of values
		"""
		if context is None:
			context = {}
		else:
			context = dict(context)
		res = {}
		move_obj = self.pool.get('stock.move')
		product_obj = self.pool.get('product.product')
		currency_obj = self.pool.get('res.currency')
		uom_obj = self.pool.get('product.uom')
		sequence_obj = self.pool.get('ir.sequence')
		wf_service = netsvc.LocalService("workflow")
		for pick in self.browse(cr, uid, ids, context=context):
			new_picking = None
			complete, too_many, too_few = [], [], []
			move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
			for move in pick.move_lines:
				if move.state in ('done', 'cancel'):
				    continue
				partial_data = partial_datas.get('move%s'%(move.id), {})
				product_qty = partial_data.get('product_qty',0.0)
				move_product_qty[move.id] = product_qty
				product_uom = partial_data.get('product_uom',False)
				product_price = partial_data.get('product_price',0.0)
				product_currency = partial_data.get('product_currency',False)
				prodlot_id = partial_data.get('prodlot_id')
				prodlot_ids[move.id] = prodlot_id
				product_uoms[move.id] = product_uom
				partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
				if move.product_qty == partial_qty[move.id]:
				    complete.append(move)
				elif move.product_qty > partial_qty[move.id]:
				    too_few.append(move)
				else:
				    too_many.append(move)

				# Average price computation
				if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
				    product = product_obj.browse(cr, uid, move.product_id.id)
				    move_currency_id = move.company_id.currency_id.id
				    context['currency_id'] = move_currency_id
				    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

				    if product.id in product_avail:
				        product_avail[product.id] += qty
				    else:
				        product_avail[product.id] = product.qty_available

				    if qty > 0:
				        new_price = currency_obj.compute(cr, uid, product_currency,
				                move_currency_id, product_price)
				        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
				                product.uom_id.id)
				        if product.qty_available <= 0:
				            new_std_price = new_price
				        else:
				            # Get the standard price
				            amount_unit = product.price_get('standard_price', context=context)[product.id]
				            new_std_price = ((amount_unit * product_avail[product.id])\
				                + (new_price * qty))/(product_avail[product.id] + qty)
				        # Write the field according to price type field
				        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

				        # Record the values that were chosen in the wizard, so they can be
				        # used for inventory valuation if real-time valuation is enabled.
				        move_obj.write(cr, uid, [move.id],
				                {'price_unit': product_price,
				                 'price_currency_id': product_currency})


			for move in too_few:
				product_qty = move_product_qty[move.id]
				if not new_picking:
				    new_picking = self.copy(cr, uid, pick.id,
				            {
				                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
				                'move_lines' : [],
				                'state':'draft',
				            })
				if product_qty != 0:
				    defaults = {
				            'product_qty' : product_qty,
				            'product_uos_qty': product_qty, #TODO: put correct uos_qty
				            'picking_id' : new_picking,
				            'state': 'assigned',
				            'move_dest_id': False,
				            'price_unit': move.price_unit,
				            'product_uom': product_uoms[move.id]
				    }
				    prodlot_id = prodlot_ids[move.id]
				    if prodlot_id:
				        defaults.update(prodlot_id=prodlot_id)
				    move_obj.copy(cr, uid, move.id, defaults)
				move_obj.write(cr, uid, [move.id],
				        {
				            'product_qty' : move.product_qty - partial_qty[move.id],
				            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
				            
				        })

			if new_picking:
				move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
			for move in complete:
				defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
				if prodlot_ids.get(move.id):
				    defaults.update({'prodlot_id': prodlot_ids[move.id]})
				move_obj.write(cr, uid, [move.id], defaults)
			for move in too_many:
				product_qty = move_product_qty[move.id]
				defaults = {
				    'product_qty' : product_qty,
				    'product_uos_qty': product_qty, #TODO: put correct uos_qty
				    'product_uom': product_uoms[move.id]
				}
				prodlot_id = prodlot_ids.get(move.id)
				if prodlot_ids.get(move.id):
				    defaults.update(prodlot_id=prodlot_id)
				if new_picking:
				    defaults.update(picking_id=new_picking)
				move_obj.write(cr, uid, [move.id], defaults)

			# At first we confirm the new picking (if necessary)
			if new_picking:
				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
				# Then we finish the good picking
				self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
				self.action_move(cr, uid, [new_picking])
				wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
				wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
				delivered_pack_id = new_picking
				
				new_pick = self.browse(cr, uid, [new_picking])[0]
				new_pick_name = new_pick.name
				pick_name = pick.name
				self.write(cr, uid, [pick.id], {'name' : 'temp1'})
				self.write(cr, uid, [new_picking], {'name':pick_name})
				self.write(cr, uid, [pick.id], {'name':new_pick_name})			    
			else:
				self.action_move(cr, uid, [pick.id])
				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
				delivered_pack_id = pick.id

			delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
			res[pick.id] = {'delivered_picking': delivered_pack.id or False}
			


		return res
					
		
		
	
					
		

			
		
		
		


stock_picking()




