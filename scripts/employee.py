import csv

class Employee:
    def __init__(self, name, phone, salary, role, age, working_from, years_worked):
        self.name = name
        self.phone = phone
        self.salary = salary
        self.role = role
        self.age = age
        self.working_from = working_from
        self.years_worked = years_worked

class EmployeeManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS employee(
            e_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(30) NOT NULL,
            phone VARCHAR(40) NOT NULL,
            salary VARCHAR(20) NOT NULL,
            role VARCHAR(15) NOT NULL,
            age INTEGER NOT NULL,
            working_from VARCHAR(12) NOT NULL,
            year_worked VARCHAR(15) 
        );
        """
        self.db.execute_query(query)

    def add_employee(self, emp, auto_commit=True):
        query = """
        INSERT INTO employee(name, phone, salary, role, age, working_from, year_worked)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """
        values = (emp.name, emp.phone, emp.salary, emp.role, emp.age, emp.working_from, emp.years_worked)
        
        try:
            self.db.execute_query(query, values)
            if auto_commit:
                self.db.commit()
                print(f"Employee {emp.name} added successfully.")
        except Exception as e:
            print(f"Error adding employee: {e}")

    def import_from_csv(self, filename):
        try:
            with open(filename, "r") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    new_emp = Employee(
                        row["Name"], row["Phone"], row["Salary"], 
                        row["Role"], row["Age"], row["Working_From"], 
                        row["Years_Worked"]
                    )
                    self.add_employee(new_emp, auto_commit=False)
                    count += 1
            self.db.commit()
            print(f"Successfully imported {count} employees.")
        except FileNotFoundError:
            print("Error: CSV file not found.")

    def show_all_employees(self):
        employees = self.db.fetch_all("SELECT * FROM employee")
        
        if not employees:
            print("No employees found.")
            return

        header_fmt = "{:<5} {:<22} {:<22} {:<22} {:>12} {:^12} {:^10}"
        headers = ("ID", "Name", "Role", "Phone", "Salary", "Joined", "Exp")
        
        print("\n" + "="*115)
        print(header_fmt.format(*headers))
        print("-" * 115)

        for emp in employees:
            e_id, name, phone, salary, role, age, joined, exp = emp
            print(header_fmt.format(
                e_id, str(name).strip()[:20], str(role).strip()[:20], 
                str(phone).strip()[:20], str(salary).strip(), 
                str(joined).strip(), str(exp).strip()
            ))
        print("="*115 + "\n")