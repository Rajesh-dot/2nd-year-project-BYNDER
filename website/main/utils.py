from functools import wraps
from flask_login import current_user
from flask import flash, redirect


def require_role(role):
    """make sure user has this role"""
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.user_type == role:
                print(current_user.user_type, role,
                      current_user.user_type == role)
                flash("No Permission", category="error")
                return redirect("/")
            else:
                return func(*args, **kwargs)
        return wrapped_function
    return decorator


'''
def get_attendance():
    student = current_user.student[0]
    courses_list = []
    total_courses = Course.query.all()
    for course in total_courses:
        student_ids = course.student_ids
        for j in student_ids:
            if j.student_id == student.id:
                courses_list.append(course)
    attendance_percentages = {}
    for course in courses_list:
        count = 0
        present = 0
        for day in course.attendance:
            if day.student_id == student.id:
                count += 1
                if day.present_status:
                    present += 1
        if count == 0:
            attendance_percentages[course] = 0
        else:
            attendance_percentages[course] = int((present/count)*100)
    return attendance_percentages
'''


def get_attend_info(lecture):
    attendance_list = lecture.attendance
    presentees=[]
    absentees=[]
    for attend in attendance_list:
        if attend.present_status:
            presentees.append(attend.student_id)
        else:
            absentees.append(attend.student_id)
    return {'presentees':presentees,'absentees':absentees}


