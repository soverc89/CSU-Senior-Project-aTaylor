from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine('sqlite:///hunting.db')

Base = declarative_base()

class User(Base):
	__tablename__= 'users'
	id = Column(Integer, primary_key = True)
	username = Column(String, unique=True, nullable=False)
	properties = relationship("Property", back_populates="owner")

class Property(Base):
	__tablename__= 'properties'
	id = Column(Integer, primary_key = True)
	name = Column(String, nullable=False)
	user_id = Column(Integer, ForeignKey('users.id'))

	owner = relationship("User", back_populates="properties")
	stands = relationship("Stand", back_populates="property")

class Stand(Base):
	__tablename__= 'stands'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	property_id = Column(Integer, ForeignKey('properties.id'))
	property = relationship("Property", back_populates="stands")


if __name__ == "__main__":
	Base.metadata.create_all(engine)
	print("It is working")