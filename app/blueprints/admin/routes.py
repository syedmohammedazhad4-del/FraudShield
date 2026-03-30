import json
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models import User, Prediction, ModelMetadata


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active_user=True).count()
    total_predictions = Prediction.query.count()
    fraud_predictions = Prediction.query.filter_by(prediction_result='Fraud').count()
    legit_predictions = total_predictions - fraud_predictions
    fraud_rate = round((fraud_predictions / total_predictions * 100), 1) if total_predictions > 0 else 0

    model = ModelMetadata.query.filter_by(is_active=True).first()

    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(10).all()

    # Per-user stats
    users = User.query.all()
    user_stats = []
    for user in users:
        count = Prediction.query.filter_by(user_id=user.id).count()
        fraud = Prediction.query.filter_by(user_id=user.id, prediction_result='Fraud').count()
        user_stats.append({
            'user': user,
            'total': count,
            'fraud': fraud,
            'legit': count - fraud
        })

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           active_users=active_users,
                           total_predictions=total_predictions,
                           fraud_predictions=fraud_predictions,
                           legit_predictions=legit_predictions,
                           fraud_rate=fraud_rate,
                           model=model,
                           recent_predictions=recent_predictions,
                           user_stats=user_stats)


@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    user_data = []
    for user in all_users:
        pred_count = Prediction.query.filter_by(user_id=user.id).count()
        user_data.append({'user': user, 'predictions': pred_count})
    return render_template('admin/users.html', user_data=user_data)


@admin_bp.route('/users/<int:id>/promote', methods=['POST'])
@admin_required
def promote_user(id):
    user = User.query.get_or_404(id)
    if user.role == 'admin':
        flash(f'{user.username} is already an admin.', 'info')
    else:
        user.role = 'admin'
        db.session.commit()
        flash(f'{user.username} has been promoted to Admin.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))

    user.is_active_user = not user.is_active_user
    db.session.commit()
    status = 'activated' if user.is_active_user else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/predictions')
@admin_required
def predictions():
    page = request.args.get('page', 1, type=int)
    result_filter = request.args.get('filter', 'all')
    user_filter = request.args.get('user', 'all')

    query = Prediction.query
    if result_filter == 'fraud':
        query = query.filter_by(prediction_result='Fraud')
    elif result_filter == 'legitimate':
        query = query.filter_by(prediction_result='Legitimate')
    if user_filter != 'all':
        query = query.filter_by(user_id=int(user_filter))

    predictions = query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    users = User.query.all()
    return render_template('admin/predictions.html', predictions=predictions,
                           users=users, current_filter=result_filter,
                           current_user_filter=user_filter)


@admin_bp.route('/analytics')
@admin_required
def analytics():
    metrics = None
    model = ModelMetadata.query.filter_by(is_active=True).first()
    if model:
        metrics = {
            'version': model.version,
            'algorithm': model.algorithm,
            'accuracy': model.accuracy,
            'precision': model.precision_score,
            'recall': model.recall,
            'f1_score': model.f1_score,
            'auc_roc': model.auc_roc,
            'confusion_matrix': json.loads(model.confusion_matrix_json) if model.confusion_matrix_json else None,
            'feature_importances': json.loads(model.feature_importances_json) if model.feature_importances_json else None,
        }

    # Monthly prediction counts (last 12 months)
    all_predictions = Prediction.query.all()
    total_predictions = len(all_predictions)
    fraud_total = sum(1 for p in all_predictions if p.prediction_result == 'Fraud')
    legit_total = total_predictions - fraud_total

    return render_template('admin/analytics.html', metrics=metrics,
                           total_predictions=total_predictions,
                           fraud_total=fraud_total, legit_total=legit_total)
