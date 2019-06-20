from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databasesetup import Base, Item, Category, User

engine = create_engine(
        'sqlite:///catalogapp.db',
        connect_args={'check_same_thread': False}
)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Categories
category1 = Category(id=1, name="Soccer")
session.add(category1)
session.commit()
category2 = Category(id=2, name="Basketball")
session.add(category2)
session.commit()
category3 = Category(id=3, name="Baseball")
session.add(category3)
session.commit()
category4 = Category(id=4, name="Frisbee")
session.add(category4)
session.commit()
category5 = Category(id=5, name="Snowboarding")
session.add(category5)
session.commit()
category6 = Category(id=6, name="Foosball")
session.add(category6)
session.commit()
category7 = Category(id=7, name="Hockey")
session.add(category7)
session.commit()
category8 = Category(id=8, name="Hiking")
session.add(category8)
session.commit()

# Create dummy user
User1 = User(id=1, name="Brian Swalve", email="bswalve@hotmail.com")
session.add(User1)
session.commit()

# Create dummy item
item1 = Item(name="Cracker Lake", description="Out of this world!",
             category_id=8, user_id=1
             )
session.add(item1)
session.commit()

print "added default DB data!"
