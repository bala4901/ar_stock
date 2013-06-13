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

class wizard_return_picking(osv.osv_memory):
	_name = 'stock.wizard_return_picking'
	_description = 'Wizard Return Picking'
	
	def default_detail_ids(self, cr, uid, context={}):
		obj_expedition = self.pool.get(context['active_model'])
		
		expedition = obj_expedition.browse(cr, uid, context['active_ids'])[0]
		res = []
		
		for detail in expedition.picking_ids:
			if detail.state != 'done':
				val =	{
							'picking_id' : detail.id,
							'note' : '-',
							}
				res.append(val)
		return res
		
		

	_columns =	{
							'detail_ids' : fields.one2many(string='Detail', obj='stock.wizard_return_picking_detail', fields_id='wizard_id'),
							}
							
	def return_picking(self, cr, uid, ids, context={}):
		for id in ids:
			if not self.picking_return(cr, uid, id, context['active_id']):
				return False
				
		return {}
		
	def picking_return(self, cr, uid, id, expedition_id):
		wizard = self.browse(cr, uid, [id])[0]
		obj_picking = self.pool.get('stock.picking')
		wkf_service = netsvc.LocalService('workflow')
		obj_return = self.pool.get('stock.returned_expedition_package')
		
		for detail in wizard.detail_ids:
			val =	{
						'expedition_id' : expedition_id,
						'picking_id' : detail.picking_id.id,
						'reason' : detail.note
						}
						
			obj_return.create(cr, uid, val)
			
			obj_picking.write(cr, uid, [detail.picking_id.id], {'expedition_id' : False})
			
		return True
						
	_defaults =	{
							'detail_ids' : default_detail_ids,
							}
wizard_return_picking()

class wizard_return_picking_detail(osv.osv_memory):
	_name = 'stock.wizard_return_picking_detail'
	_description = 'Wizard Detail Deliver Picking'
	
	_columns =	{
							'wizard_id' : fields.many2one(string='Wizard', obj='stock.wizard_return_picking'),
							'picking_id' : fields.many2one(string='Picking', obj='stock.picking', required=True),
							'note' : fields.char(string='Date Done', required=True, size=100),
							}
	

wizard_return_picking_detail()




