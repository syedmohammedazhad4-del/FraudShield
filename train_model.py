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
        # Recreate tables if schema changed (handles new columns like policy_number)
        db.create_all()

        # Remove old model metadata and insert fresh
        ModelMetadata.query.delete()
        db.session.commit()

        version = f"v1.0-adaboost-{metrics['feature_count']}f"

        model_meta = ModelMetadata(
            version=version,
            algorithm='AdaBoost (DecisionTree base, 500 estimators, lr=0.05) + SMOTETomek',
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

        # Seed 5 analyst users
        demo_users = [
            {'full_name': 'Nabeel Rehman', 'email': 'nabeel@fraudshield.com', 'username': 'nabeel', 'password': 'Nabeel@123'},
            {'full_name': 'Abdul Suleman', 'email': 'suleman@fraudshield.com', 'username': 'suleman', 'password': 'Suleman@123'},
            {'full_name': 'Analyst One', 'email': 'analyst1@fraudshield.com', 'username': 'analyst1', 'password': 'Analyst1@123'},
            {'full_name': 'Analyst Two', 'email': 'analyst2@fraudshield.com', 'username': 'analyst2', 'password': 'Analyst2@123'},
            {'full_name': 'Analyst Three', 'email': 'analyst3@fraudshield.com', 'username': 'analyst3', 'password': 'Analyst3@123'},
        ]
        for u in demo_users:
            if not User.query.filter_by(username=u['username']).first():
                hashed_pw = bcrypt.generate_password_hash(u['password']).decode('utf-8')
                user = User(
                    full_name=u['full_name'],
                    email=u['email'],
                    username=u['username'],
                    password_hash=hashed_pw,
                    role='analyst'
                )
                db.session.add(user)
        db.session.commit()
        print("5 analyst accounts created")

        # Seed predictions from test_cases CSV
        from app.models import Prediction
        Prediction.query.delete()
        db.session.commit()
        if True:
            import pandas as pd
            csv_path = 'data/test_cases_new.csv' if os.path.exists('data/test_cases_new.csv') else 'data/test_cases.csv'
            tc = pd.read_csv(csv_path)

            from app.ml.predictor import predict as ml_predict
            from app.field_mappings import WIZARD_STEPS

            all_fields = []
            for step in WIZARD_STEPS:
                all_fields.extend(step['fields'])

            seeded = 0
            for _, row in tc.iterrows():
                assigned_user = row['AssignedUser']
                user = User.query.filter_by(username=assigned_user).first()
                if not user:
                    continue

                form_data = {}
                for field in all_fields:
                    if field == 'PolicyNumber':
                        continue
                    if field in row.index:
                        form_data[field] = str(row[field])

                try:
                    result = ml_predict(form_data)
                    pred = Prediction(
                        user_id=user.id,
                        policy_number=str(row.get('PolicyNumber', '')),
                        prediction_result=result['result'],
                        confidence_score=result['confidence'],
                        input_data_json=json.dumps(form_data),
                        encoded_data_json=json.dumps(result['encoded_data']),
                        model_version=version
                    )
                    db.session.add(pred)
                    seeded += 1
                except Exception as e:
                    print(f"  Skipped {row.get('TestCase','?')}: {e}")

            db.session.commit()
            print(f"{seeded} predictions seeded from test cases")
        else:
            print("Predictions already exist, skipping seed")


if __name__ == '__main__':
    main()
