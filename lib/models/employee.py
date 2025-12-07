import sys
from models.department import Department

def _get_conn_cursor():
    """Get CONN and CURSOR from the models module"""
    models_module = sys.modules.get('models')
    if models_module:
        return models_module.CONN, models_module.CURSOR
    # Fallback
    import sqlite3
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    return conn, conn.cursor()

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self._name = None
        self._job_title = None
        self._department_id = None
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Job title cannot be empty")
        self._job_title = value

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        CONN, CURSOR = _get_conn_cursor()
        if not isinstance(value, int):
            raise ValueError("Department ID must be an integer")
        if value not in Department.all:
            sql = "SELECT id FROM departments WHERE id = ?"
            CURSOR.execute(sql, (value,))
            if not CURSOR.fetchone():
                raise ValueError("Department ID does not exist")
        self._department_id = value

    @classmethod
    def create_table(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()
        cls.all = {}

    def save(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Employee.all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        emp = cls(name, job_title, department_id)
        emp.save()
        return emp

    def update(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "UPDATE employees SET name = ?, job_title = ?, department_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        Employee.all.pop(self.id, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        emp_id = row[0]
        if emp_id in cls.all:
            return cls.all[emp_id]
        emp = cls(row[1], row[2], row[3], emp_id)
        cls.all[emp_id] = emp
        return emp

    @classmethod
    def get_all(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM employees"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM employees WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def find_by_name(cls, name):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM employees WHERE name = ?"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None