from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_doctor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Doctor(User):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String, nullable=False)
    license_number = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialization='{self.specialization}')>"

class Admin(User):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    admin_level = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Admin(username='{self.username}', admin_level='{self.admin_level}')>"