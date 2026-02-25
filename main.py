from fastapi import FastAPI
from pydantic import BaseModel
import pyodbc

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\MSSQLLocalDB;"
    "DATABASE=SqlInjectionLab;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)


@app.post("/login-insecure")
def login_insecure(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT * FROM Users
        WHERE username = '{data.username}'
        AND password = '{data.password}'
    """

    print("INSECURE QUERY:", query)

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return {
            "variant": "insecure",
            "status": "success" if rows else "failed",
            "rows_returned": len(rows)
        }
    except Exception:
        return {"variant": "insecure", "status": "error"}
    finally:
        conn.close()

@app.post("/login-partial")
def login_partial(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM Users
        WHERE username = ?
        AND password = '""" + data.password + "'"

    print("PARTIAL QUERY:", query)

    try:
        cursor.execute(query, (data.username,))
        rows = cursor.fetchall()
        return {
            "variant": "partial",
            "status": "success" if rows else "failed",
            "rows_returned": len(rows)
        }
    except Exception:
        return {"variant": "partial", "status": "error"}
    finally:
        conn.close()

@app.post("/login-secure")
def login_secure(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM Users
        WHERE username = ?
        AND password = ?
    """

    print("SECURE QUERY: Prepared Statement Used")

    try:
        cursor.execute(query, (data.username, data.password))
        rows = cursor.fetchall()
        return {
            "variant": "secure",
            "status": "success" if rows else "failed",
            "rows_returned": len(rows)
        }
    except Exception:
        return {"variant": "secure", "status": "error"}
    finally:
        conn.close()