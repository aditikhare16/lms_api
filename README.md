# Mini Leave Management System (LMS)

A simple **Leave Management System** for small organizations that allows employees to apply for leaves and HR to manage them. Built using **Python, FastAPI, SQLite, and Tkinter**.

---
## **Link to demo video - https://drive.google.com/file/d/1Q-g49Is52Qyov4wK7l-HHM-St6yhge1D/view?usp=sharing **

## **Features**

### Employee Panel

* Apply for leave with start & end dates, reason.
* Check leave balance (total, used, remaining).

### HR Panel

* Add new employees with details (Name, Email, Department, Joining Date, Opening Balance).
* View all leave requests.
* Approve or reject leave requests.

### Backend / API Features

* Validate leave requests:

  * Cannot apply before joining date.
  * Cannot apply for more days than balance.
  * Overlapping leaves prevented.
  * Invalid dates rejected (end < start).
  * Only business days counted (weekends excluded).
* Leave status: Pending → Approved / Rejected.

---

## **Tech Stack**

| Layer         | Technology        | Reason / Alternative                                                |
| ------------- | ----------------- | ------------------------------------------------------------------- |
| Frontend GUI  | Tkinter           | Simple, Python-native GUI; alternative: React / Angular for web.    |
| Backend       | FastAPI           | Lightweight, fast API framework; alternative: Flask or Django REST. |
| Database      | SQLite            | Easy setup for MVP; alternative: PostgreSQL for scalability.        |
| ORM           | SQLAlchemy        | Handles database mapping easily; alternative: raw SQL queries.      |
| HTTP Requests | Requests (Python) | GUI communicates with API; alternative: Axios for web.              |

---

## **System Design & Scalability**

### **Architecture**

```
+----------------+        +----------------+        +----------------+
|   Employee /   | <----> |   Backend API  | <----> |    Database    |
|      HR GUI    |        |   FastAPI +    |        |   SQLite / ORM |
| Tkinter App    |        |   CRUD & Logic |        |   Employees &  |
|                |        |                |        |   Leaves       |
+----------------+        +----------------+        +----------------+
```

### **Database Design**

```
Employee (1) --------> (many) LeaveRequest
```

* Employee: id, name, email, department, joining\_date, opening\_balance
* LeaveRequest: id, employee\_id, start\_date, end\_date, business\_days, status, reason

### **Scalability Considerations**

* Replace **SQLite** with **PostgreSQL** for handling 500+ employees.
* Use **API pagination** to fetch leave records efficiently.
* Deploy backend with **FastAPI + Uvicorn/Gunicorn** behind **NGINX**.
* Use **ORM caching** or Redis for frequent leave balance queries.
* Implement **authentication & roles** for secure HR access.

---

## **Installation & Setup**

### **1. Clone the repository**

```bash
git clone <your-repo-url>
cd <repository-folder>
```

### **2. Create and activate a virtual environment**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

### **4. Initialize the database**

```bash
python app/database.py
```

> This will create the **employees** and **leaves** tables.

---

### **5. Run the backend API**

```bash
uvicorn app.main:app --reload
```

* Swagger UI available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test APIs.

---

### **6. Run the GUI in a separate terminal**

> Open a **new terminal** so that the backend stays running.

```bash
cd <repository-folder>
# Activate virtual environment again if needed
# Windows
.venv\Scripts\activate
# Linux / Mac
source .venv/bin/activate
python gui.py
```

* Choose **Employee** or **HR** role.
* Employees can apply leaves or check balance.
* HR can add employees, view leaves, approve/reject.

---

## **Usage Notes**

* HR API key must match `HR_KEY` in `gui.py` (default: `admin123`).
* Dates must be in **YYYY-MM-DD** format.
* Weekends are automatically excluded when counting leave days.

---

## **Future Enhancements**

* Web-based frontend (React / Angular).
* PostgreSQL for better scalability.
* Email notifications for leave approval/rejection.
* Role-based authentication.
* Multi-company support.




