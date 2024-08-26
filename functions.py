import json
from math import ceil
from tabnanny import check

from database import get_database, close_connection
from fastapi import HTTPException, status, APIRouter
from schemas import *
from cemirutils import CemirUtils

class Dict2Dot(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' objesinde '{key}' anahtarı bulunamadı.")

def fetchone__dict2dot(cursor, sql):
    cursor.execute(sql)
    sql_result = cursor.fetchone()
    if sql_result:
        return Dict2Dot(sql_result)
    else:
        return None

def fetchall__dict2dot(cursor, sql):
    cursor.execute(sql)
    sql_result = cursor.fetchall()
    result_list = []
    if sql_result:
        for result in sql_result:
            new_result = Dict2Dot(result)
            result_list.append(new_result)
        return result_list
    else:
        return result_list

async def create_tables():
    conn , cursor= get_database()
    if conn is None:
        print("Database connection failed")
        return
    try:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes(
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses(
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id SERIAL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                class_name TEXT REFERENCES classes(name) ON DELETE CASCADE,
                another_data JSONB
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades(
                id SERIAL PRIMARY KEY,
                course_name TEXT REFERENCES courses(name) ON DELETE CASCADE,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                grade NUMERIC
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS total(
                first_name TEXT,
                last_name TEXT,
                course_name TEXT,
                class_name TEXT,
                grade NUMERIC
            );
        """)
        # print("Total table created")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {str(e)}")
    finally:
        close_connection(cursor, conn)

async def insert_student(first_name, last_name, class_name, another_data):
    conn, cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute(""" INSERT INTO students (first_name, last_name, class_name, another_data) VALUES (%s,%s,%s,%s) RETURNING id;
        """, (first_name,last_name, class_name, json.dumps(another_data)))
        conn.commit()
        student_id = cursor.fetchone()[0]
        close_connection(cursor,conn)
        return {"student_id":student_id, "first_name":first_name, "last_name":last_name, "class_name":class_name, "another_data":another_data}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def insert_class(name):
    conn, cursor= get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO classes (name) VALUES (%s) RETURNING id; """, (name,))
        conn.commit()
        class_id = cursor.fetchone()[0]
        close_connection(cursor,conn)
        return {"class_id":class_id, "name":name}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def insert_course(name):
    conn, cursor= get_database()
    try:
        cursor.execute('''INSERT INTO courses (name) VALUES (%s) RETURNING id;''', (name,))
        print("oluştu")
        conn.commit()
        print("gönderildi")
        course_id = cursor.fetchone()[0]
        print("id verildi")
        close_connection(cursor,conn)
        print("kapatlıldı")
        print(course_id)
        return {"course_id":course_id, "name":name}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def insert_grades(course_name,student_id, grade):
    conn,cursor = get_database()
    try:
        cursor.execute('''INSERT INTO grades (course_name, student_id, grade) VALUES (%s,%s,%s) RETURNING id;''', (course_name, student_id, grade))
        conn.commit()
        grade_id = cursor.fetchone()[0]
        close_connection(cursor,conn)
        return {"grade_id":grade_id, "course_name":course_name, "student_id":student_id, "grade":grade}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def get_students():
    conn, cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor, 'SELECT * FROM students')
        close_connection(cursor,conn)
        return check_data

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

async def get_class():
    conn, cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes")
        result = cursor.fetchall()
        close_connection(cursor,conn)
        return result

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

async def get_course():
    conn,cursor= get_database()
    try:
        check_data = fetchall__dict2dot(cursor,'SELECT * FROM courses')
        close_connection(cursor,conn)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def get_grades():
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor,'SELECT * FROM grades')
        close_connection(cursor,conn)
        print(check_data)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

async def get_total():
    conn, cursor= get_database()
    try:
        check_data = fetchall__dict2dot(cursor,'''SELECT students.first_name,
                        students.last_name,
                        courses.name as course_name,
                        classes.name as class_name,
                        grades.grade FROM grades
                        JOIN
                            students ON grades.student_id = students.id
                        JOIN
                            courses ON grades.course_name = courses.name
                        JOIN
                            classes ON students.class_name = classes.name;''')
        insert_query = "INSERT INTO total (first_name, last_name, course_name, class_name, grade) VALUES (%s, %s, %s, %s, %s)"
        cursor.executemany(insert_query, [(d.first_name, d.last_name, d.course_name, d.class_name, d.grade) for d in check_data])
        conn.commit()
        close_connection(cursor,conn)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"bir hata oluştu:{str(e)}")
#
async def update_student(first_name, last_name, class_name,another_data,student_id):
    conn, cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET first_name=%s, last_name = %s, class_name=%s, another_data = %s WHERE id=%s", (first_name,last_name,class_name,json.dumps(another_data),student_id))
        conn.commit()
        close_connection(cursor,conn)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

async def update_class(name,id):
    conn, cursor= get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE classes SET name =%s WHERE id=%s",(name,id))
        conn.commit()
        close_connection(cursor,conn)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def update_course(name,id):
    conn, cursor= get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE courses SET name =%s WHERE id=%s",(name,id))
        conn.commit()
        close_connection(cursor,conn)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def update_grade(course_name, student_id, grade,id):
    conn, cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE grades SET course_name =%s, student_id =%s, grade=%s WHERE id =%s", (course_name,student_id,grade,id))
        conn.commit()
        close_connection(cursor,conn)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def delete_student(student_id):
    conn, cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
        conn.commit()
        close_connection(cursor,conn)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def delete_class(class_id):
    conn,cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classes WHERE id=%s", (class_id,))
        conn.commit()
        close_connection(cursor, conn)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def delete_course(course_id):
    conn,cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id=%s", (course_id,))
        conn.commit()
        close_connection(cursor, conn)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
async def delete_grade(grade_id):
    conn,cursor = get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grades WHERE id=%s", (grade_id,))
        conn.commit()
        close_connection(cursor, conn)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
#
#Ögrenci genel  ortalaması
async def average_student(student_id):
    conn, cursor = get_database()
    try:
        print("deneme")
        check_data = fetchone__dict2dot(cursor, f'''SELECT avg(grade) FROM grades WHERE student_id='{student_id}'; ''')
        close_connection(cursor, conn)
        return round(ceil(check_data["avg"]),2)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

# # Belli sınıftaki ögrencileri getirme

async def get_same_class(class_name):
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor, f'''SELECT first_name, last_name, class_name FROM students WHERE class_name ='{class_name}'; ''')
        student_count = len(check_data)
        if not check_data:
            raise HTTPException(status_code=404, detail="class_name not found")
        close_connection(cursor, conn)
        return {"Students": check_data}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
# # SINIF MEVCUDUNU GETİREN LİSTE
async def get_length_class(class_name):
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor,f'''SELECT * FROM students WHERE class_name='{class_name}'; ''')
        if not check_data:
            raise HTTPException(status_code=404, detail="class_name not found")
        close_connection(cursor, conn)
        return len(check_data)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

# Belli bir sınıftaki ögrencilerin aldığı derslerin listesi
async def same_class_courses(class_name):
    conn,cursor = get_database()

    try:
        check_data = fetchall__dict2dot(cursor,f''' SELECT DISTINCT ON (course_name) course_name  FROM total WHERE class_name='{class_name}' ;''')
        print(check_data)
        if not check_data:
            raise HTTPException(status_code=404, detail="class_name not found")
        close_connection(cursor, conn)
        return check_data

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

# aynı dersi alan ögrencilerin listesi
async def get_same_courses(course_name):
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor, f"SELECT first_name, last_name, grade FROM total WHERE course_name ='{course_name}'; ")
        print(check_data)
        if not check_data:
            raise HTTPException(status_code=404, detail="Not found items")
        close_connection(cursor,conn)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")


# Öğrencinin aldığı tüm derslerin isimlerini getirme
async def get_student_course_list(student_id):
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor, f"SELECT course_name FROM grades WHERE student_id='{student_id}'; ")
        if not check_data:
            raise HTTPException(status_code=404, detail="Not found student")
        close_connection(cursor,conn)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

#Herhangi bir dersten En Yüksek Notu Alan Öğrenci ve Notunu Getirme
async def get_top_student(course_name):
    conn,cursor =get_database()
    try:
        check_data = fetchone__dict2dot(cursor, f'''SELECT first_name, last_name, grade FROM total WHERE course_name = '{course_name}' 
        ORDER BY grade DESC LIMIT 1; ''')
        if not check_data:
            raise HTTPException(status_code=404, detail="Not found student")
        close_connection(cursor,conn)
        return check_data
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

#Herhangi bir dersten En düşük Notu Alan Öğrenci ve Notunu Getirme
async def get_lowe_student(course_name):
    conn,cursor = get_database()
    try:
        check_data = fetchone__dict2dot(cursor, f'''SELECT first_name, last_name, grade FROM total WHERE course_name = '{course_name}' 
        ORDER BY grade ASC LIMIT 1 ''')
        if not check_data:
            raise HTTPException(status_code=404, detail="Not found student")
        close_connection(cursor, conn)
        return check_data


    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

# Bir Öğrencinin Belli Bir Dersteki Notlarını Getirme
async def get_student_course_grades(course_name, student_id):
    conn,cursor = get_database()
    try:
        check_data = fetchall__dict2dot(cursor, f'''SELECT grade FROM grades WHERE course_name = '{course_name}' AND  student_id ='{student_id}' ;''')
        if not check_data:
            raise HTTPException(status_code=404, detail="Not found student")
        close_connection(cursor, conn)
        return {"Not-1":check_data[0], "Not-2":check_data[1]}


    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")

# Bir Dersin Geçme Oranını Hesaplama
async def get_passed_count(course_name,gecme_not=50.0):
    conn, cursor = get_database()
    try:
        passed_count_student = fetchone__dict2dot(cursor, f'''SELECT COUNT (*) as passed_count_student FROM grades WHERE course_name = '{course_name}' AND grade >= {gecme_not}; ''')
        print(passed_count_student)
        total_count_student = fetchone__dict2dot(cursor, f'''SELECT COUNT (*) as total_count_student FROM grades WHERE course_name = '{course_name}'; ''')
        print(total_count_student)
        if total_count_student.total_count_student >0:
            gecme_yuzdesi = (passed_count_student.passed_count_student/total_count_student.total_count_student) * 100
        else:
            gecme_yuzdesi = 0.0
        close_connection(cursor,conn)
        return {"course_name":course_name, "gecme yüzdesi":gecme_yuzdesi}


    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Not found items {str(e)}")
