from models import engine, User, sessionmaker

# Create the session
Session = sessionmaker(bind=engine)
session = Session()

# Create a test user
test_user = User(username="Spike_Shooter_Caleb")

# Put it on the "desk" (Session)
session.add(test_user)

# Save it to the "cabinet" (Database)
session.commit()

print(f"Added {test_user.username} to the database!")