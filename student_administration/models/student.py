from odoo import api, fields, models


class Student(models.Model):
    _inherit = 'student.student'

    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    image = fields.Binary(string='Photo')
    skills = fields.Text(string='Skills')
    active = fields.Boolean(string='Active', default=True)
    attendance_ids = fields.One2many('student.attendance', 'student_id', string='Attendance Records')
    attendance_status = fields.Selection(
        [('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')],
        string='Attendance Status',
        compute='_compute_attendance_status',
        store=True,
    )
    exam_ids = fields.One2many('student.exam', 'student_id', string='Exam Results')
    overall_pass = fields.Boolean(
        string='Passed All Exams',
        compute='_compute_overall_pass',
        store=True,
    )

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            rec.age = rec._get_age_from_birthdate(today)

    @api.depends('attendance_ids.status', 'attendance_ids.date')
    def _compute_attendance_status(self):
        for rec in self:
            if not rec.attendance_ids:
                rec.attendance_status = 'absent'
                continue
            latest_attendance = rec.attendance_ids.sorted(
                key=lambda att: (att.date or fields.Date.from_string('1900-01-01'), att.id)
            )[-1]
            rec.attendance_status = latest_attendance.status or 'absent'

    @api.depends('exam_ids.result', 'exam_ids.marks', 'exam_ids.total_marks')
    def _compute_overall_pass(self):
        for rec in self:
            exams = rec.exam_ids
            rec.overall_pass = bool(exams) and all(exam.result == 'Pass' for exam in exams)

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        today = fields.Date.today()
        for rec in self:
            rec.age = rec._get_age_from_birthdate(today)

    def _get_age_from_birthdate(self, today):
        self.ensure_one()
        if not self.date_of_birth:
            return 0

        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return max(age, 0)
