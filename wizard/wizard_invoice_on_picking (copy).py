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

class wizard_invoice_on_picking(osv.osv_memory):
    _name = "stock.wizard_invoice_on_picking"
    _description = "Wizard Invoice On Picking"

    _columns = {
        'account_journal_id' : fields.many2one(string='Account Journal', obj='account.journal', required=True),
        'group': fields.boolean("Group by partner"),
        'invoice_date': fields.date('Invoiced date'),
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(wizard_invoice_on_picking, self).view_init(cr, uid, fields_list, context=context)
        pick_obj = self.pool.get('stock.picking')
        count = 0
        active_ids = context.get('active_ids',[])
        for pick in pick_obj.browse(cr, uid, active_ids, context=context):
            if pick.stock_journal_id.default_invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == 1 and count:
            raise osv.except_osv(_('Warning !'), _('This picking list does not require invoicing.'))
        if len(active_ids) == count:
            raise osv.except_osv(_('Warning !'), _('None of these picking lists require invoicing.'))
        return res
        
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(wizard_invoice_on_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)

        obj_stock_journal = self.pool.get('stock.journal')
        obj_picking = self.pool.get('stock.picking')
        x = []
        
        record_id = context and context.get('stock_journal', False) or False
        
        stock_journal_ids = obj_stock_journal.search(cr, uid, [('name','=',record_id)])[0]       
        
        stock_journal = obj_stock_journal.browse(cr, uid, stock_journal_ids, context=context)
        
        if stock_journal.allowed_account_journal_ids:
            for journal in stock_journal.allowed_account_journal_ids:
                x.append(journal.id)
                
        #raise osv.except_osv(_('Error !'), _('%s')%x)

        separator_string = _("Create Invoice")
        view = """<?xml version="1.0" encoding="utf-8"?>
                    <form string="Create invoice">
                    <separator string="%s" colspan="4"/>
                    <field name="account_journal_id" domain="[('id','in',%s)]"/>
                    <newline/>
                    <field name="group"/>
                    <newline/>
                    <field name="invoice_date" />
                    <separator string="" colspan="4" />
                    <button special="cancel" string="_Cancel" icon='gtk-cancel'/>
                    <button name="open_invoice" string="Create" type="object" icon="terp-gtk-go-back-rtl"/>
                </form>""" % (separator_string, tuple(x))
                

        view = etree.fromstring(view.encode('utf8'))
        xarch, xfields = self._view_look_dom_arch(cr, uid, view, view_id, context=context)
        view = xarch
        res.update({
            'arch': view
        })
        return res

    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        invoice_ids = []
        action_model = False
        action = {}        
        
        data_pool = self.pool.get('ir.model.data')
        
        res = self.create_invoice(cr, uid, ids, context=context)
        invoice_ids += res.values()
        
        inv_type = context.get('inv_type', False)

        if not invoice_ids:
            raise osv.except_osv(_('Error'), _('No Invoices were created'))
            
            
        # pemilihan view mana yang akan dibuka
        #TODO: pilih view nya yg jenis form aja
        
        if inv_type == "out_invoice":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        elif inv_type == "in_invoice":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
        elif inv_type == "out_refund":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree3")
        elif inv_type == "in_refund":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree4")
            
        #TODO: Karena sudah form yg dibuka bukan tree, maka gunakan res_id, jangan domain 
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
        return action

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['account_journal_id', 'group', 'invoice_date'])
        
        # dapet context new picking nya dari mana yah?
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking # onshipdata_obj.new_picking ini apaan yah?
            onshipdata_obj[ids] = onshipdata_obj.new_picking # onshipdata_obj.new_picking ini apaan yah?
            
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        
        active_ids = context.get('active_ids', [])
        active_picking = picking_pool.browse(cr, uid, context.get('active_id',False), context=context)
        
        inv_type = picking_pool._get_invoice_type(active_picking) # Pertimbangkan untuk override/buat method sendiri
        context['inv_type'] = inv_type
        
        if isinstance(onshipdata_obj[0]['account_journal_id'], tuple):
            onshipdata_obj[0]['account_journal_id'] = onshipdata_obj[0]['account_journal_id'][0]
            
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['account_journal_id'],
              group = onshipdata_obj[0]['group'],
              type = inv_type,
              context=context)
        return res

wizard_invoice_on_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
