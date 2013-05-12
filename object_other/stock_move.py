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


from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
from tools import float_compare
import decimal_precision as dp
import logging

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
							
        def _prepare_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
                """Prepare the definition (values) to create a new chained picking.

                   :param str picking_name: desired new picking name
                   :param browse_record picking: source picking (being chained to)
                   :param str picking_type: desired new picking type
                   :param list moves_todo: specification of the stock moves to be later included in this
                       picking, in the form::

                           [[move, (dest_location, auto_packing, chained_delay, chained_journal,
                                          chained_company_id, chained_picking_type)],
                            ...
                           ]

                       See also :meth:`stock_location.chained_location_get`.
                """
                res_company = self.pool.get('res.company')
                #raise osv.except_osv(_('Error !'), _('%s')%moves_todo[0][1][0].id)
                return {
                            'name': picking_name,
                            'origin': tools.ustr(picking.origin or ''),
                            'type': picking_type,
                            'note': picking.note,
                            'move_type': picking.move_type,
                            'auto_picking': moves_todo[0][1][1] == 'auto',
                            'stock_journal_id': moves_todo[0][1][3],
                            'company_id': moves_todo[0][1][4] or res_company._company_default_get(cr, uid, 'stock.company', context=context),
                            'address_id': picking.address_id.id,
                            'invoice_state': 'none',
                            'date': picking.date,
                            'location_dest_id' : moves_todo[0][1][0].id, #<-- Additional Code
                            'location_id' : picking.location_dest_id.id, #<-- Additional Code
                        }
		
        def create_chained_picking(self, cr, uid, moves, context=None):
                res_obj = self.pool.get('res.company')
                location_obj = self.pool.get('stock.location')
                move_obj = self.pool.get('stock.move')
                wf_service = netsvc.LocalService("workflow")
                new_moves = []
                
                if context is None:
                    context = {}
                seq_obj = self.pool.get('ir.sequence')
                for picking, todo in self._chain_compute(cr, uid, moves, context=context).items():
                    ptype = todo[0][1][5] and todo[0][1][5] or location_obj.picking_type_get(cr, uid, todo[0][0].location_dest_id, todo[0][1][0])
                    #raise osv.except_osv(_('Error !'), _('%s')%type(str(picking.location_dest_id.chained_journal_id.name)))
                    if picking:
                        # name of new picking according to its type
                        new_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + ptype)
                        pickid = self._create_chained_picking(cr, uid, new_pick_name, picking, ptype, todo, context={'stock_journal': picking.location_dest_id.chained_journal_id.name}) #<----- Modification Pada Context
                        # Need to check name of old picking because it always considers picking as "OUT" when created from Sale Order
                        old_ptype = location_obj.picking_type_get(cr, uid, picking.move_lines[0].location_id, picking.move_lines[0].location_dest_id)
                        if old_ptype != picking.type:
                            old_pick_name = seq_obj.get(cr, uid, 'stock.picking.' + old_ptype)
                            self.pool.get('stock.picking').write(cr, uid, [picking.id], {'name': old_pick_name}, context=context)
                    else:
                        pickid = False
                    for move, (loc, dummy, delay, dummy, company_id, ptype) in todo:
                        new_id = move_obj.copy(cr, uid, move.id, {
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': loc.id,
                            'date_moved': time.strftime('%Y-%m-%d'),
                            'picking_id': pickid,
                            'state': 'waiting',
                            'company_id': company_id or res_obj._company_default_get(cr, uid, 'stock.company', context=context)  ,
                            'move_history_ids': [],
                            'date': (datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') + relativedelta(days=delay or 0)).strftime('%Y-%m-%d'),
                            'move_history_ids2': []}
                        )
                        move_obj.write(cr, uid, [move.id], {
                            'move_dest_id': new_id,
                            'move_history_ids': [(4, new_id)]
                        })
                        new_moves.append(self.browse(cr, uid, [new_id])[0])
                    if pickid:
                        wf_service.trg_validate(uid, 'stock.picking', pickid, 'button_confirm', cr)
                if new_moves:
                    new_moves += self.create_chained_picking(cr, uid, new_moves, context)
                return new_moves
							



stock_move()




