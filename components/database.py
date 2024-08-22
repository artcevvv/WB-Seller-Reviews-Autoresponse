from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, URL
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_SQL_PASS = os.getenv("POSTGRES_SQL_PASS")

POSTGRES_SQL_URL = URL.create(
    "postgresql",
    username="postgres",
    password=POSTGRES_SQL_PASS,
    host="localhost",
    port=5432,
    database="postgres",
)

engine = create_engine(POSTGRES_SQL_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Integer, unique=True, index=True)
    phone_number = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now())

    tokens = relationship("Token", back_populates="owner")


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wb_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    owner = relationship("User", back_populates="tokens")


Base.metadata.create_all(bind=engine)