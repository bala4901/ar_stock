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
from datetime import datetime, date

class wizard_print_stock_card(osv.osv_memory):
    _name = 'stock.wizard_print_stock_card'
    _description = 'Wizard Print Stock Card'
    
    _columns = {
                            'product_id' : fields.many2one(string='Product', obj='product.product', required=True),
                            'location_id' : fields.many2one(string='Location', obj='stock.location', required=True),
                            'from_date' : fields.date(string='From Date', required=True),
                            'to_date' : fields.date(string='To Date', required=True),
                            }
                            
    def button_print_report(self, cr, uid, ids, data, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        obj_stock_move = self.pool.get('stock.move')
        obj_product = self.pool.get('product.product')

        from_date = date(int(wizard.from_date[0:4]), int(wizard.from_date[5:7]),int(wizard.from_date[8:10]))
        first_date_ordinal = datetime.toordinal(from_date) - 1
        first_date = date.fromordinal(first_date_ordinal).strftime('%Y-%m-%d')

        stock_awal = obj_product._product_available(cr, uid, [wizard.product_id.id], ['qty_available'], arg=False, context={'location':wizard.location_id.id, 'to_date': first_date + ' 23:59:59'})[wizard.product_id.id]['qty_available']        

        stock_akhir = obj_product._product_available(cr, uid, [wizard.product_id.id], ['qty_available'], arg=False, context={'location':wizard.location_id.id, 'to_date': wizard.to_date + ' 23:59:00'})[wizard.product_id.id]['qty_available']        

        kriteria = ['|',('location_id','=',wizard.location_id.id), ('location_dest_id','=',wizard.location_id.id) ,('product_id','=',wizard.product_id.id), ('date','>=',wizard.from_date + ' 00:00:00'), ('date','<=',wizard.to_date + ' 23:59:00'),('state', '=', 'done')]

        move_ids = obj_stock_move.search(cr, uid, kriteria)

        if move_ids:
            data['ids'] = move_ids
            data['model'] = 'stock.move'
            data['output_type'] = 'pdf'
            val =   {
                        'from_date' : '%s 00:00:00' % (wizard.from_date),
                        'to_date' : '%s 23:59:00' % (wizard.to_date),
                        'location_id' : wizard.location_id.id,
                        'location_name' : wizard.location_id.name,
                        'product_name' : wizard.product_id.name,
                        'stock_awal' : stock_awal,
                        'stock_akhir' : stock_akhir,
                        }
            data['variables'] = val
        else:
            data['ids'] = [0]
            data['model'] = 'stock.move'
            data['output_type'] = 'pdf'
            val =   {
                        'from_date' : '%s 00:00:00' % (wizard.from_date),
                        'to_date' : '%s 23:59:00' % (wizard.to_date),
                        'location_id' : wizard.location_id.id,
                        'location_name' : wizard.location_id.name,
                        'product_name' : wizard.product_id.name,
                        'stock_awal' : stock_awal,
                        'stock_akhir' : stock_akhir,
                        }
            data['variables'] = val

        return {'type': 'ir.actions.report.xml', 'report_name': 'stock.report_stock_card', 'datas': data, 'context' : {'pentaho_defaults' : {'from_date' : wizard.from_date}}}
                          
wizard_print_stock_card()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

