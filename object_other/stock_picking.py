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
		#raise osv.except_osv(_('Error !'), _('%s')%stock_journal_id)
	
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
		
	def default_type(self, cr, uid, context={}):
		"""


		"""
		obj_stock_journal = self.pool.get('stock.journal')

		stock_journal_id = self.default_stock_journal_id(cr, uid, context)

		if not stock_journal_id : return False

		stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]

		return stock_journal.default_type
		
	def selection_picking_reference(self, cr, uid, context={}):
		obj_model = self.pool.get('ir.model')
		
		model_ids = obj_model.search(cr, uid, [])
		selection_result = []
		
		if model_ids:
			res = obj_model.read(cr, uid, model_ids,  ['model', 'name'])
			return [(r['model'], r['name']) for r in res] +  [('','')]
		else:
			return []
			
	def function_reference_num(self, cr, uid, ids, field_name, args, context=None):
		res = {}
		
		obj_stock_picking = self.pool.get('stock.picking')
		
		for picking in obj_stock_picking.browse(cr, uid, ids):
			if picking.picking_reference_id:
				res[picking.id] = picking.picking_reference_id.name
				#raise osv.except_osv(_('Error !'), _('%s')%picking.picking_reference_id.name)
		return res
			
	_columns =	{
							'name' : fields.char(string='# Picking', size=64, select='1'),
							'location_id': fields.many2one('stock.location', 'Location', help="Keep empty if you produce at the location where the finished products are needed." \
									"Set a location if you produce at a fixed location. This can be a partner location " \
									"if you subcontract the manufacturing operations.",readonly=True, select=True, states={'draft': [('readonly', False)]}),
							'location_dest_id': fields.many2one('stock.location', 'Dest. Location',help="Location where the system will stock the finished products.", select=True,readonly=True, states={'draft': [('readonly', False)]}),
							'picking_reference_id' : fields.reference(string='Reference', selection=selection_picking_reference, readonly=True, size=256),
							'expedition_id' : fields.many2one(string='Expedition', obj='stock.expedition'),
							'create_user_id' : fields.many2one(obj='res.users', string='Created By', readonly=True),
							'create_time' : fields.datetime(string='Creation Time', readonly=True),
							'confirm_user_id' : fields.many2one(obj='res.users', string='Confirmed By', readonly=True),
							'confirm_time' : fields.datetime(string='Confimation Time', readonly=True),							
							'process_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'process_time' : fields.datetime(string='Processed Time', readonly=True),		
							'cancel_user_id' : fields.many2one(obj='res.users', string='Processed By', readonly=True),
							'cancel_time' : fields.datetime(string='Cancelled Time', readonly=True),									
							'cancel_description' : fields.text(string='Cancel Description', readonly=True),	
							'reference_num' : fields.function(fnct=function_reference_num, string='Reference', type='char', method=True, store=True)
							}				

	_defaults =	{
							'name' : default_name,
							'stock_journal_id' : default_stock_journal_id,
							'location_id' : default_location_id,
							'location_dest_id' : default_location_dest_id,
							'invoice_state' : default_invoice_state,
							'type' : default_type,
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
		
	def onchange_location_dest_id(self, cr, uid, ids, location_dest_id):
		"""
		Ini dipake ga yah?
		"""
		
		return {'value': {'move_lines.location_dest_id': location_dest_id or False}}
		
	def log_picking(self, cr, uid, ids, context=None):
		""" This function will create log messages for picking.
		@param cr: the database cursor
		@param uid: the current user's ID for security checks,
		@param ids: List of Picking Ids
		@param context: A standard dictionary for contextual values
		"""
		if context is None:
		    context = {}
		    
		data_obj = self.pool.get('ir.model.data')
		
		for pick in self.browse(cr, uid, ids, context=context):
			msg=''

			if pick.auto_picking:
				continue

			type_list = pick.stock_journal_id and pick.stock_journal_id.name or _('Document')
		
			view_list = {
				'out': 'view_picking_out_form',
				'in': 'view_picking_in_form',
				'internal': 'view_picking_form',
			}

			message = type_list + " '" + (pick.name or '?') + "' "

			if pick.min_date:
				msg= _(' for the ')+ datetime.strptime(pick.min_date, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')
				
			state_list = {
				'confirmed': _('is scheduled %s.') % msg,
				'assigned': _('is ready to process.'),
				'cancel': _('is cancelled.'),
				'done': _('is done.'),
				'auto': _('is waiting.'),
				'draft': _('is in draft state.'),
			}
			
			res = data_obj.get_object_reference(cr, uid, pick.stock_journal_id.modul_origin, pick.stock_journal_id.model_view_form)
			
			res_context =	{
										'view_id' : res and res[1] or False,
										}
			
			context.update(res_context)
			message += state_list[pick.state]
			self.log(cr, uid, pick.id, message, context=context)
		return True
        		

	def create_sequence(self, cr, uid, id):
		"""

		"""
		obj_sequence = self.pool.get('ir.sequence')

		picking = self.browse(cr, uid, [id])[0]

		if not picking.stock_journal_id.default_sequence_id:
			raise osv.except_osv('Warning!', 'There is no sequence defined')
			return False
			
		if picking.date:
			tanggal = picking.date
		else:
			tanggal = datetime.now().strftime('%Y-%m-%d')
	
		sequence_id = picking.stock_journal_id.default_sequence_id.id

		sequence = obj_sequence.next_by_id(cr, uid, sequence_id, context={'tanggal' : tanggal})
		
		self.write(cr, uid, [id], {'name' : sequence})

		return True
		
	def update_location_dest_id(self, cr, uid, id):
		"""

		"""
		obj_stock_move = self.pool.get('stock.move')

		picking = self.browse(cr, uid, [id])[0]
		
		stock_move_ids = obj_stock_move.search(cr, uid, [('picking_id','=',picking.id)])
		
		for stock_move in obj_stock_move.browse(cr, uid, stock_move_ids):
			if stock_move.location_dest_id.id <> picking.location_dest_id.id:
				obj_stock_move.write(cr, uid, [stock_move.id], {'location_dest_id' : picking.location_dest_id.id})
		return True
		
	def update_location_id(self, cr, uid, id):
		"""

		"""
		obj_stock_move = self.pool.get('stock.move')

		picking = self.browse(cr, uid, [id])[0]
		
		stock_move_ids = obj_stock_move.search(cr, uid, [('picking_id','=',picking.id)])
		
		for stock_move in obj_stock_move.browse(cr, uid, stock_move_ids):
			if stock_move.location_id.id <> picking.location_id.id:
				obj_stock_move.write(cr, uid, [stock_move.id], {'location_id' : picking.location_id.id})
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
			
		if not self.update_location_dest_id(cr, uid, new_id):
			return False
			
		if not self.update_location_id(cr, uid, new_id):
			return False
			
		return new_id

	def write(self,cr, uid, ids, vals, context=None):
		obj_stock_move = self.pool.get('stock.move')
		
		stock_move_ids = obj_stock_move.search(cr, uid, [('picking_id','in',ids)])
		
		if stock_move_ids:
			for stock_move in obj_stock_move.browse(cr, uid, stock_move_ids):
				if 'location_id' in vals:
					obj_stock_move.write(cr, uid, [stock_move.id], {'location_id' : vals['location_id']})
				elif 'location_dest_id' in vals:
					obj_stock_move.write(cr, uid, [stock_move.id], {'location_dest_id' : vals['location_dest_id']})
		
		return super(stock_picking,self).write(cr, uid, ids, vals, context=context)
	
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
                                    name = sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type))
                                    #raise osv.except_osv(_('Warning'), _('%s')%(pick.id))
				    new_picking = self.copy(cr, uid, pick.id,
				            {
				                'name': name,
				                'move_lines': [],
				                'state' : 'draft',
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




