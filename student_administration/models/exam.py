from odoo import models, fields, api

class Exam(models.Model):
    _name = 'student.exam'
    _description = 'Exam'

    exam_type_id = fields.Many2one('student.exam_type', string='Exam Type')
    exam_date = fields.Date(related='exam_type_id.exam_date', string='Exam Date', store=True, readonly=True)
    student_id = fields.Many2one('student.student', string='Student', required=True)
    student_email = fields.Char(related='student_id.email', string='Email', readonly=True)
    student_phone = fields.Char(related='student_id.phone', string='Phone', readonly=True)
    student_class = fields.Char(related='student_id.class_name', string='Department', readonly=True)
    # Keep a stored text copy for dashboards and legacy records.
    subject = fields.Char(string='Subject', compute='_compute_subject', store=True)
    subject_id = fields.Many2one('student.subject', string='Subject')
    marks = fields.Float(string='Marks')
    total_marks = fields.Float(string='Total Marks', default=100)
    percentage = fields.Float(string='Percentage (%)', compute='_compute_exam_metrics', store=True, group_operator='avg')
    result = fields.Char(string='Result', compute='_compute_exam_metrics', store=True)
    grade = fields.Char(string='Grade', compute='_compute_exam_metrics', store=True)

    @api.depends('subject_id', 'subject_id.name')
    def _compute_subject(self):
        for record in self:
            record.subject = record.subject_id.name or False

    def _get_exam_metrics(self):
        self.ensure_one()
        total_marks = self.total_marks or 0.0
        marks = self.marks or 0.0

        if total_marks <= 0:
            return {
                'percentage': 0.0,
                'result': 'Fail',
                'grade': 'F',
            }

        percentage = round((marks / total_marks) * 100, 2)
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 80:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B+'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 50:
            grade = 'C'
        elif percentage >= 40:
            grade = 'D'
        else:
            grade = 'F'

        return {
            'percentage': percentage,
            'result': 'Pass' if marks >= 0.4 * total_marks else 'Fail',
            'grade': grade,
        }

    @api.depends('marks', 'total_marks')
    def _compute_exam_metrics(self):
        for record in self:
            metrics = record._get_exam_metrics()
            record.percentage = metrics['percentage']
            record.result = metrics['result']
            record.grade = metrics['grade']

    @api.onchange('marks', 'total_marks')
    def _onchange_exam_scores(self):
        for record in self:
            metrics = record._get_exam_metrics()
            record.percentage = metrics['percentage']
            record.result = metrics['result']
            record.grade = metrics['grade']

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._compute_subject()
        records._compute_exam_metrics()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {'subject_id', 'marks', 'total_marks'} & set(vals):
            self._compute_subject()
            self._compute_exam_metrics()
        return res
