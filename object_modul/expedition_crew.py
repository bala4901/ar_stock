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

class expedition_crew(osv.osv):
	_name = 'stock.expedition_crew'
	_description = 'Expedition Crew'

			
		
	
	_columns =	{
							'expedition_id' : fields.many2one(string='# Expedition', obj='stock.expedition'),
							'expedition_crew_position_id' : fields.many2one(string='Crew Position', obj='stock.expedition_crew_position', required=True),
							'name' : fields.char(string='Crew Name', size=100, required=True),
                			 }	





expedition_crew()




