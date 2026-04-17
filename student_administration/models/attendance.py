from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, time, timedelta

class Attendance(models.Model):
    _name = 'student.attendance'
    _description = 'Attendance'

    student_id = fields.Many2one('student.student', string='Student', required=True)
    student_email = fields.Char(related='student_id.email', string='Email', readonly=True)
    student_phone = fields.Char(related='student_id.phone', string='Phone', readonly=True)
    student_class = fields.Char(related='student_id.class_name', string='Department', readonly=True)
    date = fields.Date(string='Date', default=lambda self: fields.Date.today())
    check_in = fields.Float(string='Check In Time (Hours)', digits=(12, 2), help="Enter time in hours (e.g., 9.5 for 9:30 AM)")
    check_out = fields.Float(string='Check Out Time (Hours)', digits=(12, 2), help="Enter time in hours (e.g., 17.5 for 5:30 PM)")
    late_minutes = fields.Integer(string='Late Minutes', compute='_compute_late_minutes', store=True)
    status = fields.Selection([
        ('present', 'Present'), 
        ('absent', 'Absent'), 
        ('late', 'Late')
    ], string='Status', compute='_compute_status', store=True)

    @api.constrains('check_in', 'check_out')
    def _check_times(self):
        for rec in self:
            if rec.check_in is not False:
                if rec.check_in < 0 or rec.check_in > 24:
                    raise ValidationError('Check in time must be between 0 and 24 hours.')
            if rec.check_out is not False:
                if rec.check_out < 0 or rec.check_out > 24:
                    raise ValidationError('Check out time must be between 0 and 24 hours.')
            if rec.check_in is not False and rec.check_out is not False:
                if rec.check_out < rec.check_in:
                    raise ValidationError('Check out time cannot be before check in time.')

    @api.depends('check_in')
    def _compute_late_minutes(self):
        for rec in self:
            if rec.check_in:
                # 9:00 AM = 9.0 hours
                if rec.check_in > 9.0:
                    rec.late_minutes = int((rec.check_in - 9.0) * 60)
                else:
                    rec.late_minutes = 0
            else:
                rec.late_minutes = 0

    @api.depends('check_in', 'late_minutes')
    def _compute_status(self):
        for rec in self:
            if not rec.check_in:
                rec.status = 'absent'
            elif rec.late_minutes > 0:
                rec.status = 'late'
            else:
                rec.status = 'present'
