from odoo import models, fields, api

class Skill(models.Model):
    _name = 'student.skill'
    _description = 'Skill'
    _order = 'name'

    name = fields.Char(string='Skill Name', required=True)
    category = fields.Char(string='Category')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Skill name must be unique.')
    ]
