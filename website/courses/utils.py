from ..models import Course
from flask_login import current_user


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


def validate_course(course_name):
    course = Course.query.filter_by(course_name=course_name).first()
    if course:
        if current_user.user_type == 'p':
            teacher = current_user.teacher[0]
            courses = teacher.courses
            if course in courses:
                return True
            else:
                return False
        else:
            student = current_user.student[0]
            courses_ids = student.courses
            for i in courses_ids:
                temp_course = Course.query.get(i.course_id)
                if course.id == temp_course.id:
                    return True
            return False

    else:
        return False


ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
