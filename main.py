from fastapi import FastAPI
from pydantic import BaseModel
import pyodbc

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

class SearchRequest(BaseModel):
    query: str

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=SqlInjectionLab;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str, timeout=5)

@app.post("/login-insecure")
def login_insecure(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM Users WHERE username = '{data.username}' AND password = '{data.password}'"
    print("INSECURE QUERY:", query)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "password": r.password, "role": r.role} for r in rows]
        return {"variant": "insecure", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "insecure", "status": "error"}
    finally:
        conn.close()

@app.post("/login-partial")
def login_partial(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Users WHERE username = ? AND password = '" + data.password + "'"
    print("PARTIAL QUERY:", query)
    try:
        cursor.execute(query, (data.username,))
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "password": r.password, "role": r.role} for r in rows]
        return {"variant": "partial", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "partial", "status": "error"}
    finally:
        conn.close()

@app.post("/login-secure")
def login_secure(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM Users WHERE username = ? AND password = ?"
    print("SECURE QUERY: Prepared Statement Used")
    try:
        cursor.execute(query, (data.username, data.password))
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "password": r.password, "role": r.role} for r in rows]
        return {"variant": "secure", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "secure", "status": "error"}
    finally:
        conn.close()

@app.post("/search-insecure")
def search_insecure(data: SearchRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT id, username, role FROM Users WHERE username LIKE '%{data.query}%'"
    print("INSECURE SEARCH QUERY:", query)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "role": r.role} for r in rows]
        return {"variant": "insecure", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "insecure", "status": "error"}
    finally:
        conn.close()

@app.post("/search-partial")
def search_partial(data: SearchRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, username, role FROM Users WHERE username LIKE '%" + data.query + "%'"
    print("PARTIAL SEARCH QUERY:", query)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "role": r.role} for r in rows]
        return {"variant": "partial", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "partial", "status": "error"}
    finally:
        conn.close()

@app.post("/search-secure")
def search_secure(data: SearchRequest):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, username, role FROM Users WHERE username LIKE ?"
    print("SECURE SEARCH QUERY: Prepared Statement Used")
    try:
        cursor.execute(query, (f"%{data.query}%",))
        rows = cursor.fetchall()
        result_list = [{"id": r.id, "username": r.username, "role": r.role} for r in rows]
        return {"variant": "secure", "results": len(rows), "data": result_list}
    except Exception:
        return {"variant": "secure", "status": "error"}
    finally:
        conn.close()