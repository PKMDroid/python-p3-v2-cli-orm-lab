# We'll get CONN and CURSOR from __init__ via the module
import sys

def _get_conn_cursor():
    """Get CONN and CURSOR from the models module"""
    models_module = sys.modules.get('models')
    if models_module:
        return models_module.CONN, models_module.CURSOR
    # Fallback - this shouldn't happen
    import sqlite3
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    return conn, conn.cursor()

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self._name = None
        self._location = None
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

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
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("Location must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Location cannot be empty")
        self._location = value

    @classmethod
    def create_table(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = "DROP TABLE IF EXISTS departments"
        CURSOR.execute(sql)
        CONN.commit()
        cls.all = {}

    def save(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Department.all[self.id] = self

    @classmethod
    def create(cls, name, location):
        dept = cls(name, location)
        dept.save()
        return dept

    def update(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "UPDATE departments SET name = ?, location = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        CONN, CURSOR = _get_conn_cursor()
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        Department.all.pop(self.id, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        dept_id = row[0]
        if dept_id in cls.all:
            return cls.all[dept_id]
        dept = cls(row[1], row[2], dept_id)
        cls.all[dept_id] = dept
        return dept

    @classmethod
    def get_all(cls):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM departments"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM departments WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def find_by_name(cls, name):
        CONN, CURSOR = _get_conn_cursor()
        sql = "SELECT * FROM departments WHERE name = ?"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def employees(self):
        from models.employee import Employee
        return [emp for emp in Employee.all.values() if emp.department_id == self.id]