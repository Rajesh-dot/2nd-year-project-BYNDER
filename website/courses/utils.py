from ..models import Course
from flask_login import current_user


def get_attendance():
    student = current_user.student[0]
    courses_list = []
    courses_ids = student.courses
    for course_id in courses_ids:
        courses_list.append(Course.query.get(course_id.course_id))
    attendance_percentages = {}
    for course in courses_list:
        count = 0
        present = 0
        for lecture in course.lecture:
            count+=1
            for day in lecture.attendance:
                if day.student_id == student.id and day.present_status:
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