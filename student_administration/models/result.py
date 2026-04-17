from odoo import models, fields, api

class Result(models.Model):
    _name = 'student.result'
    _description = 'Student Result'

    student_id = fields.Many2one(
        'student.student', 
        string='Student', 
        required=True
    )
    get_students_with_exams = fields.Many2many(
        'student.student',
        compute='_compute_students_with_exams',
        string='Students with Exam Results'
    )
    exam_type_id = fields.Many2one(
        'student.exam_type',
        string='Exam'
    )
    exam_id = fields.Many2one(
        'student.exam',
        string='Exam'
    )
    exam_ids = fields.One2many('student.exam', 'student_id', string='Exam Results')
    student_email = fields.Char(related='student_id.email', string='Email', readonly=True)
    student_class = fields.Char(related='student_id.class_name', string='Department', readonly=True)
    total_marks = fields.Float(string='Total Marks (Out of 500)', compute='_compute_total_marks', store=True)
    percentage = fields.Float(string='Percentage (%)', compute='_compute_percentage', store=True, group_operator='avg')
    rank = fields.Integer(string='Rank', compute='_compute_rank', store=True)
    result_status = fields.Char(string='Result Status', compute='_compute_result_status', store=True)
    grade = fields.Char(string='Grade', compute='_compute_grade', store=True)
    date = fields.Date(string='Date', default=lambda self: fields.Date.today())

    MAX_MARKS = 500  # Total marks out of 500 (5 subjects x 100 marks each)

    @api.depends('exam_ids')
    def _compute_students_with_exams(self):
        # Get all students who have at least one exam result
        students_with_exams = self.env['student.exam'].search([]).mapped('student_id')
        self.get_students_with_exams = [(6, 0, students_with_exams.ids)]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        # Only show students who have exam results
        if not args:
            students_with_exams = self.env['student.exam'].search([]).mapped('student_id').ids
            args = [('id', 'in', students_with_exams)]
        return super(Result, self)._name_search(name, args=args, operator=operator, limit=limit)

    @api.depends('exam_ids', 'student_id')
    def _compute_total_marks(self):
        for rec in self:
            if rec.student_id:
                # Get all exams (subjects) for this student - each subject is out of 100
                exams = self.env['student.exam'].search([('student_id', '=', rec.student_id.id)])
                rec.total_marks = sum(exam.marks for exam in exams)
            else:
                rec.total_marks = 0.0

    @api.depends('total_marks', 'exam_ids')
    def _compute_percentage(self):
        for rec in self:
            # Calculate percentage out of 100 (total_marks is out of 500)
            if self.MAX_MARKS > 0:
                rec.percentage = round((rec.total_marks / self.MAX_MARKS) * 100, 2)
            else:
                rec.percentage = 0.0

    @api.depends('percentage', 'exam_ids', 'student_id')
    def _compute_rank(self):
        # Get all results and sort by percentage (highest first)
        all_results = self.search([])
        sorted_results = all_results.sorted(key=lambda r: r.percentage or 0, reverse=True)
        
        # Assign rank based on percentage (highest = 1)
        for rank, result in enumerate(sorted_results, start=1):
            result.rank = rank

    @api.depends('exam_ids', 'student_id')
    def _compute_result_status(self):
        for rec in self:
            if rec.student_id:
                # Search for all exams for this student
                exams = self.env['student.exam'].search([('student_id', '=', rec.student_id.id)])
                if exams:
                    has_failed = False
                    for exam in exams:
                        exam_result = exam.result
                        # If exam has marks < 40%, it's a fail
                        if exam.marks and exam.total_marks:
                            if exam.marks < 0.4 * exam.total_marks:
                                has_failed = True
                                break
                    rec.result_status = 'Fail' if has_failed else 'Pass'
                else:
                    rec.result_status = 'Fail'
            else:
                rec.result_status = 'Fail'

    @api.depends('percentage', 'exam_ids')
    def _compute_grade(self):
        for rec in self:
            if rec.percentage >= 90:
                rec.grade = 'A+'
            elif rec.percentage >= 80:
                rec.grade = 'A'
            elif rec.percentage >= 70:
                rec.grade = 'B+'
            elif rec.percentage >= 60:
                rec.grade = 'B'
            elif rec.percentage >= 50:
                rec.grade = 'C'
            elif rec.percentage >= 40:
                rec.grade = 'D'
            else:
                rec.grade = 'F'
