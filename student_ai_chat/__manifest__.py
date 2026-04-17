# -*- coding: utf-8 -*-
{
    'name': 'Student AI Chat',
    'version': '1.0',
    'category': 'Education',
    'summary': 'AI Chatbot for Student Administration',
    'description': """
        AI Chatbot for Student Administration
        ======================================
        
        This module provides an AI-powered chatbot that can answer queries
        about student administration data including:
        
        - Student information
        - Exam results and grades
        - Attendance records
        - Leave requests
        - Subject information
        
        The chatbot uses AI to convert natural language queries into
        Odoo ORM queries and returns formatted results.
    """,
    'author': 'AI Developer',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'student_administration',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
