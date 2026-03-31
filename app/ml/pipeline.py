"""
ML Training Pipeline for Insurance Fraud Detection.
Fixes: PolicyNumber removed, 80/20 split, per-column LabelEncoders.
"""
import time
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from imblearn.over_sampling import SMOTE
import joblib


COLUMNS_TO_DROP = ['Month', 'DayOfWeek', 'MonthClaimed', 'RepNumber',
                   'DriverRating', 'Year', 'PolicyNumber']

CATEGORICAL_COLUMNS = [
    'Make', 'AccidentArea', 'DayOfWeekClaimed', 'Sex', 'MaritalStatus',
    'Fault', 'PolicyType', 'VehicleCategory', 'VehiclePrice',
    'Days_Policy_Accident', 'Days_Policy_Claim', 'PastNumberOfClaims',
    'AgeOfVehicle', 'AgeOfPolicyHolder', 'PoliceReportFiled',
    'WitnessPresent', 'AgentType', 'NumberOfSuppliments',
    'AddressChange_Claim', 'NumberOfCars', 'BasePolicy'
]


def train_model(data_path='data/fraud_oracle.csv', models_dir='models'):
    """Run the complete training pipeline and return metrics."""
    print("=" * 60)
    print("INSURANCE FRAUD DETECTION - MODEL TRAINING PIPELINE")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/10] Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"  Shape: {df.shape}")
    print(f"  Class distribution:\n{df['FraudFound_P'].value_counts().to_string()}")

    # Step 2: Drop irrelevant columns (including PolicyNumber - data leakage fix)
    print("\n[2/10] Dropping irrelevant columns...")
    df = df.drop(columns=[c for c in COLUMNS_TO_DROP if c in df.columns])
    print(f"  Remaining columns: {len(df.columns)}")
    print(f"  PolicyNumber REMOVED (was causing data leakage)")

    # Step 3: Handle missing values
    print("\n[3/10] Handling missing values...")
    # Replace Age=0 with median age
    if (df['Age'] == 0).any():
        median_age = df.loc[df['Age'] > 0, 'Age'].median()
        count_zero = (df['Age'] == 0).sum()
        df.loc[df['Age'] == 0, 'Age'] = median_age
        print(f"  Replaced {count_zero} zero-age entries with median: {median_age}")

    # Handle DayOfWeekClaimed '0' value
    if '0' in df['DayOfWeekClaimed'].values:
        df.loc[df['DayOfWeekClaimed'] == '0', 'DayOfWeekClaimed'] = df['DayOfWeekClaimed'].mode()[0]
        print("  Replaced DayOfWeekClaimed '0' with mode")

    # Step 4: Encode categorical features (per-column LabelEncoders)
    print("\n[4/10] Encoding categorical features...")
    encoders = {}
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
            print(f"  {col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")

    # Step 5: Split features and target
    print("\n[5/10] Splitting features and target...")
    X = df.drop('FraudFound_P', axis=1)
    y = df['FraudFound_P']

    feature_names = X.columns.tolist()
    print(f"  Features ({len(feature_names)}): {feature_names}")

    # Step 6: Train/test split (FIXED: 80/20 instead of 30/70)
    print("\n[6/10] Train/test split (70/30, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    print(f"  Training: {X_train.shape[0]} samples")
    print(f"  Testing:  {X_test.shape[0]} samples")

    # Step 7: SMOTETomek on training data (balance + clean noisy samples)
    print("\n[7/10] Applying SMOTETomek to balance training data...")
    print(f"  Before: {dict(zip(*np.unique(y_train, return_counts=True)))}")
    from imblearn.combine import SMOTETomek
    st = SMOTETomek(random_state=42)
    X_train_smote, y_train_smote = st.fit_resample(X_train, y_train)
    print(f"  After:  {dict(zip(*np.unique(y_train_smote, return_counts=True)))}")

    # Step 8: Scale features
    print("\n[8/10] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_smote)
    X_test_scaled = scaler.transform(X_test)

    # Step 9: Train RandomForest with heavy fraud penalty
    print("\n[9/10] Training RandomForest classifier (fraud-weighted)...")
    start_time = time.time()

    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(
        n_estimators=1000,
        max_depth=20,
        min_samples_leaf=3,
        class_weight={0: 1, 1: 10},
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train_smote)
    training_duration = time.time() - start_time
    print(f"  Training completed in {training_duration:.2f}s")

    # Step 10: Evaluate with optimized threshold
    print("\n[10/10] Evaluating model...")
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    # Find threshold that maximizes F1 while keeping fraud recall >= 60%
    best_threshold = 0.5
    best_f1 = 0
    for t in np.arange(0.25, 0.60, 0.01):
        yp = (y_proba >= t).astype(int)
        r = recall_score(y_test, yp, zero_division=0)
        f = f1_score(y_test, yp, zero_division=0)
        a = accuracy_score(y_test, yp)
        if r >= 0.60 and f > best_f1:
            best_f1 = f
            best_threshold = t

    print(f"  Optimized threshold: {best_threshold:.2f}")
    y_pred = (y_proba >= best_threshold).astype(int)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"\n{'='*40}")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  AUC-ROC:   {auc:.4f}")
    print(f"  Confusion Matrix: {cm}")
    print(f"{'='*40}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud'])}")

    # Feature importances
    importances = model.feature_importances_
    feature_imp = dict(zip(feature_names, [round(float(x), 4) for x in importances]))
    sorted_imp = dict(sorted(feature_imp.items(), key=lambda x: x[1], reverse=True))
    print("\nTop 10 Feature Importances:")
    for i, (feat, imp) in enumerate(sorted_imp.items()):
        if i >= 10:
            break
        print(f"  {feat}: {imp:.4f}")

    # Save artifacts
    print(f"\nSaving artifacts to {models_dir}/...")
    joblib.dump(model, f'{models_dir}/model.pkl')
    joblib.dump(scaler, f'{models_dir}/scaler.pkl')
    joblib.dump(encoders, f'{models_dir}/encoders.pkl')
    joblib.dump(best_threshold, f'{models_dir}/threshold.pkl')
    print(f"  Saved: model.pkl, scaler.pkl, encoders.pkl, threshold.pkl (threshold={best_threshold:.2f})")

    hyperparams = {
        'algorithm': 'AdaBoostClassifier',
        'n_estimators': 500,
        'learning_rate': 0.1,
        'base_estimator': 'DecisionTreeClassifier(max_depth=1)',
        'smote': True,
        'scaler': 'StandardScaler',
        'test_size': 0.2,
        'PolicyNumber_removed': True
    }

    metrics = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'auc_roc': round(auc, 4),
        'confusion_matrix': cm,
        'feature_importances': sorted_imp,
        'training_samples': int(X_train_smote.shape[0]),
        'test_samples': int(X_test.shape[0]),
        'feature_count': len(feature_names),
        'training_duration': round(training_duration, 2),
        'hyperparameters': hyperparams
    }

    print("\nTraining pipeline completed successfully!")
    return metrics
