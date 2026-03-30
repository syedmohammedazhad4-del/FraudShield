from flask import render_template, request
from flask_login import login_required, current_user
from app.blueprints.main import main_bp
from app.models import Prediction, ModelMetadata
from app.extensions import db


@main_bp.route('/')
def home():
    return render_template('main/home.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    total = Prediction.query.filter_by(user_id=current_user.id).count()
    fraud_count = Prediction.query.filter_by(user_id=current_user.id, prediction_result='Fraud').count()
    legit_count = total - fraud_count

    model = ModelMetadata.query.filter_by(is_active=True).first()
    accuracy = round(model.accuracy * 100, 1) if model else 0

    recent = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc()).limit(5).all()

    return render_template('main/dashboard.html',
                           total=total, fraud_count=fraud_count,
                           legit_count=legit_count, accuracy=accuracy,
                           recent=recent)


@main_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    result_filter = request.args.get('filter', 'all')

    query = Prediction.query.filter_by(user_id=current_user.id)
    if result_filter == 'fraud':
        query = query.filter_by(prediction_result='Fraud')
    elif result_filter == 'legitimate':
        query = query.filter_by(prediction_result='Legitimate')

    predictions = query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template('main/history.html', predictions=predictions,
                           current_filter=result_filter)


@main_bp.route('/about')
def about():
    model = ModelMetadata.query.filter_by(is_active=True).first()
    return render_template('main/about.html', model=model)
