import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests

BASE = "http://127.0.0.1:8000"
HR_KEY = "admin123"  # must match your .env

root = tk.Tk()
root.title("Leave Management System")
root.geometry("750x650")

# Define frames early
emp_frame = tk.LabelFrame(root, text="Employee Panel", font=("Arial", 12, "bold"))
hr_frame = tk.LabelFrame(root, text="HR Panel", font=("Arial", 12, "bold"))

# ---------------------- EMPLOYEE FUNCTIONS ---------------------- #
def apply_leave():
    try:
        emp_id_val = emp_id_entry.get()
        if not emp_id_val.isdigit():
            messagebox.showerror("Error", "Employee ID must be a number")
            return

        data = {
            "employee_id": int(emp_id_val),
            "start_date": start_entry.get(),
            "end_date": end_entry.get(),
            "reason": reason_entry.get()
        }
        r = requests.post(f"{BASE}/leaves/apply", json=data)
        res = r.json()
        if r.status_code != 200 and "detail" in res:
            messagebox.showerror("Error", str(res["detail"]))
        else:
            messagebox.showinfo("Success", f"Leave Applied ✅\nStatus: {res['status']}\nDays: {res['business_days']}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def get_balance():
    emp_id_val = emp_id_entry.get()
    if not emp_id_val.isdigit():
        messagebox.showerror("Error", "Employee ID must be a number")
        return
    r = requests.get(f"{BASE}/employees/{emp_id_val}/balance")
    res = r.json()
    if r.status_code != 200 and "detail" in res:
        messagebox.showerror("Error", str(res["detail"]))
    else:
        messagebox.showinfo(
            "Leave Balance",
            f"Employee {res['employee_id']}\n"
            f"Total: {res['total']} days\n"
            f"Used: {res['used']} days\n"
            f"Remaining: {res['remaining']} days"
        )

# ---------------------- HR FUNCTIONS ---------------------- #
def show_hr_panel():
    pwd = simpledialog.askstring("HR Login", "Enter HR Password:", show="*")
    if pwd == HR_KEY:
        clear_panels()
        hr_frame.pack(fill="both", expand=True, padx=10, pady=10)
    else:
        messagebox.showerror("Access Denied", "Invalid HR password ❌")


def add_employee():
    try:
        open_bal_val = openbal_entry.get()
        if not open_bal_val.isdigit():
            messagebox.showerror("Error", "Opening Balance must be a number")
            return
        data = {
            "name": name_entry.get(),
            "email": email_entry.get(),
            "department": dept_entry.get(),
            "joining_date": join_entry.get(),
            "opening_balance": int(open_bal_val)
        }
        r = requests.post(f"{BASE}/employees", json=data, headers={"X-API-Key": HR_KEY})
        res = r.json()
        if r.status_code != 200 and "detail" in res:
            messagebox.showerror("Error", str(res["detail"]))
        else:
            messagebox.showinfo("Added", f"Employee {res['name']} added with ID {res['id']}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_leaves():
    try:
        r = requests.get(f"{BASE}/leaves", headers={"X-API-Key": HR_KEY})
        res = r.json()
        if isinstance(res, list):
            win = tk.Toplevel(root)
            win.title("All Leave Requests")
            tree = ttk.Treeview(win, columns=("ID", "EmpID", "Start", "End", "Days", "Status"), show="headings")
            for col in ("ID", "EmpID", "Start", "End", "Days", "Status"):
                tree.heading(col, text=col)
                tree.column(col, width=100)
            for leave in res:
                tree.insert("", "end", values=(
                    leave["id"], leave["employee_id"], leave["start_date"],
                    leave["end_date"], leave["business_days"], leave["status"]
                ))
            tree.pack(fill="both", expand=True)

            def act_on_leave(action):
                selected = tree.focus()
                if not selected:
                    messagebox.showerror("Error", "Select a leave first")
                    return
                lid = tree.item(selected)["values"][0]
                if action == "approve":
                    r = requests.post(f"{BASE}/leaves/{lid}/approve", headers={"X-API-Key": HR_KEY})
                else:
                    r = requests.post(f"{BASE}/leaves/{lid}/reject", headers={"X-API-Key": HR_KEY})
                res = r.json()
                messagebox.showinfo("Result", f"Leave {lid} → {res.get('status', '?')}")
                tree.item(selected, values=(
                    lid, tree.item(selected)["values"][1],
                    tree.item(selected)["values"][2],
                    tree.item(selected)["values"][3],
                    tree.item(selected)["values"][4],
                    res.get("status", "?")
                ))

            tk.Button(win, text="Approve Selected", bg="green", command=lambda: act_on_leave("approve")).pack(side="left", padx=10, pady=5)
            tk.Button(win, text="Reject Selected", bg="red", command=lambda: act_on_leave("reject")).pack(side="left", padx=10, pady=5)
        else:
            messagebox.showerror("Error", str(res))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------------- UI LAYOUT ---------------------- #
def show_employee_panel():
    clear_panels()
    emp_frame.pack(fill="both", expand=True, padx=10, pady=10)


def clear_panels():
    emp_frame.pack_forget()
    hr_frame.pack_forget()


# --- Top Menu --- #
tk.Label(root, text="Choose Role", font=("Arial", 14, "bold")).pack(pady=10)
btn_frame = tk.Frame(root)
btn_frame.pack()
tk.Button(btn_frame, text="Employee", width=20, command=show_employee_panel, bg="lightblue").pack(side="left", padx=10)
tk.Button(btn_frame, text="HR", width=20, command=show_hr_panel, bg="lightgreen").pack(side="left", padx=10)

# --- Employee Frame --- #
tk.Label(emp_frame, text="Employee ID").grid(row=0, column=0, padx=5, pady=5)
emp_id_entry = tk.Entry(emp_frame)
emp_id_entry.grid(row=0, column=1)

tk.Label(emp_frame, text="Start Date (YYYY-MM-DD)").grid(row=1, column=0)
start_entry = tk.Entry(emp_frame)
start_entry.grid(row=1, column=1)

tk.Label(emp_frame, text="End Date (YYYY-MM-DD)").grid(row=2, column=0)
end_entry = tk.Entry(emp_frame)
end_entry.grid(row=2, column=1)

tk.Label(emp_frame, text="Reason").grid(row=3, column=0)
reason_entry = tk.Entry(emp_frame)
reason_entry.grid(row=3, column=1)

tk.Button(emp_frame, text="Apply Leave", command=apply_leave, bg="orange").grid(row=4, column=0, pady=10)
tk.Button(emp_frame, text="Check Balance", command=get_balance, bg="lightgrey").grid(row=4, column=1, pady=10)

# --- HR Frame --- #
tk.Label(hr_frame, text="Name").grid(row=0, column=0)
name_entry = tk.Entry(hr_frame)
name_entry.grid(row=0, column=1)

tk.Label(hr_frame, text="Email").grid(row=1, column=0)
email_entry = tk.Entry(hr_frame)
email_entry.grid(row=1, column=1)

tk.Label(hr_frame, text="Dept").grid(row=2, column=0)
dept_entry = tk.Entry(hr_frame)
dept_entry.grid(row=2, column=1)

tk.Label(hr_frame, text="Joining Date (YYYY-MM-DD)").grid(row=3, column=0)
join_entry = tk.Entry(hr_frame)
join_entry.grid(row=3, column=1)

tk.Label(hr_frame, text="Opening Balance").grid(row=4, column=0)
openbal_entry = tk.Entry(hr_frame)
openbal_entry.grid(row=4, column=1)

tk.Button(hr_frame, text="Add Employee", command=add_employee, bg="lightblue").grid(row=5, columnspan=2, pady=5)
tk.Button(hr_frame, text="View All Leaves", command=view_leaves, bg="lightgrey").grid(row=6, columnspan=2, pady=5)

root.mainloop()
