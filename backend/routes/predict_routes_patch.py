"""
Patch to add to backend/routes/predict_routes.py
Add these lines inside the /api/predict endpoint, right after you get the result dict back.

After:
    result = predictor.predict(disease, feature_dict)
    return jsonify(result), 200

Replace with:
    result = predictor.predict(disease, feature_dict)

    # ── Save to DB (works for guests too) ──────────────────────────────
    try:
        from routes.history_routes import save_prediction
        save_prediction(
            disease     = disease,
            inputs_dict = data,
            risk_level  = result.get('risk_level', ''),
            probability = result.get('probability', 0.0) / 100
        )
    except Exception:
        pass   # never let DB errors break the prediction response

    return jsonify(result), 200
"""
