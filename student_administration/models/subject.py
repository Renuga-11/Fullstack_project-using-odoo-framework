from odoo import models, fields, api

class Subject(models.Model):
    _name = 'student.subject'
    _description = 'Subject'
    _order = 'name'

    name = fields.Char(string='Subject Name', required=True)
    code = fields.Char(string='Subject Code')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Subject name must be unique.')
    ]
