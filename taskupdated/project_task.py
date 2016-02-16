from openerp.osv import fields, osv
from openerp.tools.translate import _
import datetime
from datetime import date, datetime, timedelta
import time
import math


class project_description(osv.Model):
    _inherit = 'project.project'
    _columns={
    'description' :fields.text(string='Work summary'),
    'product_relation' : fields.many2many('product.product', string="Select Multiple products"),
    'source' : fields.selection([
        ('Elance','Elance'),('Odesk','Odesk'),('Direct','Direct'),('Others','Others'),], string='Source'),
    'link' : fields.char("Link"),
    'hourly_check' : fields.boolean("For Hourly Work", help="If you check this field in task hourly menu will be shown. "),
    'fixed_check' : fields.boolean("For Fixed Entries", help="If you check this field in task Fixed menu will be shown. "),
    
    }
    def onchang_this_field(self, cr, uid, ids, product_relation,  context=None):
        res = {}
        if product_relation:
            print "000000000000000000000000000000000"
            print "product relation as fellows : ",product_relation[0][2]
            print "*********************************"
            print "000000000000000000000000000000000"


class task_project(osv.Model): #declaring/creating new class
    _inherit = 'project.task' #inheriting class

    def on_change_project_id_task(self, cr, uid, ids, project_id, context=None): # function for getting description from project to task on change
        if not project_id: # Condition for product_id
            return {}
        project_in_task = self.pool.get('project.project').browse(cr, uid, project_id, context=context) #getting all data from project on basis of product_id
        descrip_task = project_in_task.description #assiging value of description field value in project to descrip_task variable
        hour_check = project_in_task.hourly_check
        fix_check = project_in_task.fixed_check
        proj_relation_field = project_in_task.product_relation
        print "*********************************"
        print proj_relation_field
        print "*********************************"
        print hour_check
        print "*********************************"
        print descrip_task
        print "*********************************"
        # writing the value of descrip_task variable to the field description in task
        return {
                    'value': {
                    'description': descrip_task,
                    'hourly_check': hour_check,
                    'fixed_check' : fix_check,
                    #'proj_relation': proj_relation_field,
                }
                }


    # creating field in the database
    _columns={
    #'proj_relation' : fields.many2many('product.product', string="Select Multiple products"),
    #'product_id':fields.many2one('product.product','Products', domain="[('id', 'in', proj_relation[0][2])]" ),
    'hourly_check' : fields.boolean("Hourly"),
    'fixed_check' : fields.boolean("Fixed"),
    'work_ids': fields.one2many('project.task.work', 'task_id', 'Work done',),
    'description' : fields.text('Project Description', readonly=True),
    'worksheet_link' : fields.char('Worksheet link', ),
    'Rate_per_entry' : fields.float('Rate per entry', ),
    'start_tracker' : fields.selection([
        ('Elance','Elance'),('Upwork','Upwork'),('No','No'),], string='Start Tracker',),
    }

    def onchang_this_field(self, cr, uid, ids, product_id,  context=None):
        res = {}
        if product_id:
            project_in_task = self.pool.get('project.task').browse(cr, uid, product_id, context=context)
            proj_relation_field = project_in_task.proj_relation
            print "000000000000000000000000000000000"
            print "product relation as fellows : ",proj_relation_field
            print "*********************************"
            print "000000000000000000000000000000000"
    
class task_update(osv.Model):
    _inherit = 'project.task.work'

    #fields
    def STask(self, cr, uid, ids, SDate, EDate, context=None):
        res = {}
        if SDate and EDate:
            dt_s_obj = datetime.strptime(SDate,"%Y-%m-%d %H:%M:%S")
            dt_e_obj = datetime.strptime(EDate,"%Y-%m-%d %H:%M:%S")
            timedelta = dt_e_obj - dt_s_obj

            res['Diff_date'] = timedelta
        return {'value': res}
    _columns={
    'name': fields.char('Work summary'),
    'date': fields.datetime('Date', select="1"),
    'task_id': fields.many2one('project.task', 'Task', ondelete='cascade', required=True, select="1"),
    'hours': fields.float('Time Spent'),
    'user_id': fields.many2one('res.users', 'Done by', required=True, select="1"),
    'company_id': fields.related('task_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
    'entries_col' : fields.integer("No of Entries"),
    #'sal_col': fields.integer(string="Salary Per Entries"),
    #'total_sal':fields.integer('Total Salary', readonly=True),
    'SDate': fields.datetime('Start Date', readonly=True),
    'EDate': fields.datetime('End Date', readonly=True),
    'Diff_date': fields.char('Diffenence in Time', readonly=True),
    'InitiateTask': fields.datetime('InitiateTask'),
    'check_analytic' : fields.char('Analytic Edit'),
    'amount_recalculate' : fields.float(string='Amount'),


    }

    _defaults = {
                'Diff_date':lambda obj, cr, uid, context: '/',
     }

    def MyInitiateTask(self, cr, uid, ids, context=None):
        res = {}
        res = datetime.now()
        result = self.write(cr, uid, ids, {'SDate': res}, context=context)
        return result

    def MyFinalTask(self, cr, uid, ids, context=None):
        res = {}
        res = datetime.now()
        finalresult = self.write(cr, uid, ids, {'EDate': res}, context=context)
        brw_obj = self.pool.get('project.task.work').browse(cr, uid, ids, context=context)
        print brw_obj.SDate
        print brw_obj.EDate
        if brw_obj.SDate and brw_obj.EDate:
            dt_s_obj = datetime.strptime(brw_obj.SDate,"%Y-%m-%d %H:%M:%S")
            dt_e_obj = datetime.strptime(brw_obj.EDate,"%Y-%m-%d %H:%M:%S")
            timedelta = dt_e_obj - dt_s_obj
            sec = timedelta.seconds
            #dys = sec / (3600 * 24)
            #hrs = (sec / 3600) % 24
            #minuts = (sec / 60) % 60
            #float_mint = sec/60.0
            float_hours = sec/3600.0
            print "*********************************"
            print float_hours
            print "000000000000000000000000000000000"
            result = self.write(cr, uid, ids, {'Diff_date': timedelta, 'hours':float_hours,}, context=context)
        return finalresult, result   

    def onchange_result(self, cr, uid, ids, sal_col, entries_col, context=None):
        res = {}
        if sal_col and entries_col:
            res['total_sal'] = sal_col * entries_col
        return {'value': res}
class task_project_matrials(osv.Model):
    _inherit = 'project.task.materials'
    def on_change_project_id_task(self, cr, uid, ids, project_id, context=None): # function for getting description from project to task on change
        if not project_id: # Condition for product_id
            return {}
        project_in_task = self.pool.get('project.project').browse(cr, uid, project_id, context=context) #getting all data from project on basis of product_id
        #descrip_task = project_in_task.description #assiging value of description field value in project to descrip_task variable
        #hour_check = project_in_task.hourly_check
        proj_relation_field = project_in_task.product_relation
        print "*********************************"
        print proj_relation_field
        print "*********************************"
        print "*********************************"
        # writing the value of descrip_task variable to the field description in task
        return {
                    'value': {
                    'proj_relation_task': proj_relation_field,
                }
                }
    def _get_project(self, cr, uid, context=None):
        #ADD YOUR LOGIC
        res = self.pool.get('project.task').browse(cr, uid, context=context)
        print res.project_id
        return res.project_id
    def STask(self, cr, uid, ids, SDate, EDate, context=None):
        res = {}
        if SDate and EDate:
            dt_s_obj = datetime.strptime(SDate,"%Y-%m-%d %H:%M:%S")
            dt_e_obj = datetime.strptime(EDate,"%Y-%m-%d %H:%M:%S")
            timedelta = dt_e_obj - dt_s_obj

            res['Diff_date'] = timedelta
        return {'value': res}

    _columns={
    #'project_id' : fields.many2one('project.project',string="Project",),
    #'proj_relation_task' : fields.many2many('product.product', string="Select Multiple products"),
    #'product_id':fields.many2one('product.product','Product', domain="[('id', 'in', proj_relation_task[0][2])]" ),
    'product_id':fields.many2one('product.product', 'Project Name' ),
    'description' :fields.char(string='Work summary'),
    'date': fields.datetime('Date', select="1"),
    'hours' : fields.float(string='Time Spent'),
    'SDate': fields.datetime('Start Date', readonly=True),
    'EDate': fields.datetime('End Date', readonly=True),
    'Diff_date': fields.char('Diffenence in Time'),
    #'user_id': fields.many2one('res.users', 'Done by', required=True, select="1"),
    'done_by' :fields.many2one('res.users', 'Done by Task', required=True, select="1"),
    'amount_recalculate' : fields.float(string='Amount'),
    'test_date': fields.datetime('Date', select="1"),
    #'test_proj_produts_rel':fields.many2many('product.product', string="Select Multiple products"),
    #'test_product_id' : fields.many2one('product.product', string="task products test"),
    #'create_uid': fields.many2one('res.users', 'created by', required=True, select="1"),

    }
    _defaults = {
                #'project_id':_get_project,
                'Diff_date':lambda obj, cr, uid, context: '/',
                'date' : lambda obj, cr, uid, context: datetime.now(),
                'done_by': lambda obj, cr, uid, context: uid,
     }
    def ochange_test_date(self, cr, uid, ids, date,  context=None):
        res = {}
        if date:
            dt_s_obj = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
            timedelta_test = dt_s_obj + timedelta(hours=5)

            res['test_date'] = timedelta_test
        return {'value': res}
    def MyInitiateTask(self, cr, uid, ids, context=None):
        res = {}
        res = datetime.now()
        result = self.write(cr, uid, ids, {'SDate': res}, context=context)
        return result

    def MyFinalTask(self, cr, uid, ids, context=None):
        res = {}
        res = datetime.now()
        finalresult = self.write(cr, uid, ids, {'EDate': res}, context=context)
        brw_obj = self.pool.get('project.task.materials').browse(cr, uid, ids, context=context)
        print brw_obj.SDate
        print brw_obj.EDate
        if brw_obj.SDate and brw_obj.EDate:
            dt_s_obj = datetime.strptime(brw_obj.SDate,"%Y-%m-%d %H:%M:%S")
            dt_e_obj = datetime.strptime(brw_obj.EDate,"%Y-%m-%d %H:%M:%S")
            timedelta = dt_e_obj - dt_s_obj
            sec = timedelta.seconds
            #dys = sec / (3600 * 24)
            #hrs = (sec / 3600) % 24
            #minuts = (sec / 60) % 60
            #float_mint = sec/60.0
            float_hours = sec/3600.0
            print "*********************************"
            print float_hours
            print "000000000000000000000000000000000"
            result = self.write(cr, uid, ids, {'Diff_date': timedelta, 'hours':float_hours,}, context=context)
        return finalresult, result,
class task_description_custom(osv.Model):
    _inherit = 'project.task'
#"""    def _hours_get_mat(self, cr, uid, ids, field_names, args, context=None):
#        res = {}
#        cr.execute("SELECT task_id, COALESCE(SUM(hours),0) FROM project_task_work WHERE task_id IN %s GROUP BY task_id",(tuple(ids),))
#        hours = dict(cr.fetchall())
#        for task in self.browse(cr, uid, ids, context=context):
#            res[task.id] = {'effective_hours': hours.get(task.id, 0.0)}
#            #res[task.id]['delay_hours'] = res[task.id]['total_hours'] - task.planned_hours
#            #res[task.id]['progress'] = 0.0
#            #if (task.remaining_hours + hours.get(task.id, 0.0)):
#            #    res[task.id]['progress'] = round(min(100.0 * hours.get(task.id, 0.0) / res[task.id]['total_hours'], 99.99),2)
#            # TDE CHECK: if task.state in ('done','cancelled'):
#            #if task.stage_id and task.stage_id.fold:
#            #    res[task.id]['progress'] = 100.0
#        return res
#    def _get_task_mat(self, cr, uid, ids, context=None):
#        result = {}
#        for work in self.pool.get('project.task.materials').browse(cr, uid, ids, context=context):
#            if work.task_id: result[work.task_id.id] = True
#        return result.keys()"""
    _columns={
    'describe' :fields.text(string='Task Description'),
    #'effective_hours': fields.function(_hours_get_mat, string='Hours Spent', multi='hours', help="Computed using the sum of the task work done.",
    #        store = {
    #            'project.task': (lambda self, cr, uid, ids, c={}: ids, ['material_ids', 'remaining_hours', 'planned_hours'], 10),
    #            'project.task.materials': (_get_task_mat, ['hours'], 10),
    #        }),
    }
#Project description field is set from odoo inside > edit form view
#hourly_check invisible is also set from odoo inside > elit from view
