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
		
	

	_columns =	{
							'name' : fields.char(string='# Expedition', size=30, required=True, readonly=True),
							'ref' : fields.char(string='Reference', size=30),
							'vehicle_number' : fields.char(string='Vehicle Number', size=50, required=True),
							'expedition_type' : fields.selection(selection=[('in','Incoming'),('out','Outgoing')], string='Type', required=True),
							'expedition_mode' : fields.selection(selection=[('air','Air'),('land','Land'),('water','Water')], string='Expedition Mode', required=True),
							'partner_id' : fields.many2one(string='Partner', obj='res.partner'),
							'start_location_id' : fields.many2one(obj='stock.location', string='Start Location', required=True, domain=[('type','!=','view')]),
							'expedition_crew_ids' : fields.one2many(string='Expedition Crew', obj='stock.expedition_crew', fields_id='expedition_id'),
							'picking_ids' : fields.one2many(string='Movement', obj='stock.picking', fields_id='expedition_id'),
							'state' : fields.selection(selection=[('draft','Draft'),('confirm','Confirm'),('loading','Loading'),('finished_loading','Finished Loading'),('departed','Departed'),('arrived','Arrived'),('cancel','Cancel')], string='State', required=True, readonly=True),
							'create_id' : fields.many2one(string='Created By', obj='res.users', readonly=True),
							'create_time' : fields.datetime(string='Creation Time', readonly=True),
							'confirm_id' : fields.many2one(string='Confirmed By', obj='res.users', readonly=True),
							'confirm_time' : fields.datetime(string='Confirmation Time', readonly=True),
							'loading_id' : fields.many2one(string='Start Loaded By', obj='res.users', readonly=True),
							'loading_time' : fields.datetime(string='Start Loading Time', readonly=True),
							'finished_loading_id' : fields.many2one(string='Finished Loaded By', obj='res.users', readonly=True),
							'finished_loading_time' : fields.datetime(string='Finish Loading Time', readonly=True),
							'departed_id' : fields.many2one(string='Departed By', obj='res.users', readonly=True),
							'departed_time' : fields.datetime(string='Departed Time', readonly=True),	
							'arrived_id' : fields.many2one(string='Arrived By', obj='res.users', readonly=True),
							'arrived_time' : fields.datetime(string='Arrived Time', readonly=True),				
							'cancel_id' : fields.many2one(string='Cancelled By', obj='res.users', readonly=True),
							'cancel_time' : fields.datetime(string='Cancelled Time', readonly=True),	
							'cancel_description' : fields.text(string='Cancel Description', readonly=True),											
		        			 }	
		        			 
	_defaults =	{
	 						'name' : default_name,
	 						'expedition_type' : default_expedition_type,
	 						'expedition_mode' : default_expedition_mode,
	 						'state' : default_state,
	 						}
	 						
	def workflow_action_confirm(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'confirm'})
			
	def workflow_action_loading(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'loading'})			
			
	def workflow_action_finished_loading(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'finished_loading'})	
			
	def workflow_action_departed(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'departed'})												
			
	def workflow_action_arrived(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'arrived'})					
			
	def workflow_action_cancel(self, cr, uid, ids, context={}):
		for id in ids:
			self.write(cr, uid, [id], {'state' : 'cancel'})							




expedition()




