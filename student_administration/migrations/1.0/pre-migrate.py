# Migration script to add new fields to student module
def migrate(cr, version):
    # Add columns to student_student table
    cr.execute("""
        ALTER TABLE student_student 
        ADD COLUMN IF NOT EXISTS image bytea,
        ADD COLUMN IF NOT EXISTS skills text,
        ADD COLUMN IF NOT EXISTS course character varying,
        ADD COLUMN IF NOT EXISTS year integer
    """)
    
    # Add columns to student_leave table
    cr.execute("""
        ALTER TABLE student_leave 
        ADD COLUMN IF NOT EXISTS leave_reason character varying,
        ADD COLUMN IF NOT EXISTS no_of_days integer
    """)
