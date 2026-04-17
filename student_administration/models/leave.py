from odoo import fields, models


class Leave(models.Model):
    _inherit = 'student.leave'

    student_email = fields.Char(
        related='student_id.email',
        string='Email',
        readonly=True
    )
    student_phone = fields.Char(
        related='student_id.phone',
        string='Phone',
        readonly=True
    )
    student_class = fields.Char(
        related='student_id.class_name',
        string='Department',
        readonly=True
    )
    leave_from = fields.Date(
        related='date_from',
        string='Leave From',
        store=True,
        readonly=False
    )
    leave_to = fields.Date(
        related='date_to',
        string='Leave To',
        store=True,
        readonly=False
    )
    leave_reason = fields.Selection(
        related='leave_type',
        string='Reason Type',
        store=True,
        readonly=False
    )
    no_of_days = fields.Integer(
        related='number_of_days',
        string='Number of Days',
        store=True,
        readonly=True
    )
