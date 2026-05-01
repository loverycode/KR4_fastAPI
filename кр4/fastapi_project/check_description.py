from database import SessionLocal
from models import Product

db = SessionLocal()
print("ID | Название | Цена | Кол-во | Description")
print("-" * 50)
for p in db.query(Product).all():
    print(f"{p.id} | {p.title} | {p.price} | {p.count} | '{p.description}'")
db.close()
