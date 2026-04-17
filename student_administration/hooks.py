from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    students = env['student.student'].search([])
    if not students:
        return

    students._compute_attendance_status()
    students._compute_overall_pass()
    env.flush_all()
