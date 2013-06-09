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
import netsvc

class wizard_deliver_picking(osv.osv_memory):
	_name = 'stock.wizard_deliver_picking'
	_description = 'Wizard Deliver Picking'
	
	def default_detail_ids(self, cr, uid, context={}):
		obj_expedition = self.pool.get(context['active_model'])
		
		expedition = obj_expedition.browse(cr, uid, context['active_ids'])[0]
		res = []
		
		for detail in expedition.picking_ids:
			val =	{
						'picking_id' : detail.id,
						'date_done' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
						}
			res.append(val)
		return res
		
		

	_columns =	{
							'detail_ids' : fields.one2many(string='Detail', obj='stock.wizard_deliver_picking_detail', fields_id='wizard_id'),
							}
							
	def deliver_picking(self, cr, uid, ids, context={}):
		for id in ids:
			if not self.picking_done(cr, uid, id):
				return False
				
		return {}
		
	def picking_done(self, cr, uid, id):
		wizard = self.browse(cr, uid, [id])[0]
		obj_picking = self.pool.get('stock.picking')
		wkf_service = netsvc.LocalService('workflow')
		
		for detail in wizard.detail_ids:
			obj_picking.action_move(cr, uid, [detail.picking_id.id])
			wkf_service.trg_validate(uid, 'stock.picking', detail.picking_id.id, 'button_done', cr)
			obj_picking.change_date_done(cr, uid, detail.picking_id.id, detail.date_done) 
			
		return True
						
	_defaults =	{
							'detail_ids' : default_detail_ids,
							}
wizard_deliver_picking()

class wizard_deliver_picking_detail(osv.osv_memory):
	_name = 'stock.wizard_deliver_picking_detail'
	_description = 'Wizard Detail Deliver Picking'
	
	_columns =	{
							'wizard_id' : fields.many2one(string='Wizard', obj='stock.wizard_deliver_picking'),
							'picking_id' : fields.many2one(string='Picking', obj='stock.picking', required=True),
							'date_done' : fields.datetime(string='Date Done', required=True),
							}
	

wizard_deliver_picking_detail()




