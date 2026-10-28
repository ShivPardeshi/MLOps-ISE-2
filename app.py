"""
Student Performance Prediction Web Application (student-app)
DevOps & MLOps CI/CD Lifecycle Implementation
"""

import os
import logging
from flask import Flask, render_template, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Model path and loading
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "student_performance_model.joblib")
model_pipeline = None

try:
    if os.path.exists(MODEL_PATH):
        import joblib
        model_pipeline = joblib.load(MODEL_PATH)
        logger.info("Successfully loaded ML pipeline from %s", MODEL_PATH)
    else:
        logger.warning("Model file not found at %s. Fallback predictor will be used.", MODEL_PATH)
except Exception as e:
    logger.error("Failed to load model file (%s). Using fallback heuristic: %s", MODEL_PATH, e)


def predict_grade(data: dict) -> float:
    """Predict final grade (0-20 scale) given student features."""
    import pandas as pd

    # Default baseline schema
    baseline = {
        'school': 'GP', 'sex': 'F', 'age': 17, 'address': 'U', 'famsize': 'GT3', 'Pstatus': 'T',
        'Medu': 3, 'Fedu': 3, 'Mjob': 'other', 'Fjob': 'other', 'reason': 'course',
        'guardian': 'mother', 'traveltime': 1, 'studytime': 2, 'failures': 0,
        'schoolsup': 'no', 'famsup': 'yes', 'paid': 'no', 'activities': 'yes',
        'nursery': 'yes', 'higher': 'yes', 'internet': 'yes', 'romantic': 'no',
        'famrel': 4, 'freetime': 3, 'goout': 3, 'Dalc': 1, 'Walc': 1, 'health': 4, 'absences': 4
    }

    # Update with incoming data and type conversion
    for key, val in data.items():
        if key in baseline:
            if isinstance(baseline[key], int):
                try:
                    baseline[key] = int(val)
                except (ValueError, TypeError):
                    pass
            else:
                baseline[key] = str(val)

    if model_pipeline is not None:
        try:
            df = pd.DataFrame([baseline])
            pred = model_pipeline.predict(df)[0]
            return float(max(0.0, min(20.0, round(pred, 2))))
        except Exception as ex:
            logger.warning("Pipeline inference failed (%s). Falling back to calibrated model.", ex)

    # Calibrated fallback based on dataset coefficients
    score = 11.5
    score += (baseline['studytime'] - 2) * 1.2
    score -= baseline['failures'] * 1.8
    score += (baseline['Medu'] - 2) * 0.4
    score += (baseline['Fedu'] - 2) * 0.3
    score += 0.8 if baseline['higher'] == 'yes' else -1.2
    score += 0.5 if baseline['internet'] == 'yes' else -0.5
    score -= (baseline['absences'] / 10.0) * 0.9
    score -= (baseline['Dalc'] - 1) * 0.5
    score -= (baseline['Walc'] - 1) * 0.4
    return float(max(0.0, min(20.0, round(score, 2))))


def get_performance_tier(grade: float) -> dict:
    """Categorize grade according to Portuguese secondary education scale."""
    if grade >= 16:
        return {"badge": "Excellent", "color": "tier-excellent", "desc": "Outstanding academic performance."}
    elif grade >= 14:
        return {"badge": "Good", "color": "tier-good", "desc": "Strong understanding with consistent results."}
    elif grade >= 10:
        return {"badge": "Satisfactory (Pass)", "color": "tier-pass", "desc": "Meets core course requirements."}
    else:
        return {"badge": "Needs Support (At-Risk)", "color": "tier-risk", "desc": "Targeted academic intervention advised."}


@app.route("/", methods=["GET"])
def home():
    """Render home prediction page."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Kubernetes/Docker/Jenkins healthcheck probe."""
    return jsonify({
        "status": "healthy",
        "service": "student-app",
        "model_loaded": model_pipeline is not None,
        "version": "1.0.0"
    }), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Prediction API handling both JSON payloads and web form submissions."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    try:
        predicted_grade = predict_grade(data)
        tier = get_performance_tier(predicted_grade)

        response_data = {
            "status": "success",
            "predicted_grade": predicted_grade,
            "max_grade": 20.0,
            "percentage": round((predicted_grade / 20.0) * 100, 1),
            "tier": tier["badge"],
            "tier_description": tier["desc"],
            "inputs": {
                "studytime": data.get("studytime", 2),
                "failures": data.get("failures", 0),
                "absences": data.get("absences", 4),
                "higher": data.get("higher", "yes"),
                "internet": data.get("internet", "yes")
            }
        }

        if request.is_json:
            return jsonify(response_data), 200

        return render_template(
            "index.html",
            result=response_data,
            tier_class=tier["color"],
            form_data=data
        )

    except Exception as e:
        logger.exception("Error processing prediction: %s", e)
        if request.is_json:
            return jsonify({"status": "error", "message": str(e)}), 400
        return render_template("index.html", error=f"Prediction error: {str(e)}", form_data=data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
