"""Load and serve model metrics for the performance page."""
import json
from app.models import ModelMetadata


def get_active_model_metrics():
    """Get metrics for the currently active model."""
    model = ModelMetadata.query.filter_by(is_active=True).first()
    if not model:
        return None

    return {
        'version': model.version,
        'algorithm': model.algorithm,
        'accuracy': model.accuracy,
        'precision': model.precision_score,
        'recall': model.recall,
        'f1_score': model.f1_score,
        'auc_roc': model.auc_roc,
        'confusion_matrix': json.loads(model.confusion_matrix_json) if model.confusion_matrix_json else None,
        'feature_importances': json.loads(model.feature_importances_json) if model.feature_importances_json else None,
        'training_samples': model.training_samples,
        'test_samples': model.test_samples,
        'feature_count': model.feature_count,
        'hyperparameters': json.loads(model.hyperparameters_json) if model.hyperparameters_json else None,
        'training_duration': model.training_duration,
        'trained_at': model.trained_at
    }
