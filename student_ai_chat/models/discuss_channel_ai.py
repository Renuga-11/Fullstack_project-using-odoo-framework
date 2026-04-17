import logging
from html import escape

from markupsafe import Markup

from odoo import models

_logger = logging.getLogger(__name__)


class DiscussChannelAI(models.Model):
    _inherit = "discuss.channel"

    def _truncate_cell(self, value, max_length=30):
        text = str(value or "N/A").strip()
        if len(text) <= max_length:
            return text
        return f"{text[: max_length - 3]}..."

    def _format_table_text(self, headers, rows, max_width=30):
        formatted_rows = [
            [self._truncate_cell(cell, max_width) for cell in row]
            for row in rows
        ]
        normalized_rows = [[str(cell) for cell in row] for row in formatted_rows]
        header_text = [str(header).strip() for header in headers]

        column_widths = []
        for index, header in enumerate(header_text):
            values = [row[index] if index < len(row) else "" for row in normalized_rows]
            column_widths.append(max(len(header), *(len(value) for value in values)))

        def _format_line(values):
            return " | ".join(
                value.ljust(column_widths[index])
                for index, value in enumerate(values)
            ).rstrip()

        lines = [_format_line(header_text), "-" * len(_format_line(header_text))]
        lines.extend(_format_line(row) for row in normalized_rows)
        return "\n".join(lines)

    def _build_table_response(self, title, headers, rows, total_label):
        table_text = self._format_table_text(headers, rows)
        return f"""
<div style="max-width:100%; overflow-x:auto;">
    <pre style="margin:0; padding:12px 14px; border:1px solid #d1d5db; border-radius:6px; background:#ffffff; color:#374151; font-size:13px; line-height:1.6; font-family:Consolas, 'Courier New', monospace; white-space:pre-wrap;">{escape(title.upper())}
{escape(table_text)}

{escape(total_label)}: {len(rows)}</pre>
</div>
""".strip()

    def _build_text_response(self, title, lines):
        items = "".join(f"<li>{escape(str(line))}</li>" for line in lines)
        return f"""
<div>
    <div style="font-weight:600; margin-bottom:10px;">{escape(title)}</div>
    <ul style="margin:0; padding-left:18px;">
        {items}
    </ul>
</div>
""".strip()

    def _post_ai_response(self, response):
        if isinstance(response, str) and not response.lstrip().startswith("<"):
            response = f"<div>{escape(response)}</div>"
        self.with_context(ai_response=True).message_post(
            body=Markup(response),
            message_type="comment",
        )

    def message_post(self, **kwargs):
        body = kwargs.get("body", "")

        if self._context.get("ai_response"):
            return super().message_post(**kwargs)

        result = super().message_post(**kwargs)

        if body and body.strip():
            body_lower = body.lower()
            _logger.info("AI: Received: %s", body)

            try:
                if "student" in body_lower and "list" in body_lower:
                    _logger.info("AI: Fetching students")
                    try:
                        students = self.env["student.student"].sudo().search([])
                        _logger.info("AI: Found %s students", len(students))

                        if students:
                            response = self._build_table_response(
                                "Student List",
                                ["Name", "Student Code", "Year", "Department", "Email", "Phone"],
                                [
                                    [
                                        student.name,
                                        student.student_id,
                                        student.year,
                                        student.class_name,
                                        student.email,
                                        student.phone,
                                    ]
                                    for student in students
                                ],
                                "Total Students",
                            )
                        else:
                            response = "No students found in the database."
                    except Exception as e:
                        _logger.error("Student error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "exam" in body_lower or "result" in body_lower or "marks" in body_lower:
                    _logger.info("AI: Fetching exams")
                    try:
                        exams = self.env["student.exam"].sudo().search([])
                        _logger.info("AI: Found %s exams", len(exams))

                        if exams:
                            response = self._build_table_response(
                                "Exam Results",
                                ["Student", "Class", "Subject", "Marks", "Total", "Result", "Grade"],
                                [
                                    [
                                        exam.student_id.name if exam.student_id else "N/A",
                                        exam.student_class,
                                        exam.subject,
                                        exam.marks or 0,
                                        exam.total_marks or 100,
                                        exam.result,
                                        exam.grade,
                                    ]
                                    for exam in exams
                                ],
                                "Total Exams",
                            )
                        else:
                            response = "No exam results found in the database."
                    except Exception as e:
                        _logger.error("Exam error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "attendance" in body_lower or "attend" in body_lower:
                    _logger.info("AI: Fetching attendance")
                    try:
                        attendance_records = self.env["student.attendance"].sudo().search([])
                        _logger.info("AI: Found %s records", len(attendance_records))

                        if attendance_records:
                            response = self._build_table_response(
                                "Attendance Records",
                                ["Student", "Date", "Check In", "Check Out", "Status", "Department"],
                                [
                                    [
                                        attendance.student_id.name if attendance.student_id else "N/A",
                                        attendance.date,
                                        attendance.check_in,
                                        attendance.check_out,
                                        (attendance.status or "N/A").upper(),
                                        attendance.student_class,
                                    ]
                                    for attendance in attendance_records
                                ],
                                "Total Attendance",
                            )
                        else:
                            response = "No attendance records found in the database."
                    except Exception as e:
                        _logger.error("Attendance error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "leave" in body_lower or "holiday" in body_lower:
                    _logger.info("AI: Fetching leaves")
                    try:
                        leaves = self.env["student.leave"].sudo().search([])
                        _logger.info("AI: Found %s leaves", len(leaves))

                        if leaves:
                            response = self._build_table_response(
                                "Leave Records",
                                ["Student", "From Date", "To Date", "Days", "Reason", "Status"],
                                [
                                    [
                                        leave.student_id.name if leave.student_id else "N/A",
                                        leave.leave_from,
                                        leave.leave_to,
                                        leave.no_of_days or 0,
                                        leave.leave_reason,
                                        (leave.state or "N/A").upper(),
                                    ]
                                    for leave in leaves
                                ],
                                "Total Leaves",
                            )
                        else:
                            response = "No leave records found in the database."
                    except Exception as e:
                        _logger.error("Leave error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "subject" in body_lower:
                    _logger.info("AI: Fetching subjects")
                    try:
                        subjects = self.env["student.subject"].sudo().search([])
                        _logger.info("AI: Found %s subjects", len(subjects))

                        if subjects:
                            response = self._build_table_response(
                                "Subject List",
                                ["Name", "Code", "Description"],
                                [[subject.name, subject.code, subject.description] for subject in subjects],
                                "Total Subjects",
                            )
                        else:
                            response = "No subjects found in the database."
                    except Exception as e:
                        _logger.error("Subject error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "skill" in body_lower:
                    _logger.info("AI: Fetching skills")
                    try:
                        skills = self.env["student.skill"].sudo().search([])
                        _logger.info("AI: Found %s skills", len(skills))

                        if skills:
                            response = self._build_table_response(
                                "Skill List",
                                ["Name", "Description"],
                                [[skill.name, skill.description] for skill in skills],
                                "Total Skills",
                            )
                        else:
                            response = "No skills found in the database."
                    except Exception as e:
                        _logger.error("Skill error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "exam type" in body_lower:
                    _logger.info("AI: Fetching exam types")
                    try:
                        exam_types = self.env["student.exam_type"].sudo().search([])
                        _logger.info("AI: Found %s exam types", len(exam_types))

                        if exam_types:
                            response = self._build_table_response(
                                "Exam Type List",
                                ["Name", "Exam Date", "Description"],
                                [
                                    [exam_type.name, exam_type.exam_date, exam_type.description]
                                    for exam_type in exam_types
                                ],
                                "Total Exam Types",
                            )
                        else:
                            response = "No exam types found in the database."
                    except Exception as e:
                        _logger.error("Exam type error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "dashboard" in body_lower or "statistics" in body_lower:
                    _logger.info("AI: Fetching dashboard")
                    try:
                        total_students = self.env["student.student"].sudo().search_count([])
                        total_exams = self.env["student.exam"].sudo().search_count([])
                        total_attendance = self.env["student.attendance"].sudo().search_count([])
                        total_leaves = self.env["student.leave"].sudo().search_count([])
                        total_subjects = self.env["student.subject"].sudo().search_count([])

                        response = self._build_table_response(
                            "Dashboard",
                            ["Category", "Count"],
                            [
                                ["Total Students", total_students],
                                ["Total Subjects", total_subjects],
                                ["Total Exams", total_exams],
                                ["Total Attendance", total_attendance],
                                ["Total Leaves", total_leaves],
                            ],
                            "Total Metrics",
                        )
                    except Exception as e:
                        _logger.error("Dashboard error: %s", str(e))
                        response = f"Error: {str(e)}"

                    self._post_ai_response(response)

                elif "hi" in body_lower or "hello" in body_lower or "hey" in body_lower:
                    _logger.info("AI: Sending greeting")
                    response = self._build_text_response(
                        "Welcome",
                        [
                            "Hello! I can help you with:",
                            "student list",
                            "exam / result / marks",
                            "attendance",
                            "leave / holiday",
                            "subject",
                            "skill",
                            "exam type",
                            "dashboard",
                            "Just type your command!",
                        ],
                    )
                    self._post_ai_response(response)

                else:
                    _logger.info("AI: Unknown: %s", body)
                    response = self._build_text_response(
                        "Command Not Recognized",
                        [
                            f"I didn't understand: {body}",
                            "Available commands:",
                            "student list",
                            "exam / result",
                            "attendance",
                            "leave",
                            "subject",
                            "skill",
                            "exam type",
                            "dashboard",
                        ],
                    )
                    self._post_ai_response(response)

            except Exception as e:
                _logger.error("AI Error: %s", str(e))
                import traceback

                _logger.error(traceback.format_exc())
                self._post_ai_response(f"System Error: {str(e)}")

        return result
