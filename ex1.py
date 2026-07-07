from fastapi import FastAPI, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float

app = FastAPI()

@app.post("/products")
def create_product(product: ProductCreate):
    db = SessionLocal() # Mở kết nối MySQL
    
    new_product = ProductModel(
        sku=product.sku,
        name=product.name,
        price=product.price
    )
    db.add(new_product) # Thêm vào session
    
    return {
        "message": "Product prepared successfully", 
        "data": {"sku": product.sku, "name": product.name}
    }

"""
    | STT | Hành vi lỗi trong code hiện tại | Hậu quả đối với Database MySQL | Cách khắc phục bằng SQLAlchemy |
    |-----|---------------------------------|--------------------------------|--------------------------------|
    | 1 | Thiếu lệnh `db.commit()` sau khi `db.add(new_product)` | Dữ liệu chỉ được thêm vào Session (transaction tạm thời), không được ghi vĩnh viễn xuống bảng `products`. API vẫn trả về thành công nhưng MySQL không có bản ghi nào được lưu. | Gọi `db.commit()` sau `db.add(new_product)` để xác nhận (commit) transaction và lưu dữ liệu vào database. Có thể gọi thêm `db.refresh(new_product)` để đồng bộ dữ liệu vừa lưu. |
    | 2 | Không đóng Session sau khi xử lý request | Kết nối đến MySQL không được giải phóng, connection pool bị chiếm dụng. Khi có nhiều request liên tục, hệ thống có thể hết kết nối hoặc giảm hiệu năng. | Đặt `db.close()` trong khối `finally` để luôn giải phóng Session, kể cả khi xảy ra lỗi. |
"""