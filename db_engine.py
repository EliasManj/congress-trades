from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Define a base class
Base = declarative_base()

# Define the Person class
class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    prefix = Column(String)
    lastname = Column(String)
    firstname = Column(String)
    suffix = Column(String)
    
    __table_args__ = (UniqueConstraint('prefix', 'lastname', 'firstname', name='_person_unique'),)

    # Relationship to fillings
    fillings = relationship("Filling", back_populates="person")

# Define the Filling class
class Filling(Base):
    __tablename__ = 'fillings'
    docid = Column(String, primary_key=True)  # Primary key column added
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    filing_type = Column(String)
    state_dst = Column(String)
    year = Column(String)
    filing_date = Column(String)
    
    __table_args__ = (UniqueConstraint('person_id', 'filing_date', 'docid', name='_filling_unique'),)

    # Relationship to person
    person = relationship("Person", back_populates="fillings")
    transactions = relationship("Transaction", back_populates="filling")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    docid = Column(Integer, ForeignKey('fillings.docid'), nullable=False)
    asset = Column(String)
    security = Column(String)
    ticker = Column(String)
    transaction_type = Column(String)
    transaction_date = Column(String)
    notification_date = Column(String)
    min_amount = Column(String)
    max_amount = Column(String)
    
    __table_args__ = (UniqueConstraint('asset', 'security', 'docid', 'transaction_date', 'min_amount', 'max_amount', name='_transaction_unique'),)

    # Relationship to filling
    filling = relationship("Filling", back_populates="transactions")

class DbEngine:

    def __init__(self, url):
        self.engine = create_engine(url, echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()