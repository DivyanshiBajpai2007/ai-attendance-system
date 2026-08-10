import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import ARRAY, Column, Date, DateTime, Float, ForeignKey, Integer, String, Time, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    embeddings = relationship("Embedding", back_populates="employee", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    embedding_vector = Column(ARRAY(Float), nullable=False)
    label = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="embeddings")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    confidence_score = Column(Float)
    device_location = Column(String(200))
    status = Column(String(20), default="present")

    employee = relationship("Employee", back_populates="attendance_records")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
