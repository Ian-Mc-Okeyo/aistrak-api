# app/init_db.py
from core.database import Base, engine  # engine should point to your MySQL database
from models.ai import * # Import all your models so SQLAlchemy registers them
from models.notification import *  # Import Notification model
from models.user import *  # Import User model if it exists
from models.prediction import *  # Import Prediction model if it exists
from models.transaction import *  # Import Transaction model if it exists
from models.wallet import *  # Import Wallet model if it exists
from models.withdrawal import *
from models.token import *  # Import Token model if it exists

Base.metadata.create_all(bind=engine)
print("Tables created.")
