from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from enum import Enum

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    joining_date: date
    opening_balance: Optional[int] = 24

class EmployeeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    joining_date: date
    opening_balance: int
    class Config:
        orm_mode = True

class LeaveApply(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str]

class LeaveOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    business_days: int
    status: LeaveStatus
    reason: Optional[str]
    class Config:
        orm_mode = True
