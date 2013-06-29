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
import netsvc

class expedition(osv.osv):
	_name = 'stock.expedition'
	_description = 'Expedition'

	def default_name(self, cr, uid, context={}):
		return '/'
	
	def default_expedition_type(self, cr, uid, context={}):
		if context is None:
			context = {}
		
		return context.get('expedition_type', 'out')
	
	def default_expedition_mode(self, cr, uid, context={}):
		if context is None:
			context = {}
		
		return context.get('expedition_mode', 'land')
	
	def default_state(self, cr, uid, context={}):
		return 'draft'
		
	def default_company_id(self, cr, uid, context={}):
		obj_user = self.pool.get('res.users')
		
		user = obj_user.browse(cr, uid, [uid])[0]
		
		return user.company_id.id
		
	

	_columns =	{
							'name' : fields.char(string='# Expedition', size=30, required=True, readonly=True),
							'company_id' : fields.many2one(string='Company', obj='res.company', required=True, readonly=True, states={'draft' : [('readonly',False)]}),
							'ref' : fields.char(string='Reference', size=30, readonly=True, states={'draft' : [('readonly',False)]}),
							'vehicle_number' : fields.char(string='Vehicle Number', size=50, required=True, readonly=True, states={'draft' : [('readonly',False)]}),
							'expedition_type' : fields.selection(selection=[('in','Incoming'),('out','Outgoing'),('in_direct','Incoming Direct Picking'),('out_direct','Outgoing Direct Picking')], string='Type', required=True, readonly=True, states={'draft' : [('readonly',False)]}),
							'expedition_mode' : fields.selection(selection=[('air','Air'),('land','Land'),('water','Water')], string='Expedition Mode', required=True, readonly=True, states={'draft' : [('readonly',False)]}),
							'partner_id' : fields.many2one(string='Partner', obj='res.partner', readonly=True, states={'draft' : [('readonly',False)]}),
							'start_location_id' : fields.many2one(obj='stock.location', string='Start Location', required=False, domain=[('type','!=','view')]),
							'expedition_crew_ids' : fields.one2many(string='Expedition Crew', obj='stock.expedition_crew', fields_id='expedition_id', readonly=True, states={'draft' : [('readonly',False)]}),
							'delivered_picking_ids' : fields.one2many(string='Delivered Picking', obj='stock.delivered_expedition_package', fields_id='expedition_id', readonly=True),
							'returned_picking_ids' : fields.one2many(string='Returned Picking', obj='stock.returned_expedition_package', fields_id='expedition_id', readonly=True),
							'picking_ids' : fields.one2many(string='Movement', obj='stock.picking', fields_id='expedition_id', domain=[('state','=','assigned')], readonly=True, states={'draft' : [('readonly',False)]}),
							'state' : fields.selection(selection=[('draft','Draft'),('confirm','Confirm'),('ready','Ready'),('done','Done'),('cancel','Cancel')], string='State', required=True, readonly=True),
							'create_id' : fields.many2one(string='Created By', obj='res.users', readonly=True),
							'create_time' : fields.datetime(string='Creation Time'),
							'confirm_id' : fields.many2one(string='Confirmed By', obj='res.users', readonly=True),
							'confirm_time' : fields.datetime(string='Confirmation Time'),
							'loading_id' : fields.many2one(string='Start Loaded By', obj='res.users', readonly=True),
							'loading_time' : fields.datetime(string='Start Loading Time'),
							'finished_loading_id' : fields.many2one(string='Finished Loaded By', obj='res.users', readonly=True),
							'finished_loading_time' : fields.datetime(string='Finish Loading Time'),
							'departed_id' : fields.many2one(string='Departed By', obj='res.users', readonly=True),
							'departed_time' : fields.datetime(string='Departed Time'),	
							'arrived_id' : fields.many2one(string='Arrived By', obj='res.users', readonly=True),
							'arrived_time' : fields.datetime(string='Arrived Time'),				
							'cancel_id' : fields.many2one(string='Cancelled By', obj='res.users', readonly=True),
							'cancel_time' : fields.datetime(string='Cancelled Time', readonly=True),	
							'cancel_description' : fields.text(string='Cancel Description', readonly=True),											
		        			 }	
		        			 
	_defaults =	{
	 						'name' : default_name,
	 						'expedition_type' : default_expedition_type,
	 						'expedition_mode' : default_expedition_mode,
	 						'state' : default_state,
	 						'company_id' : default_company_id,
	 						}
	 						
	def workflow_action_confirm(self, cr, uid, ids, context={}):
		for id in ids:
			if not self.buat_sequence(cr, uid, id, context):
				return False
		
			self.write(cr, uid, [id], {'state' : 'confirm'})
			
		return True
															
	def workflow_action_ready(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'ready'})			
			
		return True
		
	def check_picking(self, cr, uid, id):
		expedition = self.browse(cr, uid, [id])[0]
		
		for picking in expedition.picking_ids:
			if picking.state != 'done':
				return False
				
		return True
						
	def workflow_action_done(self, cr, uid, ids, context={}):
		for id in ids:
			if not self.check_picking(cr, uid, id):
				raise osv.except_osv('Warning!', 'Please process all picking first')
				return True
				
			self.write(cr, uid, [id], {'state' : 'done'})			
			
		return True		
			
	def workflow_action_cancel(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'cancel'})			
			
		return True
		
	def button_workflow_action_confirm(self, cr, uid, ids, context):
		wkf_service = netsvc.LocalService('workflow')
		
		for id in ids:
			wkf_service.trg_validate(uid, 'stock.expedition', id, 'button_confirm', cr)
			
		return True
		
	def button_workflow_action_ready(self, cr, uid, ids, context):
		wkf_service = netsvc.LocalService('workflow')
		
		for id in ids:
			wkf_service.trg_validate(uid, 'stock.expedition', id, 'button_ready', cr)
			
		return True		
		
	def button_workflow_action_done(self, cr, uid, ids, context):
		wkf_service = netsvc.LocalService('workflow')
		
		for id in ids:
			wkf_service.trg_validate(uid, 'stock.expedition', id, 'button_done', cr)
			
		return True		
		
	def button_workflow_action_cancel(self, cr, uid, ids, context):
		wkf_service = netsvc.LocalService('workflow')
		
		for id in ids:
			wkf_service.trg_validate(uid, 'stock.expedition', id, 'button_cancel', cr)
			
		return True		
		
			
	def buat_sequence(self, cr, uid, id, context={}):
		obj_user = self.pool.get('res.users')
		obj_sequence = self.pool.get('ir.sequence')
		
		
		user = obj_user.browse(cr, uid, [uid])[0]
		expedition = self.browse(cr, uid, [id])[0]
		
		if expedition.expedition_type == 'out':
			sequence_id = user.company_id.sequence_outgoing_expedition_id.id
		elif expedition.expedition_type == 'in':
			sequence_id = user.company_id.sequence_incoming_expedition_id.id			
		elif expedition.expedition_type == 'out_picking':
			sequence_id = user.company_id.sequence_outgoing_picking_id.id	
		elif expedition.expedition_type == 'in_picking':
			sequence_id = user.company_id.sequence_incoming_picking_id.id						
			
		sequence = obj_sequence.next_by_id(cr, uid, sequence_id, context={'tanggal' : expedition.create_time})
		
		self.write(cr, uid, [id], {'name' : sequence})
		
		return True
		
					

expedition()

class delivered_expedition_package(osv.osv):
	_name = 'stock.delivered_expedition_package'
	_description = 'Delivered Expedition Package'
	
	_columns =	{
							'expedition_id' : fields.many2one(string='Expedition', obj='stock.expedition'),
							'picking_id' : fields.many2one(string='Picking', obj='stock.picking'),
							'date_done' : fields.related('picking_id','date_done',type='datetime',relation='stock.picking', string='Date Done'),
							}

delivered_expedition_package()
	
class returned_expedition_package(osv.osv):
	_name = 'stock.returned_expedition_package'
	_description = 'Returned Expedition Package'
	
	_columns =	{
							'expedition_id' : fields.many2one(string='Expedition', obj='stock.expedition'),
							'picking_id' : fields.many2one(string='Picking', obj='stock.picking'),
							'reason' : fields.char(string='Reason', required=True, size=100),
							}

returned_expedition_package()



