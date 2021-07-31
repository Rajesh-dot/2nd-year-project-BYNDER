from ..models import Group, Student_ids

def validate_user(user,group):
    if user.user_type=='p':
        teacher=user.teacher[0]
        if teacher.id==group.teacher_id:
            return True
        else:
            return False
    else:
        '''
        student_ids = group.student_ids
        for i in student_ids:
            if i.stude
        '''
        pass
