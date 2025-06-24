# 🏫 School Management System – MongoDB + Flask

A simple web-based School Management System built using **Flask**, **MongoDB**, and **Bootstrap**. The system allows managing students and courses with interactive features.

---

## 📸 Screenshots

### 🔷 Home Page
![Home](screenshots/01_screenshot.png)

### 🟩 Students Section
Displays all students with their details and options to edit or delete.

![Students](screenshots/02_screenshot.png)

### 🟦 Courses Section
Shows all courses with their active status and controls.

![Courses](screenshots/03_screenshot.png)

---

## ⚙️ Features

- ➕ Add Student & Course  
- ✏️ Edit / Delete Records  
- 🧮 Calculate Grades  
- 🔍 Run Custom Mongo Queries  
- 📁 View Indexes  
- 🗑️ Delete Specific Documents  

---

## 🧰 Tech Stack

- Python (Flask Framework)  
- MongoDB (NoSQL Database)  
- HTML / CSS / Bootstrap  
- FontAwesome Icons  

---

## 🚀 How to Run

1. Install dependencies:
   ```bash
   pip install flask pymongo
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

3. Visit:
   ```
   http://localhost:5000
   ```

---

## 📦 Folder Structure

```
Mongo-Task/
├── app.py
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   └── ...
└── requirements.txt
```

---

## 📌 Notes

- Ensure MongoDB is running locally on port `27017`.
- The database used is called `school_db`.

---

## 🧑‍💻 Author

**[Mahmoud Elnahrawy](https://github.com/NA7RAWY)**  
Built as part of a task demonstrating CRUD operations and MongoDB integration.
