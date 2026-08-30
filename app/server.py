from flask import Flask, jsonify, request, send_from_directory
import logging
from app.generator import generate_password
from app.analyzer import analyze_password
from app.cracker_estimator import estimate_crack_time
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, static_folder='../static', static_url_path='/static')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = request.get_json()
        if not data or 'method' not in data:
            return jsonify({"error": "Ожидается JSON с полем 'method'"}), 400

        method = data.pop('method')
        password = generate_password(method, **data)

        return jsonify({
            "status": "success",
            "password": password
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({"error": "Ожидается JSON с полем 'password'"}), 400

        password = data['password']
        analysis = analyze_password(password)

        crack_estimate = estimate_crack_time(password, analysis)
        analysis["crack_time_display"] = crack_estimate["crack_times"]["offline_fast_hash"]["display"]
        analysis["crack_times"] = crack_estimate["crack_times"]

        return jsonify({
            "status": "success",
            "analysis": analysis
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/estimate', methods=['POST'])
def api_estimate():
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({"error": "Ожидается JSON с полем 'password'"}), 400

        password = data['password']
        analysis = analyze_password(password)
        estimate = estimate_crack_time(password, analysis)

        return jsonify({
            "status": "success",
            "estimate": estimate
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/full', methods=['POST'])
def api_full():
    try:
        data = request.get_json()
        if not data or 'method' not in data:
            return jsonify({"error": "Ожидается JSON с полем 'method'"}), 400

        method = data.pop('method')
        password = generate_password(method, **data)
        analysis = analyze_password(password)
        crack_estimate = estimate_crack_time(password, analysis)

        analysis["crack_time_display"] = crack_estimate["crack_times"]["offline_fast_hash"]["display"]
        analysis["crack_times"] = crack_estimate["crack_times"]

        return jsonify({
            "status": "success",
            "password": password,
            "analysis": analysis
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не найден"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500