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

class incoming_shipment(osv.osv):
	_name = 'stock.incoming_shipment'
	_inherit = 'stock.picking'
	_table = 'stock_picking'
	_description = 'Incoming Shipment'
	
	_columns =	{
        'state': fields.selection([
            ('draft', 'New'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Process'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ], 'State', readonly=True, select=True,
            help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                 "* Confirmed: still waiting for the availability of products\n"\
                 "* Available: products reserved, simply waiting for confirmation.\n"\
                 "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                 "* Done: has been processed, can't be modified or cancelled anymore\n"\
                 "* Cancelled: has been cancelled, can't be confirmed anymore"),
                 }	
			
	
	
	def check_access_rights(self, cr, uid, operation, raise_exception=True):
		#override in order to redirect the check of acces rights on the stock.picking object
		return self.pool.get('stock.picking').check_access_rights(cr, uid, operation, raise_exception=raise_exception)
		
	def check_access_rule(self, cr, uid, ids, operation, context=None):
		#override in order to redirect the check of acces rules on the stock.picking object
		return self.pool.get('stock.picking').check_access_rule(cr, uid, ids, operation, context=context)
		
	def create(self, cr, uid, value, context=None):
		new_id = super(incoming_shipment, self).create(cr, uid, value, context)
		
		wkf_service = netsvc.LocalService('workflow')
		wkf_service.trg_create(uid, 'stock.picking', new_id, cr)
		
		return new_id
		
	def unlink(self, cr, uid, ids, context=None):
		wkf_service = netsvc.LocalService('workflow')
		for id in ids:
			wkf_service.trg_delete(uid, 'stock.picking', id, cr)
			
		return super(incoming_shipment, self).unlink(cr, uid, ids, context)



incoming_shipment()




