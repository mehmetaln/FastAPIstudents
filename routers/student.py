from fastapi import APIRouter, HTTPException, status
from watchfiles import awatch

from database import *
from schemas import *
from functions import *

router = APIRouter(
    prefix="/school",
    tags=["schoollist"]
)

@router.on_event("startup")
async def startup_event():
    await create_tables()

@router.post("/classes/class_create/", summary="create class", status_code=status.HTTP_201_CREATED)
async def create_class(classes:ClassCreate):
    return await insert_class(
    name = classes.name
)

@router.post("/students/student_create/", summary="student create", status_code=status.HTTP_201_CREATED)
async def create_student(student:StudentCreate):
    return await insert_student(
        first_name=student.first_name,
        last_name=student.last_name,
        class_name=student.class_name,
        another_data=student.another_data
    )

@router.post("/courses/course_create/", summary="course create", status_code=status.HTTP_201_CREATED)
async def create_course(course:CourseCreate):
    return await insert_course(
    name = course.name
    )
@router.post("/grades/grade_create/", summary="grade course",status_code=status.HTTP_201_CREATED)
async def create_grade(grade:GradeAdd):
    return await insert_grades(
        course_name=grade.course_name,
        student_id=grade.student_id,
        grade=grade.grade
    )

@router.get("/students/", summary="Students list", status_code=status.HTTP_200_OK)
async def student_list():
    return await get_students()

@router.get("/classes/", summary="get class", status_code=status.HTTP_200_OK)
async def class_list():
    return await get_class()


@router.get("/courses/", summary="get courses", status_code=status.HTTP_200_OK)
async def course_list():
    return await get_course()

@router.get("/grades/", summary="get grades list", status_code=status.HTTP_200_OK)
async def grade_list():
    return await get_grades()

@router.get("/total/", summary="get total list", status_code=status.HTTP_200_OK)
async def total_list():
    return await get_total()

@router.put("/students/{student_id}/update_student/", summary="update student", status_code=status.HTTP_204_NO_CONTENT)
async def student_update(student_id:int,student:StudentUpdate):
    return await update_student(
        student_id=student_id,
        first_name = student.first_name,
        last_name = student.last_name,
        class_name=student.class_name,
        another_data=student.another_data
    )

@router.put("/classes/{class_id}/update_class/", summary="update class name", status_code=status.HTTP_204_NO_CONTENT)
async def class_update(class_id:int, class_update:ClassUpdate):
    return await update_class(
        id=class_id,
        name=class_update.name
    )

@router.put("/courses/{course_id}/update_course/", summary="update course name", status_code=status.HTTP_204_NO_CONTENT)
async def course_update(course_id:int, course:CourseUpdate):
    return await update_course(
        id=course_id,
        name=course.name
    )

@router.put("/grades/{grade_id}/update_grade",summary="update grade", status_code=status.HTTP_204_NO_CONTENT)
async def grade_update(grade_id:int, grade:GradeUpdate):
    return await update_grade(
        id=grade_id,
        course_name=grade.course_name,
        student_id=grade.student_id,
        grade=grade.grade
    )

@router.delete("/students/{student_id}/delete_student/", summary="delete student", status_code=status.HTTP_204_NO_CONTENT)
async def student_delete_api(student_id:int):
    return await delete_student(student_id=student_id)

@router.delete("/classes/{class_id}/delete_class/", summary="delete class", status_code=status.HTTP_204_NO_CONTENT)
async def class_delete_api(class_id:int):
    return await delete_class(class_id=class_id)

@router.delete("/courses/{course_id}/delete_course/", summary="delete course", status_code=status.HTTP_204_NO_CONTENT)
async def course_delete_api(course_id:int):
    return await delete_course(course_id=course_id)

@router.delete("/grades/{grade_id}/delete_grade/", summary="delete grade", status_code=status.HTTP_204_NO_CONTENT)
async def grade_delete_api(grade_id:int):
    return await delete_grade(grade_id=grade_id)

#Not ortalaması
@router.get("/students/{student_id}/average/", summary="student average", status_code=status.HTTP_200_OK)
async def student_average_api(student_id:int):
    return await average_student(
        student_id=student_id
    )

# # Belli sınıftaki ögrencileri getirme
@router.get("/classes/{class_name/", summary="same class list", status_code=status.HTTP_200_OK)
async def get_same_class_api(class_name:str):
    return await get_same_class(
        class_name=class_name
    )

# # SINIF MEVCUDUNU GETİREN LİSTE
@router.get("/classes/{class_name/length_class/", summary="class lenght", status_code=status.HTTP_200_OK)
async def get_length_class_api(class_name:str):
    return await get_length_class(
        class_name=class_name
    )

# Belli bir sınıftaki ögrencilerin aldığı derslerin listesi
@router.get("/classes/{class_name}/courses/", summary="Courses taken by students in the same class", status_code=status.HTTP_200_OK)
async def same_class_course_api(class_name:str):
    return await same_class_courses(
        class_name=class_name
    )

# aynı dersi alan ögrencilerin listesi
@router.get("courses/{course_name}/", summary="same courses student list", status_code=status.HTTP_200_OK)
async def get_same_course_api(course_name:str):
    return await get_same_courses(
        course_name=course_name
    )

# Öğrencinin aldığı tüm derslerin isimlerini getirme
@router.get("/students/{student_id}/courses/", summary=" get student course list", status_code=status.HTTP_200_OK)
async def get_student_course_list_api(student_id:int):
    return await get_student_course_list(
        student_id=student_id
    )

#Herhangi bir dersten En Yüksek Notu Alan Öğrenci ve Notunu Getirme
@router.get("/courses/{course_name}/top-student/", summary="top student", status_code=status.HTTP_200_OK)
async def get_top_student_api(course_name:str):
    return await get_top_student(course_name=course_name)

#Herhangi bir dersten En düşük Notu Alan Öğrenci ve Notunu Getirme
@router.get("/courses/{course_name}/low-student/", summary="low student", status_code=status.HTTP_200_OK)
async def get_low_student_api(course_name:str):
    return await get_lowe_student(course_name=course_name)

# Bir Öğrencinin Belli Bir Dersteki Notlarını Getirme
@router.get("/courses/{course_name}/{student_id}/grades/", summary="ögrencinin belli bir dersteki aldığı notlar", status_code=status.HTTP_200_OK)
async def get_student_course_grades_api(course_name:str, student_id):
    return await get_student_course_grades(course_name=course_name, student_id=student_id)

# Belli bir dersin geçme yüzdesi
@router.get("/courses/{course_name}/passed-rate/", summary="Belli bir dersin geçme yüzdesi", status_code=status.HTTP_200_OK)
async def get_pass_rate(course_name:str, gecme_notu:int = 50):
    return await get_passed_count(course_name=course_name, gecme_not=gecme_notu)