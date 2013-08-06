# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree

import netsvc
import time

from osv import osv,fields
from tools.translate import _
import decimal_precision as dp
from datetime import datetime

class wizard_split_picking(osv.osv_memory):
    _name = 'stock.wizard_split_picking'
    _description = 'Wizard Split Picking'
    
    def default_line_ids(self, cr, uid, context={}):
        obj_picking = self.pool.get('stock.picking')
        
        picking = obj_picking.browse(cr, uid, context['active_ids'])[0]
        res = []
        
        if picking.move_lines:
            for move in picking.move_lines:
                val =   {
                            'name' : move.name,
                            'product_id' : move.product_id.id,
                            'quantity' : move.product_qty,
                            'product_uom' : move.product_uom.id,
                            'location_id' : move.location_id.id,
                            'location_dest_id' : move.location_dest_id.id,
                            'move_id' : move.id
                            }
                            
                res.append(val)
        return res
    
    _columns =     {
                                'line_ids' : fields.one2many(string='Wizard Line', obj='stock.wizard_split_picking_line', fields_id='wizard_id'),
                                }
                                
    _defaults = {
                            'line_ids' : default_line_ids,
                            }
                            
    def button_split_picking(self, cr, uid, ids, context={}):
        for id in ids:
            if not self.split_picking(cr, uid, id, context):
                return False
                
        return {}
        
    def split_picking(self, cr, uid, id, context):
        obj_picking = self.pool.get('stock.picking')
        obj_wizard_line = self.pool.get('stock.wizard_split_picking_line')
        
        picking = obj_picking.browse(cr, uid, context['active_ids'])[0]
        wizard = self.browse(cr, uid, [id])[0]
        
        #raise osv.except_osv('a', picking.picking_reference_id._name)
        
        
        
        val =   {
                    'origin' : picking.origin,
                    'backorder_id' : picking.id,
                    'location_id' : picking.location_id.id,
                    'location_dest_id' : picking.location_dest_id.id,
                    'date' : picking.date,
                    'picking_reference_id' : '%s, %s' % (picking.picking_reference_id._name,picking.picking_reference_id.id),
                    'company_id' : picking.company_id.id,
                    'address_id' : picking.address_id.id,
                    }
                    
        picking_id = obj_picking.create(cr, uid, val, context={'stock_journal' : picking.stock_journal_id.name})
        
        if wizard.line_ids:
            for wizard_line in wizard.line_ids:
                if not obj_wizard_line.create_picking_move(cr, uid, wizard_line.id, picking_id, context):
                    raise False
                    
                if not obj_wizard_line.update_previous_move(cr, uid, wizard_line.id):
                    raise False
                 
        
        return picking_id
                    

wizard_split_picking()

class wizard_split_picking_line(osv.osv_memory):
    _name = 'stock.wizard_split_picking_line'
    _description = 'Wizard Split Picking Line'
    
    
    _columns =     {
                                'product_id' : fields.many2one(obj='product.product', string='Product', required=True, ondelete='CASCADE'),
                                'quantity' : fields.float(string='Quantity', digits_compute=dp.get_precision('Product UoM'), required=True),
                                'product_uom': fields.many2one(obj='product.uom', string='Unit of Measure', required=True, ondelete='CASCADE'),
                                'location_id': fields.many2one(obj='stock.location', string='Location', required=True, ondelete='CASCADE', domain = [('usage','<>','view')]),
                                'location_dest_id': fields.many2one(obj='stock.location', string='Dest. Location', required=True, ondelete='CASCADE', domain = [('usage','<>','view')]),
                                'move_id' : fields.many2one(obj='stock.move', string='Move', ondelete='CASCADE'),
                                'wizard_id' : fields.many2one(obj='stock.wizard_split_picking', string="Wizard", ondelete='CASCADE'),
                                }
                                
    def create_picking_move(self, cr, uid, id, picking_id, context):
        obj_move = self.pool.get('stock.move')
        
        wizard_line = self.browse(cr, uid, [id])[0]
        move = obj_move.browse(cr, uid, [wizard_line.move_id.id])[0]
        
        val =   {
                    'name' : move.name,
                    'priority' : move.priority,
                    #'create_date' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'date_expected' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'product_id' : move.product_id.id,
                    'product_qty' : wizard_line.quantity,
                    'product_uom' : wizard_line.product_uom.id,
                    #'product_uos_qty' : 0, #TODO,
                    #'product_uos' : 0,
                    'product_packaging' : move.product_packaging.id,
                    'location_id' : wizard_line.location_id.id,
                    'location_dest_id' : wizard_line.location_dest_id.id,
                    'address_id' : move.address_id.id,
                    'prodlot_id' : move.prodlot_id.id,
                    'tracking_id' : move.tracking_id.id,
                    'auto_validate' : move.auto_validate,
                    'note' : move.note,
                    'price_unit' : move.price_unit,
                    'price_currency_id' : move.price_currency_id.id,
                    'company_id' : move.company_id.id,
                    'picking_id' : picking_id,
                    }
                    
        move_id = obj_move.create(cr, uid, val)
        
        return move_id
        
    def update_previous_move(self, cr, uid, id):
        obj_move = self.pool.get('stock.move')
        obj_uom = self.pool.get('product.uom')
        
        wizard_line = self.browse(cr, uid, [id])[0]
        qty_substract = obj_uom._compute_qty(cr, uid, wizard_line.product_uom.id, wizard_line.quantity, wizard_line.move_id.product_uom.id)
        qty_final = wizard_line.move_id.product_qty - qty_substract
        
        if qty_final<=0.0:
            obj_move.unlink(cr, uid, [wizard_line.move_id.id])
            #raise osv.except_osv('Warning!', 'You can not split move to zero or less-then zero')
            return True
        
        val =   {
                    'product_qty' : qty_final,
                    }
                    
        obj_move.write(cr, uid, [wizard_line.move_id.id], val)
        
        return True
                    
        
wizard_split_picking_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

