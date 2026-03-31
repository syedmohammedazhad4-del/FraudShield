import json
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.extensions import db
from app.models import Prediction, ModelMetadata
from app.forms import PredictionForm
from app.field_mappings import WIZARD_STEPS, FIELD_CHOICES
from app.ml.predictor import predict
from app.ml.metrics import get_active_model_metrics


@api_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict_view():
    form = PredictionForm()

    if form.validate_on_submit():
        # Collect human-readable form data
        form_data = {}
        for step in WIZARD_STEPS:
            for field_name in step['fields']:
                form_data[field_name] = request.form.get(field_name, '')

        try:
            # Extract policy number (not fed to model, just for tracking)
            policy_number = form_data.pop('PolicyNumber', '')

            result = predict(form_data)

            model = ModelMetadata.query.filter_by(is_active=True).first()
            prediction = Prediction(
                user_id=current_user.id,
                policy_number=policy_number,
                prediction_result=result['result'],
                confidence_score=result['confidence'],
                input_data_json=json.dumps(form_data),
                encoded_data_json=json.dumps(result['encoded_data']),
                model_version=model.version if model else 'unknown'
            )
            db.session.add(prediction)
            db.session.commit()

            return redirect(url_for('api.result_view', id=prediction.id))

        except Exception as e:
            flash(f'Prediction failed: Please check your inputs.', 'danger')

    return render_template('predict/wizard.html', form=form,
                           wizard_steps=WIZARD_STEPS,
                           field_choices=FIELD_CHOICES)


@api_bp.route('/result/<int:id>')
@login_required
def result_view(id):
    prediction = Prediction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    input_data = json.loads(prediction.input_data_json)
    return render_template('predict/result.html', prediction=prediction,
                           input_data=input_data, field_choices=FIELD_CHOICES)


@api_bp.route('/performance')
@login_required
def performance():
    metrics = get_active_model_metrics()
    return render_template('predict/performance.html', metrics=metrics)


@api_bp.route('/api/metrics')
@login_required
def api_metrics():
    metrics = get_active_model_metrics()
    if metrics:
        return jsonify(metrics)
    return jsonify({'error': 'No active model'}), 404
