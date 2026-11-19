from flask import Blueprint, request, jsonify
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.predictor import predict

predict_bp = Blueprint('predict', __name__)


@predict_bp.route('/api/predict', methods=['POST'])
def predict_route():
    data = request.get_json(force=True)

    disease = data.get('disease', '').strip().lower()
    if not disease:
        return jsonify({'error': 'disease field is required'}), 400

    feature_dict = {k: v for k, v in data.items() if k != 'disease'}

    try:
        result = predict(disease, feature_dict)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Prediction failed', 'details': str(e)}), 500