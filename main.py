from fastapi import FastAPI

app = FastAPI()

# --- ЭНДПОИНТЫ С ЗАНЯТИЯ ---

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "0.1.0",
        "day": 1
    }

@app.get("/about")
def get_about():
    return {
        "project": "My First API",
        "author": "Ilia Beliaev",
        "course": "Applied Programming"
    }

# --- ДОМАШНЕЕ ЗАДАНИЕ (3 НОВЫХ ЭНДПОИНТА) ---

# Задача 1: Квадрат числа
@app.get("/square/{number}")
def calculate_square(number: int):
    result = number * number
    return {
        "number": number,
        "square": result,
        "calculation": f"{number} x {number} = {result}"
    }

# Задача 2: Информация о студенте
@app.get("/student")
def get_student():
    return {
        "name": "ТВОЕ ИМЯ",         # <-- ПОМЕНЯЙ ЗДЕСЬ
        "semester": 1, 
        "course": "Wirtschaftsinformatik",
        "university": "ТВОЙ УНИК"    # <-- ПОМЕНЯЙ ЗДЕСЬ
    }

# Задача 3: Удвоение числа
@app.get("/double/{number}")
def calculate_double(number: int):
    result = number * 2
    return {
        "number": number,
        "double": result,
        "calculation": f"{number} x 2 = {result}"
    }