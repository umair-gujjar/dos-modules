from openerp import models,  fields,  api
import datetime
from datetime import date, datetime, timedelta
import time
import math
class account_anlytic_line_inherit(models.Model):
    _inherit='account.analytic.line'
    task_hourly_entries = fields.Integer('Hourly Entries')
    task_fixed_entries = fields.Integer('Fixed Entries')
    task_assigned_to = fields.Many2one('res.users','Task Assigned To')
    hours_materials = fields.Float('Fixed Hours')
    task_assigned_name = fields.Many2one('project.task','Task Name')
    task_mat_id = fields.Many2one('project.task.materials','Task Material ID')
    task_wrk_id =  fields.Many2one('project.task.work','Task Material ID')
    task_wrko_ids =  fields.Many2one('project.task.work','Task Material ID')
    total_no_of_hours = fields.Float('Total Hours')
    total_no_of_entries = fields.Float('Total Entries')
    check_analytic = fields.Char('Delete Analytic Line')
    overtime_amount_field = fields.Float('Overtime ')
    task_name = fields.Many2one('project.task','Task Ref')
    date_deadline = fields.Date('Deadline')
    date_start = fields.Datetime('Date Start')
    date_stop = fields.Datetime('Date Stop')
    #overtime_amount = fields.Float('Over Time')
    @api.multi
    def recalculate_amount(self):
        analytic_product_amount =  self.product_id.standard_price
        analytic_quantity = self.unit_amount
        current_amount = self.amount
        if current_amount < 0:
            negative_amount = -1 * current_amount
            divide_amount = current_amount/negative_amount
            self.amount =  divide_amount * analytic_product_amount * analytic_quantity
        elif current_amount > 0:
            divide_amount = current_amount/current_amount
            self.amount =  divide_amount * analytic_product_amount * analytic_quantity
        else:
            self.amount = analytic_product_amount * analytic_quantity
    @api.one
    def overtime_amount(self):
        analytic_product_amount =  self.product_id.standard_price
        analytic_quantity = self.unit_amount
        current_amount = self.amount
        overtime_amount_bonus = self.overtime_amount_field
        if current_amount < 0:
            negative_amount = -1 * current_amount
            divide_amount = current_amount/negative_amount
            self.amount =  divide_amount * analytic_product_amount * analytic_quantity * overtime_amount_bonus
        elif current_amount > 0:
            divide_amount = current_amount/current_amount
            self.amount =  divide_amount * analytic_product_amount * analytic_quantity * overtime_amount_bonus
        else:
            self.amount =  analytic_product_amount * analytic_quantity * overtime_amount_bonus    


    @api.multi
    def do_update_ent(self, task_mat_id):
        analytic_line_rec = self.env['account.analytic.line'].search([])
        task_hours_mat = self.task_mat_id.hours
        for i in analytic_line_rec:
            if i.journal_id.code == "TS":
                i.total_no_of_hours = i.unit_amount
            else:
                i.total_no_of_hours = task_hours_mat
                i.hours_materials = task_hours_mat


class Task(models.Model):
    _inherit = "project.task"
    @api.multi
    def write(self, material_ids):
        for task in self:
            res = super(Task, self).write(material_ids)
            if task.material_ids:
                task.analytic_line_ids.unlink()
                task.material_ids.create_analytic_line()
        return res
    def delete_button_analytic(self, material_ids):
        for task in self:
            res = super(Task, self).write(material_ids)
            if task.material_ids:
                task.analytic_line_ids.unlink()
        return res
    @api.multi
    def unlink(self):
        #self.unlink_stock_move()
        self.analytic_line_ids.unlink()
        return super(Task, self).unlink()

class task_project_matrials_customize(models.Model):
    _inherit='project.task.materials'
    def _prepare_analytic_line(self):
        product = self.product_id
        company_id = self.env['res.company']._company_default_get(
            'account.analytic.line')
        journal = self.env.ref(
            'project_task_materials_stock.analytic_journal_sale_materials')
        analytic_account = getattr(self.task_id, 'analytic_account_id', False)\
            or self.task_id.project_id.analytic_account_id
        #test_date = datetime.strftime(self.date,"%Y-%m-%d %H:%M:%S")
        res = {
            #'user_id': self.done_by.id,
            #'hours_materials' : self.hours,
            #'task_assigned_name' : self.task_id.id,
            #'name': self.task_id.name + ': ' + self.description,
            #'ref': self.task_id.name,
            #'date': self.test_date,
            #'product_id': product.id,
            #'journal_id': journal.id,
            #'unit_amount': self.quantity,
            #'account_id': analytic_account.id,

            'user_id': self.done_by.id,
            'hours_materials' : self.hours,
            'total_no_of_hours' : self.hours,
            'task_assigned_name' : self.task_id.id,
            'name': self.task_id.name + ': ' + self.description,
            'ref': self.task_id.name,
            'product_id': product.id,
            'journal_id': journal.id,
            'unit_amount': self.quantity,
            'date': self.test_date,
            'task_mat_id' : self.id,
            'total_no_of_entries': self.quantity,
            'account_id': analytic_account.id,
        }
        analytic_line_obj = self.pool.get('account.analytic.line')
        amount_dic = analytic_line_obj.on_change_unit_amount(
            self._cr, self._uid, self._ids, product.id, self.uos_qty(),
            company_id, False, journal.id, self._context)
        res.update(amount_dic['value'])
        res['product_uom_id'] = self.product_uom.id
        to_invoice = getattr(self.task_id.project_id.analytic_account_id,
                             'to_invoice', None)
        if to_invoice is not None:
            res['to_invoice'] = to_invoice.id
        return res
    @api.multi
    def create_analytic_line(self):
        for line in self:
            move_id = self.env['account.analytic.line'].create(
                line._prepare_analytic_line())
            line.analytic_line_id = move_id.id

from openerp import models,  fields,  api
class project_view_form_button(models.Model):
    _inherit = "project.project"
    @api.multi
    def do_update_des(self):
        print self.description
        prj_des = self.description
        for task_all in self.tasks:
            task_all.description = prj_des
            print task_all.description



from openerp import models,  fields,  api
class product_in_ptm_line(models.Model):
    _inherit = "project.task.materials"
    @api.onchange('product_id','quantity')
    def onchange_product_hours(self):
        product_in_project_line = self.product_id.standard_price
        self.amount_recalculate = product_in_project_line * self.quantity

class product_in_ptw_line(models.Model):
    _inherit = "project.task.work"
    @api.onchange('hours')
    def onchange_product_hours(self):
        test = self.user_id
        emp_obj_all = self.env['hr.employee']
        emp_obj_id = emp_obj_all.search([])
        for each_emp in emp_obj_id:
            if each_emp.user_id == test:
                product_price = each_emp.product_id.standard_price
                print product_price
        self.amount_recalculate = product_price * self.hours

