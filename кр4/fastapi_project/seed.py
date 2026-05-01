from database import SessionLocal
from models import Product

db=SessionLocal()
p1=Product(title="Ноутбук",price=50000, count=10)
p2=Product(title="Мышь", price=1500, count=50)
db.add_all([p1, p2])
db.commit()

print("Добавлены продукты:")
for p in db.query(Product).all():
    print(f"  ID: {p.id}, {p.title}, {p.price} руб, {p.count} шт")

db.close()