from pydantic import BaseModel, Field
from typing import Optional,Dict


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    class_name: str
    another_data: Optional[Dict] = None

class StudentUpdate(BaseModel):
    first_name: str
    last_name: str
    class_name: str
    another_data: Optional[Dict] = None

class StudentResponse(BaseModel):
    id:int
    first_name: str
    last_name: str
    class_name: str
    another_data: Optional[Dict] = None


class GradeAdd(BaseModel):
    course_name :str
    student_id : int
    grade:float = Field(gt =0 ,lt =100)

class CourseCreate(BaseModel):
    name : str = Field(min_length=2)

class ClassCreate(BaseModel):
    name : str = Field(min_length=2)

class ClassUpdate(BaseModel):
    name:str
class CourseUpdate(BaseModel):
    name:str

class GradeUpdate(BaseModel):
    course_name:str
    student_id :int
    grade: float = Field(gt=0, lt=100)


class Total(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    course_name: str
    class_name: str
    grade: float
