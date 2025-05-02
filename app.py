from flask import Flask, render_template, request, redirect
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from bson import ObjectId  # To handle ObjectId correctly

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['School']
students = db['students']
courses = db['courses']

# Create some collections and insert documents with various field types
if students.count_documents({}) == 0:
    students.insert_many([
    {"name": "Alice", "age": 20, "grades": [90, 80, 85], "address": {"city": "Cairo", "zip": "12345"}, "active": True},
    {"name": "Bob", "age": 22, "grades": [70, 75, 80], "address": {"city": "Alexandria", "zip": "54321"}, "active": False},
    {"name": "Charlie", "age": 23, "grades": [88, 92, 85], "address": {"city": "Giza", "zip": "67890"}, "active": True}
])

initial_courses = [
    {"course_name": "Math", "students_enrolled": ["Alice", "Bob"], "active": True},
    {"course_name": "Science", "students_enrolled": ["Charlie", "Alice"], "active": True},
    {"course_name": "History", "students_enrolled": ["Bob"], "active": False}
]

for course in initial_courses:
    if not courses.find_one({"course_name": course["course_name"]}):
        courses.insert_one(course)


# 1. Create Indexes
students.create_indexes([
    IndexModel([("name", ASCENDING)]),  # Single field index
    IndexModel([("age", ASCENDING), ("name", DESCENDING)]),  # Compound index
])

courses.create_index([("course_name", ASCENDING)], unique=True)  # Unique index on course_name

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

        # Example of using $set operator to update data
        students.update_one(
            {"_id": student["_id"]},
            {"$set": {
                "name": new_name,
                "age": new_age,
                "grades": new_grades
            }}
        )
        return redirect('/')

    return render_template('update_student.html', student=student)

@app.route('/delete_student/<student_id>', methods=['POST'])
def delete_student(student_id):
    students.delete_one({"_id": ObjectId(student_id)})
    return redirect('/')

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        students_enrolled = request.form.getlist('students_enrolled')
        active = True if 'active' in request.form else False

        # Check if the course already exists by searching with course_name
        existing_course = courses.find_one({"course_name": course_name})
        if not existing_course:
            # Insert the course data if it doesn't exist
            course_id = courses.insert_one({
                "course_name": course_name,
                "students_enrolled": students_enrolled,
                "active": active
            }).inserted_id

            # Enroll students in the course
            for student_name in students_enrolled:
                students.update_one(
                    {"name": student_name},
                    {"$push": {"courses": str(course_id)}}
                )
        else:
            # If the course already exists, handle it by either ignoring it or displaying a message
            print(f"Course {course_name} already exists.")

        return redirect('/')

    # Fetch all students for course enrollment
    all_students = students.find()
    return render_template('add_course.html', students=all_students)



# 4. Find Queries with Logical Operators
@app.route('/find_queries')
def find_queries():
    # Example using $or and $in
    query_1 = students.find({"$or": [{"age": 20}, {"age": 22}]})
    
    # Example using $in
    query_2 = students.find({"grades": {"$in": [80, 85]}})

    return render_template('find_queries.html', query_1=query_1, query_2=query_2)

# 6. Multiply All Array Elements (Sum grades and store in totalGrade)
@app.route('/update_grades')
def update_grades():
    # Loop through students and calculate totalGrade
    for student in students.find():
        total_grade = sum(student['grades'])
        students.update_one(
            {"_id": student["_id"]},
            {"$set": {"totalGrade": total_grade}}
        )
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
