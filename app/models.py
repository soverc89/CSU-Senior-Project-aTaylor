from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    properties = db.relationship("Property", back_populates="owner", cascade="all, delete-orphan")

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    owner = db.relationship("User", back_populates="properties")
    stands = db.relationship("Stand", back_populates="property", cascade="all, delete-orphan")

class Stand(db.Model):
    __tablename__ = 'stands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Adding a degree field as per requirements!
    degree = db.Column(db.Integer, nullable=True) 
    
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    property = db.relationship("Property", back_populates="stands")

    def current_score(self, wind_degree):
        """
        Calculates the Stand's grade based on the current wind direction.
        100% means the wind is blowing directly FROM the stand's facing degree,
        meaning the hunter's scent is blown BEHIND them (optimal).
        
        0% means the wind is blowing directly INTO the stand's facing degree,
        meaning the hunter's scent is blown right in front of them (worst).
        """
        if wind_degree is None or self.degree is None:
            return None
            
        # Calculate the absolute shortest path difference (0 to 180 degrees)
        difference = 180 - abs(abs(wind_degree - self.degree) - 180)
        score = (difference / 180) * 100
        return int(round(score))
