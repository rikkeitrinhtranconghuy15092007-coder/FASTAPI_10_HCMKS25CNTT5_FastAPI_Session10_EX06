import uvicorn
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ShipmentModel(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), default="PREPARING")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Shipping Shipment Management API")

class ShipmentCreate(BaseModel):
    tracking_number: str

@app.post("/shipments", status_code=status.HTTP_201_CREATED)
async def create_shipment(payload: ShipmentCreate, db: Session = Depends(get_db)):
    existing_shipment = db.query(ShipmentModel).filter(
        ShipmentModel.tracking_number == payload.tracking_number.strip()
    ).first()
    
    if existing_shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Mã vận đơn này đã được khởi tạo trước đó"
        )
        
    new_shipment = ShipmentModel(tracking_number=payload.tracking_number.strip())
    db.add(new_shipment)
    db.commit()
    db.refresh(new_shipment)
    
    return {
        "message": "Đăng ký mã vận đơn thành công!", 
        "data": new_shipment
    }

@app.get("/shipments", status_code=status.HTTP_200_OK)
async def get_all_shipments(db: Session = Depends(get_db)):
    shipments = db.query(ShipmentModel).all()
    
    return {
        "total": len(shipments), 
        "shipments": shipments
    }