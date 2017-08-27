from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin

Base = declarative_base()

class bookType(Base):
	__tablename__ = 'book_type'
	id = Column(Integer, primary_key = True)
	type = Column(String(140), nullable = False)

class author(Base, UserMixin):
	__tablename__ = 'author'
	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False)
	email = Column(String(250), nullable = False)
	password = Column(String(500))
	gid = Column(Integer, unique=True)

class book(Base):
	__tablename__ = 'book'
	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	description = Column(String(1000))
	type = relationship(bookType)
	type_id = Column(Integer, ForeignKey('book_type.id'))
	author = relationship(author)
	author_id = Column(Integer, ForeignKey('author.id'))


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)