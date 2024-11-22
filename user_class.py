from sqlalchemy import (Column, Integer, String, Date, ForeignKey, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

Base = declarative_base()

class Polzovatels(Base):
    __tablename__ = "polzovatel"
    id = Column(Integer, primary_key=True)
    fio = Column(String)
    login = Column(String)
    ppassword = Column(String)
    pincode = Column(String)
    
    @staticmethod
    def hash_password(password):
        # Генерация соли и хеширование пароля
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password, hashed_password):
        # Сравнение обычного пароля с хешем
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
class Platezs(Base):
    __tablename__ = "platez"
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    category = Column(String)
    name = Column(String)
    count = Column(Integer)
    price = Column(Float)
    checks = Column(Float)

    
class Connect():
    def create_connection():
        engine = create_engine("postgresql://postgres:1234@localhost:5432/postgres")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session