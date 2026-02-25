from fastapi import FastAPI
import pyodbc

app = FastAPI()

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\MSSQLLocalDB;"
    "DATABASE=SqlInjectionLab;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(conn_str)


@app.get("/login-insecure")
def login_insecure(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM Users WHERE username = '{username}' AND password = '{password}'"
    print("INSECURE QUERY:", query)

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return {"status": "success" if rows else "failed", "rows": len(rows)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/login-partial")
def login_partial(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM Users WHERE username = ? AND password = '" + password + "'"
    print("PARTIAL QUERY:", query)

    try:
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        return {"status": "success" if rows else "failed", "rows": len(rows)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/login-secure")
def login_secure(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM Users WHERE username = ? AND password = ?"
    print("SECURE QUERY: Prepared Statement Used")

    try:
        cursor.execute(query, (username, password))
        rows = cursor.fetchall()
        return {"status": "success" if rows else "failed", "rows": len(rows)}
    except Exception as e:
        return {"error": str(e)}