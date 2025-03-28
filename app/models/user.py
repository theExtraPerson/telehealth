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

    user_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

class Doctor(User):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String, nullable=False)
    license_number = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialization='{self.specialization}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
        'inherit_condition': (id == User.id)
    }

class Admin(User):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    access_level = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Admin(username='{self.username}', admin_level='{self.access_level}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'inherit_condition': (id == user_id)
    }