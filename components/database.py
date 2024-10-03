from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, URL, BigInteger, ARRAY
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

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class ReviewResponse(Base):
    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_id = Column(String, nullable=False)
    product_name = Column(String, nullable=True)
    message_id = Column(BigInteger, unique=True, nullable=False)
    review_text = Column(String, nullable=True)
    review_rating = Column(String, nullable=True)
    chatgpt_response = Column(String, nullable=False)
    response_sent = Column(DateTime, default=datetime.now)

    # Relationship with User
    user = relationship("User", back_populates="responses")

# Add this to the User model for the relationship
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, index=True)
    phone_number = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    points = Column(Integer, default=10)
    review_ids = Column(ARRAY(String), nullable=True)

    tokens = relationship("Token", back_populates="owner")
    responses = relationship("ReviewResponse", back_populates="user")



class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wb_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    owner = relationship("User", back_populates="tokens")


Base.metadata.create_all(bind=engine)
