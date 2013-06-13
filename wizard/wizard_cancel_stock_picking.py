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

class wizard_cancel_stock_picking(osv.osv_memory):
	_name = 'stock.wizard_cancel_stock_picking'
	_description = 'Wizard Cancel Stock Picking'

	def default_cancel_user_id(self, cr, uid, context={}):
		return uid
	
	def default_cancel_time(self, cr, uid, context={}):
		return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

	_columns =	{
							'cancel_user_id' : fields.many2one(obj='res.users', string='Cancelled By', readonly=True),
							'cancel_time' : fields.datetime(string='Cancel Time', readonly=True),
							'cancel_description' : fields.text(string='Cancel Description'),
							}
						
	_defaults =	{
							'cancel_user_id' : default_cancel_user_id,
							'cancel_time' : default_cancel_time,
							}
						
	def cancel_picking(self, cr, uid, ids, context={}):
		obj_wizard = self.pool.get('stock.wizard_cancel_stock_picking')
		obj_picking = self.pool.get('stock.picking')
		
		wizard = obj_wizard.browse(cr, uid, ids, context)[0]		
		wkf_service = netsvc.LocalService('workflow')
		
		res =	{
					'cancel_user_id' : wizard.cancel_user_id.id,
					'cancel_time' : wizard.cancel_time,
					'cancel_description' : wizard.cancel_description,
					}
					
		obj_picking.write(cr, uid, context['active_ids'], res)
	
		for id in context['active_ids']:
			picking = obj_picking.browse(cr, uid, id)[0]
			if picking.state != 'done'
				wkf_service.trg_validate(uid, 'stock.picking', id, 'button_cancel', cr)
			elif picking.state == 'done':
		        wkf_service.trg_delete(uid, 'stock.picking', id, cr)
		        wkf_service.trg_create(uid, 'stock.picking', id, cr)			
		        wkf_service.trg_validate(uid, 'stock.picking', id, 'button_cancel', cr)	
		
		return {}
							



wizard_cancel_stock_picking()




