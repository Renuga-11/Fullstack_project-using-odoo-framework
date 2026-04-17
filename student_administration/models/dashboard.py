from odoo import models, fields, api
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)

class StudentDashboard(models.Model):
    _name = 'student.dashboard'
    _description = 'Student Dashboard'

    total_students = fields.Integer(string='Total Students', compute='_compute_statistics')
    attendance_percentage = fields.Float(string='Attendance %', compute='_compute_statistics')
    leave_count = fields.Integer(string='Leave Count', compute='_compute_statistics')
    pass_percentage = fields.Float(string='Pass %', compute='_compute_statistics')

    def _compute_statistics(self):
        for rec in self:
            _logger.info('Computing dashboard statistics for student dashboard')
            
            # Total Students
            student_count = self.env['student.student'].search_count([])
            rec.total_students = student_count
            _logger.info(f'Total students count: {student_count}')

            # Attendance % - calculated as (present + late) / total attendance * 100
            # Late is now considered as present
            all_attendance = self.env['student.attendance'].search([])
            total_attendance = len(all_attendance)
            
            # Count present + late (late is considered as present)
            present_late = all_attendance.filtered(lambda r: r.status in ('present', 'late'))
            present_count = len(present_late)
            
            # Calculate percentage and cap at 100%
            if total_attendance > 0:
                attendance_pct = (present_count / total_attendance) * 100
                rec.attendance_percentage = min(round(attendance_pct, 2), 100.0)
            else:
                rec.attendance_percentage = 0.0

            # Leave Count - only approved leaves
            leave_count = self.env['student.leave'].search_count([('state', '=', 'approved')])
            rec.leave_count = leave_count

            # Pass % - Calculate percentage of students who passed
            # Get unique students with results
            results = self.env['student.result'].search([])
            student_results = {}
            for result in results:
                if result.student_id.id not in student_results:
                    student_results[result.student_id.id] = result
            
            total_students_with_results = len(student_results)
            passed_count = sum(1 for r in student_results.values() if r.result_status == 'Pass')
            
            if total_students_with_results > 0:
                rec.pass_percentage = round((passed_count / total_students_with_results) * 100, 2)
            else:
                rec.pass_percentage = 0.0

    def action_refresh(self):
        self._compute_statistics()
        return {
            'type': 'ir.actions.act_window_refresh',
        }

    def action_diagnose(self):
        """Diagnose and log dashboard statistics for debugging."""
        _logger.info('Running diagnose on student dashboard')
        
        # Log all current statistics
        for rec in self:
            _logger.info(f'Dashboard diagnostics - Total Students: {rec.total_students}')
            _logger.info(f'Dashboard diagnostics - Attendance %: {rec.attendance_percentage}')
            _logger.info(f'Dashboard diagnostics - Leave Count: {rec.leave_count}')
            _logger.info(f'Dashboard diagnostics - Pass %: {rec.pass_percentage}')
        
        return {
            'type': 'ir.actions.act_window_refresh',
        }
