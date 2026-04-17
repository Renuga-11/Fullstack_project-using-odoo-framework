from odoo import models, fields, api
from odoo.exceptions import UserError


class ExamType(models.Model):
    _name = 'student.exam_type'
    _description = 'Exam Type'
    _order = 'name'

    name = fields.Char(string='Exam Name', required=True, placeholder='e.g., Term 1, Mid Term, Final Exam')
    exam_date = fields.Date(string='Exam Date')
    description = fields.Text(string='Description')
    
    # Related exams
    exam_ids = fields.One2many('student.exam', 'exam_type_id', string='Exam Results')
    
    # Computed fields for exam statistics
    total_students = fields.Integer(string='Total Students', compute='_compute_exam_stats', store=False)
    total_marks = fields.Float(string='Total Marks Obtained', compute='_compute_exam_stats', store=False)
    average_marks = fields.Float(string='Average Marks', compute='_compute_exam_stats', store=False)
    pass_count = fields.Integer(string='Pass Count', compute='_compute_exam_stats', store=False)
    fail_count = fields.Integer(string='Fail Count', compute='_compute_exam_stats', store=False)
    
    def _compute_exam_stats(self):
        for rec in self:
            exams = rec.exam_ids
            rec.total_students = len(exams)
            
            if exams:
                rec.total_marks = sum(exam.marks for exam in exams if exam.marks)
                rec.average_marks = rec.total_marks / len(exams) if len(exams) > 0 else 0
                rec.pass_count = sum(1 for exam in exams if exam.result == 'Pass')
                rec.fail_count = sum(1 for exam in exams if exam.result == 'Fail')
            else:
                rec.total_marks = 0
                rec.average_marks = 0
                rec.pass_count = 0
                rec.fail_count = 0

    def action_send_exam_attendance_message(self):
        """Send message about exam attendance and marks to students"""
        self.ensure_one()
        
        if not self.exam_ids:
            raise UserError('No exam results found for this exam type.')
        
        # Get all students who have exams for this exam type
        students = self.exam_ids.mapped('student_id')
        
        if not students:
            raise UserError('No students found for this exam type.')
        
        # Create a message for the exam
        message_body = f"""
        <h3>Exam Attendance & Marks Report</h3>
        <p><b>Exam Type:</b> {self.name}</p>
        <p><b>Exam Date:</b> {self.exam_date or 'Not set'}</p>
        <p><b>Total Students:</b> {self.total_students}</p>
        <p><b>Pass Count:</b> {self.pass_count}</p>
        <p><b>Fail Count:</b> {self.fail_count}</p>
        <p><b>Average Marks:</b> {self.average_marks:.2f}</p>
        """
        
        # Post message to the exam type record's chatter
        self.message_post(
            body=message_body,
            subject=f'Exam Attendance & Marks - {self.name}',
            message_type='notification',
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Message Sent',
                'message': f'Exam attendance message has been sent to {len(students)} students.',
                'sticky': False,
            }
        }

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Exam name must be unique.')
    ]
