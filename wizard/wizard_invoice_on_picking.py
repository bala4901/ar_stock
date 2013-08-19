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
    
    def default_account_journal_id(self, cr, uid, context={}):
        if not context.get('active_model', False) : return False
        obj_stock_journal = self.pool.get('stock.journal')
        obj_model = self.pool.get(context['active_model'])
        obj_detail = self.pool.get('account.invoice_type_line')
        
        model = obj_model.browse(cr, uid, context['active_ids'])[0]
        company_id = model.company_id.id
        
        kriteria = [('name','=',context.get('stock_journal',False))]
        stock_journal_ids = obj_stock_journal.search(cr, uid, kriteria)
        
        if not stock_journal_ids : return False
        
        stock_journal = obj_stock_journal.browse(cr, uid, stock_journal_ids)[0]
        
        kriteria1 = [('invoice_type_id','=',stock_journal.invoice_type_id.id),('company_id','=',company_id)]
        detail_ids = obj_detail.search(cr, uid, kriteria1) 
        
        if not detail_ids : return False
        
        detail = obj_detail.browse(cr, uid, detail_ids)[0]
        
        context['invoice_type'] = stock_journal.invoice_type_id.name
        return detail.journal_id.id

    def default_invoice_type_id(self, cr, uid, context={}):
        if not context.get('active_model', False) : return False
        obj_stock_journal = self.pool.get('stock.journal')
        obj_model = self.pool.get(context['active_model'])
        obj_detail = self.pool.get('account.invoice_type_line')
        
        model = obj_model.browse(cr, uid, context['active_ids'])[0]
        company_id = model.company_id.id
        
        kriteria = [('name','=',context.get('stock_journal',False))]
        stock_journal_ids = obj_stock_journal.search(cr, uid, kriteria)
        
        if not stock_journal_ids : return False
        
        stock_journal = obj_stock_journal.browse(cr, uid, stock_journal_ids)[0]
        
        return stock_journal.invoice_type_id.id
        

    _columns = {
        'account_journal_id' : fields.many2one(string='Account Journal', obj='account.journal', required=True),
        'group': fields.boolean("Group by partner"),
        'invoice_date': fields.date('Invoiced date'),
        'invoice_type_id' : fields.many2one(string='Invoice Type', obj='account.invoice_type'),
    }
    
    _defaults = {
                            'account_journal_id' : default_account_journal_id,
                            'invoice_type_id' : default_invoice_type_id,
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
        

    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #raise osv.except_osv('a', str(context))
        res = self.create_invoice(cr, uid, ids, context=context)
        return {}

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['account_journal_id', 'group', 'invoice_date'])
        wizard = self.browse(cr, uid, ids)[0]
        
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
            
        context['invoice_type'] = wizard.invoice_type_id.name

        #raise osv.except_osv('a','a')
            
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['account_journal_id'],
              group = onshipdata_obj[0]['group'],
              type = inv_type,
              context=context)
        return res

wizard_invoice_on_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
