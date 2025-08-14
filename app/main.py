from fastapi import FastAPI, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from . import models, schemas, crud

# ---------------- Hardcoded HR API key ----------------
HR_API_KEY = "admin123"

# ---------------- Create DB tables at startup ----------------
Base.metadata.create_all(bind=engine)

# ---------------- Initialize FastAPI ----------------
app = FastAPI(title="Leave Management System", version="1.0.0")

# ---------------- Health Check ----------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- HR Auth ----------------
def hr_auth(x_api_key: str = Header(..., description="HR API key in X-API-Key")):
    if x_api_key != HR_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ---------------- Employees ----------------
@app.post("/employees", response_model=schemas.EmployeeOut, status_code=201)
def add_employee(
    emp: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    _: None = Depends(hr_auth)
):
    new_emp = models.Employee(**emp.dict())
    try:
        return crud.create_employee(db, new_emp)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/employees/{emp_id}/balance")
def balance(emp_id: int, db: Session = Depends(get_db)):
    bal = crud.employee_balance(db, emp_id)
    if not bal:
        raise HTTPException(status_code=404, detail="Employee not found")
    return bal

@app.get("/employees/{emp_id}", response_model=schemas.EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = crud.get_employee(db, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# ---------------- Leaves (Employee) ----------------
@app.post("/leaves/apply", response_model=schemas.LeaveOut, status_code=201)
def apply_leave(leave: schemas.LeaveApply, db: Session = Depends(get_db)):
    try:
        return crud.apply_leave(db, leave)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- Leaves (HR) ----------------
@app.get("/leaves", response_model=List[schemas.LeaveOut])
def all_leaves(db: Session = Depends(get_db), _: None = Depends(hr_auth)):
    return crud.list_leaves(db)

@app.post("/leaves/{leave_id}/approve", response_model=schemas.LeaveOut)
def approve(leave_id: int, db: Session = Depends(get_db), _: None = Depends(hr_auth)):
    return crud.decide_leave(db, leave_id, True)

@app.post("/leaves/{leave_id}/reject", response_model=schemas.LeaveOut)
def reject(leave_id: int, db: Session = Depends(get_db), _: None = Depends(hr_auth)):
    return crud.decide_leave(db, leave_id, False)
