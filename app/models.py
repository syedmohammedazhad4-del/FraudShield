from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, default='analyst')
    is_active_user = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_active(self):
        return self.is_active_user


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prediction_result = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    input_data_json = db.Column(db.Text, nullable=False)
    encoded_data_json = db.Column(db.Text)
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)


class ModelMetadata(db.Model):
    __tablename__ = 'model_metadata'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    algorithm = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float)
    precision_score = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    auc_roc = db.Column(db.Float)
    confusion_matrix_json = db.Column(db.Text)
    feature_importances_json = db.Column(db.Text)
    training_samples = db.Column(db.Integer)
    test_samples = db.Column(db.Integer)
    feature_count = db.Column(db.Integer)
    hyperparameters_json = db.Column(db.Text)
    training_duration = db.Column(db.Float)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    trained_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
