from flask import Flask, request, jsonify
from analysis.technical_analyzer import TechnicalAnalyzer
from analysis.strategies.technical_strategy import TechnicalAnalysisStrategy
from analysis.strategies.context import AnalysisContext
import logging
import numpy as np
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TechnicalAnalysisService")

# Initialize analyzer and strategy
analyzer = TechnicalAnalyzer()
strategy = TechnicalAnalysisStrategy(analyzer, logger)
context = AnalysisContext(strategy)

# Initialize Flask
app = Flask(__name__)
CORS(app)
def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types for JSON serialization, including NaN/inf."""
    import math
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        # Convert pandas/numpy NaN that slipped through
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
