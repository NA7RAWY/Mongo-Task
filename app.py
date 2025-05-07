from flask import Flask, render_template, request, redirect
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from bson import ObjectId 

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client['School']
students = db['students']
courses = db['courses']


if students.count_documents({}) == 0:
    students.insert_many([
    {"name": "Mahmoud", "age": 20, "grades": [90, 80, 85], "address": {"city": "Cairo", "zip": "12345"}, "active": True},
    {"name": "Mostafa", "age": 21, "grades": [70, 75, 80], "address": {"city": "Alexandria", "zip": "54321"}, "active": False},
    {"name": "Ahmed", "age": 22, "grades": [88, 92, 85], "address": {"city": "Giza", "zip": "67890"}, "active": True},
    {"name": "Ibrahim", "age": 23, "grades": [95, 87, 85], "address": {"city": "Fayium", "zip": "58746"}, "active": False}
])

initial_courses = [
    {"course_name": "MIS", "students_enrolled": ["Mahmoud", "Mostafa"], "active": True},
    {"course_name": "CS", "students_enrolled": ["Ibrahim", "Mahmoud"], "active": True},
    {"course_name": "NS", "students_enrolled": ["Mostafa","Ahmed"], "active": False}
]

for course in initial_courses:
    if not courses.find_one({"course_name": course["course_name"]}):
        courses.insert_one(course)

def populate_students_id():
    all_courses = courses.find()
    for course in all_courses:
        enrolled_names = course.get("students_enrolled", [])
        student_ids = []

        for name in enrolled_names:
            student = students.find_one({"name": name})
            if student:
                student_ids.append(student["_id"])

        courses.update_one(
            {"_id": course["_id"]},
            {"$set": {"students_id": student_ids}}
        )
populate_students_id()


students.create_indexes([
    IndexModel([("name", ASCENDING)]),  
    IndexModel([("age", ASCENDING), ("name", DESCENDING)]),  
])

courses.create_index([("course_name", ASCENDING)], unique=True)  

@app.route('/')
def index():
    all_students = list(students.find())
    all_courses = list(courses.find())   
    return render_template('index.html', students=all_students, courses=all_courses)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        grades = list(map(int, request.form['grades'].split(',')))
        address = {
            "city": request.form['city'],
            "zip": request.form['zip']
        }
        active = True if 'active' in request.form else False

        students.insert_one({
            "name": name,
            "age": age,
            "grades": grades,
            "address": address,
            "active": active,
            "courses": []
        })
        return redirect('/')

    return render_template('add_student.html')

@app.route('/update_student/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = students.find_one({"_id": ObjectId(student_id)})
    if request.method == 'POST':
        new_name = request.form['name']
        new_age = int(request.form['age'])
        new_grades = list(map(int, request.form['grades'].split(',')))

        
        students.update_one(
            {"_id": student["_id"]},
            {"$set": { #set عشان منقعدش ندور
                "name": new_name,
                "age": new_age,
                "grades": new_grades
            }}
        )
        return redirect('/')

    return render_template('update_student.html', student=student)

@app.route('/edit_course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = courses.find_one({"_id": ObjectId(course_id)})
    all_students = list(students.find())

    if request.method == 'POST':
        new_name = request.form['course_name']
        new_students = request.form.getlist('students_enrolled')
        new_active = 'active' in request.form

        courses.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": {
                "course_name": new_name,
                "students_enrolled": new_students,
                "active": new_active
            }}
        )

        students.update_many(
            {"courses": str(course_id)},
            {"$pull": {"courses": str(course_id)}}
        )

        for student_name in new_students:
            students.update_one(
                {"name": student_name},
                {"$addToSet": {"courses": str(course_id)}}
            )

        populate_students_id()

        return redirect('/')

    return render_template('edit_course.html', course=course, students=all_students)


@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    student = students.find_one({"_id": ObjectId(student_id)})

    if student:
        students.delete_one({"_id": ObjectId(student_id)})

        for course_id in student.get('courses', []):
            courses.update_one(
                {"_id": ObjectId(course_id)},
                {"$pull": {"students_enrolled": student['name']}}
            )
            print(f"Removed student {student['name']} from course {course_id}")

    return redirect('/')

@app.route('/delete_course/<course_id>', methods=['POST'])
def delete_course(course_id):
    course = courses.find_one({"_id": ObjectId(course_id)})

    if course:
        courses.delete_one({"_id": ObjectId(course_id)})

        students.update_many(
            {"courses": ObjectId(course_id)},
            {"$pull": {"courses": ObjectId(course_id)}}
        )
        students.update_many(
            {},
            {"$pull": {"students_enrolled": course['course_name']}}
        )

        print(f"Removed course {course['course_name']} from all students")

    return redirect('/')

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        students_enrolled = request.form.getlist('students_enrolled')
        active = True if 'active' in request.form else False

       
        existing_course = courses.find_one({"course_name": course_name})
        if not existing_course:
            
            course_id = courses.insert_one({
                "course_name": course_name,
                "students_enrolled": students_enrolled,
                "active": active
            }).inserted_id

            for student_name in students_enrolled:
                students.update_one(
                    {"name": student_name},
                    {"$push": {"courses": str(course_id)}} #push عشان مندورش بردو
                )
        else:
          
            print(f"Course {course_name} already exists.")

        return redirect('/')

  
    all_students = students.find()
    return render_template('add_course.html', students=all_students)


@app.route('/custom_query', methods=['GET', 'POST'])
def custom_query():
    results = []
    error = None
    if request.method == 'POST':

        field1 = request.form.get('field1')
        value1 = request.form.get('value1')
        operator = request.form.get('operator')

        if not field1 or not value1:
            return render_template('custom_query.html', results=[], error="Please provide both field and value.")

        try:
            value1 = int(value1)
        except ValueError:
            if isinstance(value1, str):
                if value1.lower() == "true":
                    value1 = True
                elif value1.lower() == "false":
                    value1 = False

        query = {}

        if operator in ['or', 'and', 'nor']:
            field2 = request.form.get('field2')
            value2 = request.form.get('value2')

            if not field2 or not value2:
                return render_template('custom_query.html', results=[], error="Please provide both field2 and value2 for logical operators.")

            try:
                value2 = int(value2)
            except ValueError:
                if isinstance(value2, str):
                    if value2.lower() == "true":
                        value2 = True
                    elif value2.lower() == "false":
                        value2 = False

            if operator == 'or':
                query = {"$or": [{field1: value1}, {field2: value2}]}
            elif operator == 'and':
                query = {"$and": [{field1: value1}, {field2: value2}]}
            elif operator == 'nor':
                query = {"$nor": [{field1: value1}, {field2: value2}]}

        elif operator in ['in', 'all']:
            if isinstance(value1, str):
                items = [item.strip() for item in value1.split(',')]
                def convert(v):
                    try:
                        return int(v)
                    except ValueError:
                        return v
                value1 = [convert(item) for item in items]
            query = {field1: {f"${operator}": value1}}

        elif operator == 'size':
            try:
                value1 = int(value1)
            except ValueError:
                return render_template('custom_query.html', results=[], error="Please provide a valid integer for the size operator.")
            query = {field1: {"$size": value1}}

        elif operator == 'expr':
            comparison_operator = request.form.get('comparison_operator')
            if not comparison_operator:
                return render_template('custom_query.html', results=[], error="Please select a comparison operator.")
            query = {"$expr": {f"${comparison_operator}": [f"${field1}", value1]}}

        else:
            query = {field1: value1}

        results = list(students.find(query))

    return render_template('custom_query.html', results=results, error=error)


@app.route('/calculate_grades')
def calculate_grades():
    for student in students.find():
        grades = student.get('grades', [])
        if isinstance(grades, list):
            total_grade = sum(grades)
        else:
            total_grade = 0
        students.update_one(
            {"_id": student["_id"]},
            {"$set": {"totalGrade": total_grade}}
        )
        print(f"Updated {student['name']} with total grade: {total_grade}")
    return redirect('/')




@app.route('/delete_dynamic', methods=['GET', 'POST'])
def delete_dynamic():
    message = None
    if request.method == 'POST':
        collection_name = request.form['collection']
        field = request.form['field']
        value = request.form['value']
        delete_type = request.form.get('delete_type', 'one')

        try:
            value = int(value)
        except ValueError:
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False

        collection = students if collection_name == 'students' else courses

        if delete_type == 'one':
            document = collection.find_one({field: value})
            if not document:
                message = f"No document found in {collection_name} with {field} = {value}"
            else:
                if collection_name == 'students':
                    student_id = document['_id']
                    student_name = document.get('name')

                    courses.update_many(
                        {"students_enrolled": student_name},
                        {"$pull": {"students_enrolled": student_name}}
                    )
                    courses.update_many(
                        {"students_id": student_id},
                        {"$pull": {"students_id": student_id}}
                    )

                elif collection_name == 'courses':
                    course_id = document['_id']

                    students.update_many(
                        {"courses": course_id},
                        {"$pull": {"courses": course_id}}
                    )

                collection.delete_one({field: value})
                message = f"Deleted one document from {collection_name} where {field} = {value}"

        elif delete_type == 'many':
            documents = list(collection.find({field: value}))
            if not documents:
                message = f"No documents found in {collection_name} with {field} = {value}"
            else:
                count = 0
                for doc in documents:
                    if collection_name == 'students':
                        student_id = doc['_id']
                        student_name = doc.get('name')

                        courses.update_many(
                            {"students_enrolled": student_name},
                            {"$pull": {"students_enrolled": student_name}}
                        )
                        courses.update_many(
                            {"students_id": student_id},
                            {"$pull": {"students_id": student_id}}
                        )

                    elif collection_name == 'courses':
                        course_id = doc['_id']

                        students.update_many(
                            {"courses": course_id},
                            {"$pull": {"courses": course_id}}
                        )

                result = collection.delete_many({field: value})
                message = f"Deleted {result.deleted_count} documents from {collection_name} where {field} = {value}"

    return render_template('delete_dynamic.html', message=message)

@app.route('/show_indexes')
def show_indexes():
    student_indexes = list(students.list_indexes())
    course_indexes = list(courses.list_indexes())
    return render_template('show_indexes.html', student_indexes=student_indexes, course_indexes=course_indexes)


if __name__ == '__main__':
    app.run(debug=True)
