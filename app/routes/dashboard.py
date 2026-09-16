from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Device, Message, ActivityLog, Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/user')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    devices = Device.query.filter_by(user_id=current_user.id).order_by(Device.created_at.desc()).all()
    lost = [d for d in devices if d.is_lost]
    msgs = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.desc()).limit(10).all()
    notes = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    acts = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard/user_dashboard.html',
                         devices=devices, lost_devices=lost,
                         recent_messages=msgs, notifications=notes, recent_activity=acts)
