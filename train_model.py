"""Standalone CLI script to train the model and save metrics to database."""
import json
import os
import sys

# Ensure we can import the app
sys.path.insert(0, os.path.dirname(__file__))

from app.ml.pipeline import train_model
from app import create_app
from app.extensions import db, bcrypt
from app.models import ModelMetadata, User
from config import Config


def main():
    os.makedirs('models', exist_ok=True)

    metrics = train_model(
        data_path='data/fraud_oracle.csv',
        models_dir='models'
    )

    # Save metrics to database
    app = create_app(Config)
    with app.app_context():
        # Deactivate all existing models
        ModelMetadata.query.update({'is_active': False})

        version = f"v1.0-adaboost-{metrics['feature_count']}f"
        existing = ModelMetadata.query.filter_by(version=version).first()
        if existing:
            db.session.delete(existing)

        model_meta = ModelMetadata(
            version=version,
            algorithm='RandomForest (n=1000, depth=20, fraud-weighted 1:10) + SMOTETomek',
            accuracy=metrics['accuracy'],
            precision_score=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            auc_roc=metrics['auc_roc'],
            confusion_matrix_json=json.dumps(metrics['confusion_matrix']),
            feature_importances_json=json.dumps(metrics['feature_importances']),
            training_samples=metrics['training_samples'],
            test_samples=metrics['test_samples'],
            feature_count=metrics['feature_count'],
            hyperparameters_json=json.dumps(metrics['hyperparameters']),
            training_duration=metrics['training_duration'],
            is_active=True
        )
        db.session.add(model_meta)
        db.session.commit()
        print(f"\nModel metadata saved to database (version: {version})")

        # Seed admin account if not exists
        if not User.query.filter_by(username='Admin').first():
            hashed_pw = bcrypt.generate_password_hash('Admin@12345678').decode('utf-8')
            admin = User(
                full_name='Admin',
                email='smazhad66@gamil.com',
                username='Admin',
                password_hash=hashed_pw,
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin account created (Username: Admin)")
        else:
            print("Admin account already exists")


if __name__ == '__main__':
    main()
