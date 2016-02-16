from openerp.osv import fields, osv
from openerp.tools.translate import _
class validate_account_move_lines(osv.osv_memory):
    _name = "dos.account.analytic.lines"
    _description = "Validate Account  Lines"
    _columns={
    'over_time' : fields.float('Over Time Amount'),
    }

    def dos_recalculate_amount(self, cr, uid, ids, context=None):
        obj_move_line = self.pool.get('account.analytic.line')
        move_ids = []
        if context is None:
            context = {}
        data_line = obj_move_line.browse(cr, uid, context['active_ids'], context)
        for line in data_line:
            analytic_product_amount =  line.product_id.standard_price
            analytic_quantity = line.unit_amount
            current_amount = line.amount
            if current_amount < 0:
                negative_amount = -1 * current_amount
                divide_amount = current_amount/negative_amount
                line.amount =  divide_amount * analytic_product_amount * analytic_quantity
            elif current_amount > 0:
                divide_amount = current_amount/current_amount
                line.amount =  divide_amount * analytic_product_amount * analytic_quantity
            else:
                line.amount = analytic_product_amount * analytic_quantity

            print "Code **************************"
        return {'type': 'ir.actions.act_window_close'}

    def dos_recalculate_overtime(self, cr, uid, ids, context=None):
        obj_move_line = self.pool.get('account.analytic.line')
        move_ids = []
        if context is None:
            context = {}
        brw_obj = self.pool.get('dos.account.analytic.lines').browse(cr, uid, ids, context=context)
        data_line = obj_move_line.browse(cr, uid, context['active_ids'], context)
        for line in data_line:
            analytic_product_amount =  line.product_id.standard_price
            analytic_quantity = line.unit_amount
            current_amount = line.amount
            #overtime_amount_bonus = line.overtime_amount_field
            overtime_amount_bonus = brw_obj.over_time
            if current_amount < 0:
                negative_amount = -1 * current_amount
                divide_amount = current_amount/negative_amount
                line.amount =  divide_amount * analytic_product_amount * analytic_quantity * overtime_amount_bonus
            elif current_amount > 0:
                divide_amount = current_amount/current_amount
                line.amount =  divide_amount * analytic_product_amount * analytic_quantity * overtime_amount_bonus
            else:
                line.amount =  analytic_product_amount * analytic_quantity * overtime_amount_bonus   
            print "Code **************************"
        return {'type': 'ir.actions.act_window_close'}