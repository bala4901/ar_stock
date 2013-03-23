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

class stock_move(osv.osv):
	_name = 'stock.move'
	_inherit = 'stock.move'
	
	def _default_location_destination(self, cr, uid, context=None):
		if context is None:
			context = {}
			
		location_dest_id = context.get('location_dest_id', False)
		
		if not location_dest_id:
			return super(stock_move, self)._default_location_destination(cr, uid, context)
		else:
			return location_dest_id
			
	def _default_location_source(self, cr, uid, context=None):
		if context is None:
			context = {}
			
		location_id = context.get('location_id', False)
		
		if not location_id:
			return super(stock_move, self)._default_location_source(cr, uid, context)
		else:
			return location_id			
			
	_defaults =	{
							'location_id' : _default_location_source,
							'location_dest_id' : _default_location_destination,
							}
							



stock_move()




