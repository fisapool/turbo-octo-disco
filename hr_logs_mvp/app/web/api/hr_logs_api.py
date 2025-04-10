from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models.hr_log import HRLog, db
from flask_login import login_required, current_user

hr_logs_api = Blueprint('hr_logs_api', __name__, url_prefix='/api/hr_logs')

@hr_logs_api.route('/', methods=['GET'])
@login_required
def list_logs():
    try:
        # If user is not admin, only show their logs
        if current_user.role != 'admin':
            logs = HRLog.query.filter_by(user_id=current_user.id).all()
        else:
            logs = HRLog.query.all()
        
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_logs_api.route('/', methods=['POST'])
@login_required
def create_log():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        required_fields = ['log_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create new log
        new_log = HRLog(
            user_id=current_user.id,
            log_type=data['log_type'],
            description=data['description'],
            status='pending',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(new_log)
        db.session.commit()
        
        return jsonify(new_log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@hr_logs_api.route('/<int:log_id>', methods=['PUT'])
@login_required
def update_log(log_id):
    try:
        log = HRLog.query.get_or_404(log_id)
        
        # Check if user has permission to update this log
        if current_user.role != 'admin' and log.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Update log fields
        for key, value in data.items():
            if hasattr(log, key) and key not in ['id', 'user_id', 'timestamp']:
                setattr(log, key, value)

        db.session.commit()
        return jsonify(log.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@hr_logs_api.route('/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    try:
        log = HRLog.query.get_or_404(log_id)
        
        # Check if user has permission to delete this log
        if current_user.role != 'admin' and log.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

        db.session.delete(log)
        db.session.commit()
        return jsonify({"message": "Log deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@hr_logs_api.route('/stats', methods=['GET'])
@login_required
def get_stats():
    try:
        # Get basic statistics about logs
        total_logs = HRLog.query.count()
        pending_logs = HRLog.query.filter_by(status='pending').count()
        approved_logs = HRLog.query.filter_by(status='approved').count()
        rejected_logs = HRLog.query.filter_by(status='rejected').count()

        # Get logs by type
        log_types = db.session.query(
            HRLog.log_type,
            db.func.count(HRLog.id)
        ).group_by(HRLog.log_type).all()

        stats = {
            "total_logs": total_logs,
            "pending_logs": pending_logs,
            "approved_logs": approved_logs,
            "rejected_logs": rejected_logs,
            "logs_by_type": {log_type: count for log_type, count in log_types}
        }

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 