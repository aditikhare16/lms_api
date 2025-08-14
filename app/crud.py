from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import timedelta
from . import models, schemas

# ----------------- HELPER ----------------- #
def calculate_business_days(start_date, end_date):
    """Count only weekdays between two dates."""
    day_count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Monday=0 ... Friday=4
            day_count += 1
        current += timedelta(days=1)
    return day_count

# ----------------- EMPLOYEE OPS ----------------- #
def create_employee(db: Session, emp):
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

def get_employee(db: Session, emp_id: int):
    return db.get(models.Employee, emp_id)

def employee_balance(db: Session, emp_id: int):
    emp = get_employee(db, emp_id)
    if not emp:
        return None
    used = sum(l.business_days for l in emp.leaves if l.status == models.LeaveStatus.APPROVED)
    return {
        "employee_id": emp.id,
        "total": emp.opening_balance,
        "used": used,
        "remaining": emp.opening_balance - used,
    }

# ----------------- LEAVE OPS ----------------- #
def apply_leave(db: Session, leave: schemas.LeaveApply):
    # 1. Find employee
    emp = db.query(models.Employee).filter(models.Employee.id == leave.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 2. Dates (already date objects from Pydantic)
    start = leave.start_date
    end = leave.end_date
    emp_join = emp.joining_date

    # 3. Validations
    if start < emp_join:
        raise HTTPException(status_code=400, detail=f"Leave cannot start before joining date ({emp.joining_date})")
    if end < emp_join:
        raise HTTPException(status_code=400, detail=f"Leave cannot end before joining date ({emp.joining_date})")
    if end < start:
        raise HTTPException(status_code=400, detail="End date cannot be before start date")

    business_days = calculate_business_days(start, end)
    if business_days <= 0:
        raise HTTPException(status_code=400, detail="Leave duration must be at least 1 business day")

    used_days = sum(l.business_days for l in emp.leaves if l.status == models.LeaveStatus.APPROVED)
    remaining = emp.opening_balance - used_days
    if business_days > remaining:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. You have {remaining} days left.")

    # 4. Check overlapping approved/pending leaves
    overlaps = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.employee_id == leave.employee_id,
        models.LeaveRequest.status.in_([models.LeaveStatus.PENDING, models.LeaveStatus.APPROVED]),
        models.LeaveRequest.start_date <= end,
        models.LeaveRequest.end_date >= start,
    ).first()
    if overlaps:
        raise HTTPException(status_code=400, detail="Leave overlaps with an existing request")

    # 5. Save leave request
    db_leave = models.LeaveRequest(
        employee_id=leave.employee_id,
        start_date=start,
        end_date=end,
        business_days=business_days,
        status=models.LeaveStatus.PENDING,
        reason=leave.reason,
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave

def decide_leave(db: Session, leave_id: int, approve: bool):
    leave = db.get(models.LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    if leave.status != models.LeaveStatus.PENDING:
        raise HTTPException(status_code=400, detail="Leave already decided")
    leave.status = models.LeaveStatus.APPROVED if approve else models.LeaveStatus.REJECTED
    db.commit()
    db.refresh(leave)
    return leave

def list_leaves(db: Session):
    return db.query(models.LeaveRequest).all()
