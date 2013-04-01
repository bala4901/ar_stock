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

import netsvc
import time

from osv import osv,fields
from tools.translate import _
import decimal_precision as dp

class wizard_forward_picking_detail(osv.osv_memory):
    _name = 'stock.wizard_forward_picking_detail'
    _description = 'Wizard Forward Picking Detail'
    _rec_name = 'product_id'
    _columns =  {
                            'product_id' : fields.many2one(obj='product.product', string='Product', required=True),
                            'quantity' : fields.float(string='Quantity', digits_compute=dp.get_precision('Product UoM'), required=True),
                            'wizard_id' : fields.many2one(obj='stock.wizard_forward_picking', string='Wizard'),
                            'move_id' : fields.many2one(obj='stock.move', string='Move'),
                            }

wizard_forward_picking_detail()


class wizard_forward_picking(osv.osv_memory):
    _name = 'stock.wizard_forward_picking'
    _description = 'Wizard Forward Picking'
    _columns = {
                            'forward_stock_journal_id' : fields.many2one(string='Forward Stock Journal', obj='stock.journal', required=True),
                            'allow_location_selection' : fields.boolean(string='Allow Location Selection'),
                            'location_id' : fields.many2one(string='Location', obj='stock.location', required=True),
                            'allow_dest_location_selection' : fields.boolean(string='Allow Destination Location Selection'),
                            'location_dest_id' : fields.many2one(string='Dest. Location', obj='stock.location', required=True),
                            'detail_ids' : fields.one2many(obj='stock.wizard_forward_picking_detail', fields_id='wizard_id', string='Moves'),
                            }

    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        
        if context is None:
            context = {}
            
        wizard = super(wizard_forward_picking, self).default_get(cr, uid, fields, context=context)
        
        record_id = context and context.get('active_id', False) or False
        obj_picking = self.pool.get('stock.picking')
        picking = obj_picking.browse(cr, uid, record_id, context=context)
        
        if picking:
            dict_header =   {
                                            'forward_stock_journal_id' : picking.stock_journal_id.stock_journal_return_id.id,
                                            'allow_location_selection' : picking.stock_journal_id.stock_journal_return_id.allow_location_selection,
                                            'allow_dest_location_selection' : picking.stock_journal_id.stock_journal_return_id.allow_dest_location_selection,
                                            'location_id' : picking.stock_journal_id.stock_journal_return_id.default_location_id and picking.stock_journal_id.stock_journal_return_id.default_location_id.id or False,
                                            'location_dest_id' : picking.stock_journal_id.stock_journal_return_id.default_location_dest_id and picking.stock_journal_id.stock_journal_return_id.default_location_dest_id.id or False,
                                            }
                                            
            wizard.update(dict_header)
                                            
            return_history = self.get_return_history(cr, uid, record_id, context)       
            for line in picking.move_lines:
                qty = line.product_qty - return_history[line.id]
                if qty > 0:
                    dict_detail =   {
                                                'product_id' : line.product_id.id, 
                                                'quantity' : qty,
                                                'move_id' : line.id
                                                }
                    result1.append(dict_detail)
            if 'detail_ids' in fields:
                wizard.update({'detail_ids' : result1})
        return wizard

    def view_init(self, cr, uid, fields_list, context=None):
        """
         Creates view dynamically and adding fields at runtime.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view with new columns.
        """
        if context is None:
            context = {}
            
        res = super(wizard_forward_picking, self).view_init(cr, uid, fields_list, context=context)
        
        record_id = context and context.get('active_id', False)
        
        if record_id:
            obj_picking = self.pool.get('stock.picking')
            picking = obj_picking.browse(cr, uid, record_id, context=context)

            if picking.state not in ['done','confirmed','assigned']:
                raise osv.except_osv(_('Warning !'), _("You may only return pickings that are Confirmed, Available or Done!"))
                
            valid_lines = 0
            return_history = self.get_return_history(cr, uid, record_id, context)
            
            for m  in picking.move_lines:
                if (return_history.get(m.id) is not None) and (m.product_qty * m.product_uom.factor > return_history[m.id]):
                        valid_lines += 1
                        
            if not valid_lines:
                raise osv.except_osv(_('Warning !'), _("There are no products to return (only lines in Done state and not fully returned yet can be returned)!"))
        return res
    
    def get_return_history(self, cr, uid, pick_id, context=None):
        """ 
         Get  return_history.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param pick_id: Picking id
         @param context: A standard dictionary
         @return: A dictionary which of values.
        """
        obj_picking = self.pool.get('stock.picking')
        picking = obj_picking.browse(cr, uid, pick_id, context=context)
        return_history = {}
        
        for m  in picking.move_lines:
            if m.state == 'done':
                return_history[m.id] = 0
                for rec in m.move_history_ids2:
                    # only take into account 'product return' moves, ignoring any other
                    # kind of upstream moves, such as internal procurements, etc.
                    # a valid return move will be the exact opposite of ours:
                    #     (src location, dest location) <=> (dest location, src location))
                    if rec.location_dest_id.id == m.location_id.id \
                        and rec.location_id.id == m.location_dest_id.id:
                        return_history[m.id] += (rec.product_qty * rec.product_uom.factor)
        return return_history
        
    def onchange_stock_journal_id(self, cr, uid, ids, stock_journal_id):
        value = {}
        domain = {}
        warning = {}
        
        list_location_id = []
        list_location_dest_id = []
        
        obj_stock_journal = self.pool.get('stock.journal')
        
        if stock_journal_id:
            stock_journal = obj_stock_journal.browse(cr, uid, [stock_journal_id])[0]
            
            if stock_journal.allowed_location_ids:
                for location in stock_journal.allowed_location_ids:
                    list_location_id.append(location.id)

            if stock_journal.allowed_location_dest_ids:
                for location in stock_journal.allowed_location_dest_ids:
                    list_location_dest_id.append(location.id)                    
                    
            if list_location_id:
                domain.update({'location_id' : [('id','in',list_location_id)]})
                
            if not list_location_id:
                domain.update({'location_id' : [('id','=',0)]})                                
                
            if list_location_dest_id:
                domain.update({'location_dest_id' : [('id','in',list_location_dest_id)]})               
                
            if not list_location_dest_id:
                domain.update({'location_dest_id' : [('id','=',0)]})                      
                
        return {'value' : value, 'domain' : domain, 'warning' : warning} 
            
        

    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
            
        record_id = context and context.get('active_id', False) or False
        
        obj_move = self.pool.get('stock.move')
        obj_picking = self.pool.get('stock.picking')
        obj_uom = self.pool.get('product.uom')
        obj_detail = self.pool.get('stock.wizard_forward_picking_detail')
        wkf_service = netsvc.LocalService('workflow')
        
        picking = obj_picking.browse(cr, uid, record_id, context=context)
        wizard = self.read(cr, uid, ids[0], context=context)
        new_picking = None
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0
        
        # Get info from stock.journal
 
        context.update({'stock_journal' : picking.stock_journal_id.stock_journal_return_id.name})
        dict_defaults = {
                                        'date' : date_cur,
                                        'move_lines' : [],
                                        'picking_reference_id' : '%s, %s' % (picking.stock_journal_id.stock_journal_return_id.model_name, str(picking.id)),
                                        }
        
        new_picking_id = obj_picking.create(cr, uid, dict_defaults, context)
        new_picking = obj_picking.browse(cr, uid, [new_picking_id])[0]
        
        val_id = wizard['detail_ids']
        
        for v in val_id:
            detail = obj_detail.browse(cr, uid, v, context=context)
            mov_id = detail.move_id.id
            new_qty = detail.quantity
            move = obj_move.browse(cr, uid, mov_id, context=context)
            returned_qty = move.product_qty
            
            # ini penting buat dimengerti nih
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            # ini juga
            if returned_qty != new_qty:
                set_invoice_state_to_none = False
                
            if new_qty:
                returned_lines += 1
                dict_defaults = {
                                                'product_qty' : new_qty,
                                                'product_uos_qty' : obj_uom._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                                'state' : 'draft',
                                                'location_id' : new_picking.location_id.id,
                                                'location_dest_id' : new_picking.location_dest_id.id,
                                                'date' : date_cur
                                                }
                
                new_move_id = obj_move.copy(cr, uid, move.id, dict_defaults)
                obj_move.write(cr, uid, [new_move_id], {'picking_id' : new_picking_id})
                obj_move.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move_id)]})
                
        if not returned_lines:
            raise osv.except_osv(_('Warning !'), _("Please specify at least one non-zero quantity!"))

        if set_invoice_state_to_none:
            obj_picking.write(cr, uid, [picking.id], {'invoice_state':'none'})
            
        wkf_service.trg_validate(uid, 'stock.picking', new_picking_id, 'button_confirm', cr)
        obj_picking.force_assign(cr, uid, [new_picking_id], context)
        
        # Menyesuaikan view yang dibuka dengan stock_journal picking yang baru
            
        obj_data = self.pool.get('ir.model.data')
        res = obj_data.get_object_reference(cr, uid, picking.stock_journal_id.stock_journal_return_id.modul_origin, picking.stock_journal_id.stock_journal_return_id.model_view_form)
        context.update({'view_id': res and res[1] or False})
        
        # membuka form dengan picking yang baru
        return  {
                        'res_id' : new_picking_id,
                        'name' : picking.stock_journal_id.stock_journal_return_id.name,
                        'view_type' : 'form',
                        'view_mode' : 'form',
                        'res_model' : picking.stock_journal_id.stock_journal_return_id.model_name, #TODO
                        'type' : 'ir.actions.act_window',
                        'context' : context,
                        }

wizard_forward_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

