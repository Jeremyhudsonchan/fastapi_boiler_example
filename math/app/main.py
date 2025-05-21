from fastapi import FastAPI, Depends, HTTPException
from models import MathInput, OperationResult
from logger import logger
from auth import verify_token
import sqlite3
import datetime

app = FastAPI(title="Secure Math API", version="1.0.0")

# DB connection
def get_db():
    conn = sqlite3.connect("math_operations.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT,
            a REAL,
            b REAL,
            result REAL,
            timestamp TEXT
        )
    """)
    return conn

# Save the operation to the DB
def save_operation(conn, op: str, a: float, b: float, result: float):
    conn.execute(
        "INSERT INTO operations (operation, a, b, result, timestamp) VALUES (?, ?, ?, ?, ?)",
        (op, a, b, result, str(datetime.datetime.now()))
    )
    conn.commit()

# Common handler function
def handle_operation(op_name: str, a: float, b: float, result_fn, conn):
    result = result_fn(a, b)
    save_operation(conn, op_name, a, b, result)
    logger.info(f"{op_name.upper()}: {a} and {b} = {result}")
    return {"operation": op_name, "a": a, "b": b, "result": result}


# Endpoints
@app.post("/add", response_model=OperationResult)
def add(input: MathInput, conn=Depends(get_db), token=Depends(verify_token)):
    return handle_operation("add", input.a, input.b, lambda a, b: a + b, conn)

@app.post("/subtract", response_model=OperationResult)
def subtract(input: MathInput, conn=Depends(get_db), token=Depends(verify_token)):
    return handle_operation("subtract", input.a, input.b, lambda a, b: a - b, conn)

@app.post("/multiply", response_model=OperationResult)
def multiply(input: MathInput, conn=Depends(get_db), token=Depends(verify_token)):
    return handle_operation("multiply", input.a, input.b, lambda a, b: a * b, conn)

@app.post("/divide", response_model=OperationResult)
def divide(input: MathInput, conn=Depends(get_db), token=Depends(verify_token)):
    if input.b == 0:
        logger.warning("Division by zero attempted")
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return handle_operation("divide", input.a, input.b, lambda a, b: a / b, conn)
