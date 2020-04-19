from app import app, db
from app.models import User, Course, Task, Student, Submission, Feedback

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 
    'User': User, 
    'Course': Course, 
    'Task': Task, 
    'Student':Student,
    'Submission':Submission,
    'Feedback':Feedback}

if __name__=='__main__':
    app.run()