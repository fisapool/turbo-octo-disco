from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..core.main_controller import MainController
import os

api = Blueprint('api', __name__)
controller = MainController()

@api.route('/start', methods=['POST'])
@login_required
def start_monitoring():
    try:
        controller.start()
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/stop', methods=['POST'])
@login_required
def stop_monitoring():
    try:
        controller.stop()
        return jsonify({'status': 'success', 'message': 'Monitoring stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/metrics', methods=['GET'])
@login_required
def get_metrics():
    try:
        metrics = controller.get_current_metrics()
        return jsonify({'status': 'success', 'data': metrics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/activity', methods=['GET'])
@login_required
def get_activity():
    try:
        limit = request.args.get('limit', default=100, type=int)
        activity_data = controller.activity_tracker.get_recent_events(limit=limit)
        return jsonify({'status': 'success', 'data': activity_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/webcam', methods=['GET'])
@login_required
def get_webcam_data():
    try:
        limit = request.args.get('limit', default=10, type=int)
        webcam_data = controller.webcam_recorder.get_recent_analysis(limit=limit)
        return jsonify({'status': 'success', 'data': webcam_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api.route('/status', methods=['GET'])
@login_required
def get_status():
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'is_running': controller.is_running,
                'last_analysis_time': controller.last_analysis_time,
                'activity_tracker_running': controller.activity_tracker.is_running,
                'webcam_recorder_running': controller.webcam_recorder.is_running
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 