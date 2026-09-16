from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps
import os
from app.models import (db, User, Device, Evidence, Message, Report,
                       ActivityLog, Notification, LocationHistory)

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.user_dashboard'))
        return f(*a, **kw)
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    pending_users = User.query.filter_by(is_verified=False, is_admin=False).count()
    unverified_evidence = Evidence.query.filter_by(is_verified=False).count()
    open_reports = Report.query.filter(Report.status.in_(['pending', 'investigating'])).count()
    return render_template('dashboard/admin_dashboard.html',
        total_users=User.query.count(),
        total_devices=Device.query.count(),
        total_evidences=Evidence.query.count(),
        total_messages=Message.query.count(),
        lost_devices=Device.query.filter_by(is_lost=True).count(),
        pending_users=pending_users,
        unverified_evidence=unverified_evidence,
        open_reports=open_reports,
        recent_users=User.query.order_by(User.created_at.desc()).limit(8).all(),
        recent_activities=ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(15).all())

# --------- USERS ---------
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    pending = User.query.filter_by(is_verified=False, is_admin=False).order_by(User.created_at.desc()).all()
    verified = User.query.filter_by(is_verified=True).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', pending=pending, users=verified)

@admin_bp.route('/user/<int:uid>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(uid):
    u = User.query.get_or_404(uid)
    u.is_verified = True
    u.approved_at = datetime.utcnow()
    u.approved_by = current_user.id
    db.session.add(Notification(user_id=u.id,
        title='Account approved!',
        message='Your account has been approved. You can now login and register devices.',
        type='success'))
    db.session.commit()
    flash(f'{u.username} approved.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/user/<int:uid>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(uid):
    u = User.query.get_or_404(uid)
    if u.is_admin:
        flash('Cannot delete admin.', 'danger')
        return redirect(url_for('admin.admin_users'))
    db.session.delete(u)
    db.session.commit()
    flash('User rejected and removed.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/user/<int:uid>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(uid):
    u = User.query.get_or_404(uid)
    if u.is_admin or u.id == current_user.id:
        flash('Cannot ban this user.', 'danger')
        return redirect(url_for('admin.admin_users'))
    u.is_banned = not u.is_banned
    u.ban_reason = request.form.get('reason', '') if u.is_banned else None
    db.session.commit()
    flash(f'{u.username} {"banned" if u.is_banned else "unbanned"}.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/user/<int:uid>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(uid):
    u = User.query.get_or_404(uid)
    u.is_admin = not u.is_admin
    u.is_verified = True
    db.session.commit()
    flash(f'{u.username} admin status updated.', 'success')
    return redirect(url_for('admin.admin_users'))

# --------- DEVICES ---------
@admin_bp.route('/devices')
@login_required
@admin_required
def admin_devices():
    devices = Device.query.order_by(Device.created_at.desc()).all()
    return render_template('admin/devices.html', devices=devices)

@admin_bp.route('/device/<int:did>')
@login_required
@admin_required
def admin_device_view(did):
    device = Device.query.get_or_404(did)
    return render_template('admin/device_view.html', device=device,
                         locations=LocationHistory.query.filter_by(device_id=did).order_by(LocationHistory.timestamp.desc()).all())

# --------- EVIDENCE ---------
@admin_bp.route('/evidence')
@login_required
@admin_required
def admin_evidence():
    pending = Evidence.query.filter_by(is_verified=False).order_by(Evidence.uploaded_at.desc()).all()
    verified = Evidence.query.filter_by(is_verified=True).order_by(Evidence.verified_at.desc()).all()
    return render_template('admin/evidence.html', pending=pending, verified=verified)

@admin_bp.route('/evidence/<int:eid>/verify', methods=['POST'])
@login_required
@admin_required
def verify_evidence(eid):
    e = Evidence.query.get_or_404(eid)
    e.is_verified = True
    e.verified_by = current_user.id
    e.verified_at = datetime.utcnow()
    e.admin_notes = request.form.get('admin_notes', '')
    db.session.add(Notification(user_id=e.user_id,
        title='Evidence verified',
        message=f'Your evidence for {e.device.device_name} was verified.',
        type='success'))
    db.session.commit()
    flash('Evidence verified.', 'success')
    return redirect(url_for('admin.admin_evidence'))

@admin_bp.route('/evidence/<int:eid>/reject', methods=['POST'])
@login_required
@admin_required
def reject_evidence(eid):
    e = Evidence.query.get_or_404(eid)
    e.is_verified = False
    e.admin_notes = request.form.get('admin_notes', '')
    db.session.commit()
    flash('Evidence rejected.', 'warning')
    return redirect(url_for('admin.admin_evidence'))

@admin_bp.route('/evidence/<int:eid>/download')
@login_required
@admin_required
def download_evidence(eid):
    e = Evidence.query.get_or_404(eid)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], e.file_path,
                             as_attachment=True, download_name=e.original_name or e.file_path)

# --------- REPORTS ---------
@admin_bp.route('/reports')
@login_required
@admin_required
def admin_reports():
    return render_template('admin/reports.html',
                         reports=Report.query.order_by(Report.created_at.desc()).all())

@admin_bp.route('/report/<int:rid>/update', methods=['POST'])
@login_required
@admin_required
def update_report(rid):
    r = Report.query.get_or_404(rid)
    r.status = request.form.get('status', r.status)
    r.admin_notes = request.form.get('admin_notes', r.admin_notes)
    r.assigned_admin = current_user.id
    if r.status == 'resolved':
        r.resolved_at = datetime.utcnow()
    db.session.commit()
    db.session.add(Notification(user_id=r.user_id,
        title=f'Report {r.case_number} updated',
        message=f'Status: {r.status}', type='info'))
    db.session.commit()
    flash('Report updated.', 'success')
    return redirect(url_for('admin.admin_reports'))

# --------- MESSAGES ---------
@admin_bp.route('/messages')
@login_required
@admin_required
def admin_messages():
    return render_template('admin/messages.html',
                         messages=Message.query.order_by(Message.timestamp.desc()).all())

# --------- ACTIVITY ---------
@admin_bp.route('/activity')
@login_required
@admin_required
def admin_activity():
    return render_template('admin/activity.html',
                         activities=ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(200).all())
