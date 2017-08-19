from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import bookType, Base


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBsession = sessionmaker(bind = engine)

session = DBsession()

book1 = bookType(type = "Fiction")
session.add(book1)
session.commit()

book2 = bookType(type = "Non-Fiction")
session.add(book2)
session.commit()

book3 = bookType(type = "Romananc")
session.add(book3)
session.commit()

book4 = bookType(type = "Action and Adventure")
session.add(book4)
session.commit()

book5 = bookType(type = "Drama")
session.add(book5)
session.commit()

book6 =bookType(type = "Biographies")
session.add(book6)
session.commit()

print "Columns Created"