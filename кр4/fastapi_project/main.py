from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from exceptions import (CustomExceptionA, CustomExceptionB, register_exception_handlers)
from models import User
app=FastAPI()
register_exception_handlers(app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc: RequestValidationError):
    errors=[]
    for error in exc.errors():
        field = error["loc"][1] if len(error["loc"]) > 1 else str(error["loc"])
        errors.append({
            "field":field,
            "message":error["msg"],
            "type":error["type"],
        })
    return JSONResponse(status_code=422, content={
            "status_code":422,
            "error_type": "ValidationError",
            "message":"Ошибка валидации данных",
            "details":{"errors" : errors}
        })

user_db={}
user_id_counter=1
async_items_db={}
async_items_counter=1

@app.get("/")
def root():
    return {"message":"Сервер работает"}
@app.get("/check/{value}")
def check_value(value: int):
    if value<0:
        raise CustomExceptionA(f"Значение {value} меньше 0 — условие не выполнено")
    if value>100:
        raise CustomExceptionB(f"Значение {value} больше 100 — ресурс вне допустимого диапазона")
    return {"status": "success", "value": value, "message": "Значение корректно"}

@app.get("/product/{product_id}")
def get_product(product_id:int):
    if product_id==0:
        raise CustomExceptionB(f"Продукт с id {product_id} не найден")
    return {"id": product_id, "name": "Продукт"}

@app.post("/register", status_code=201)
def register_user(user: User):
    global user_id_counter
    for existing in user_db.values():
        if existing["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
        if existing["username"]==user.username:
            raise HTTPException(status_code=400, detail="Username already exists")
    user_db[user_id_counter]=user.model_dump()
    user_id_counter+=1
    return  {"message": "User registered", "user_id": user_id_counter - 1}

@app.get("/users")
def get_users():
    return list(user_db.values())

@app.post("/async/items",status_code=201)
async def create_async_item(name:str,quantity:int=1, price:float=0):
    global async_items_counter
    item={
        "id": async_items_counter,
        "name": name,
        "quantity": quantity,
        "price": price
    }
    async_items_db[async_items_counter]=item
    async_items_counter+=1
    return item

@app.get("/async/items/{item_id}")
async def get_async_item(item_id:int):
    if item_id not in async_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return async_items_db[item_id]

@app.delete("/async/items/{item_id}", status_code=204)
async def delete_async_item(item_id:int):
    if item_id not in async_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del async_items_db[item_id]
    return None
