from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Device, Evidence, LocationHistory, Report
from app.forms import DeviceForm, EvidenceForm, ReportForm
import os, uuid
from werkzeug.utils import secure_filename

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register_device():
    form = DeviceForm()
    if form.validate_on_submit():
        device = Device(
            device_name=form.device_name.data,
            device_type=form.device_type.data,
            imei_number=form.imei_number.data,
            serial_number=form.serial_number.data,
            brand=form.brand.data, model=form.model.data, color=form.color.data,
            description=form.description.data,
            lost_date=form.lost_date.data, lost_location=form.lost_location.data,
            is_lost=form.is_lost.data, user_id=current_user.id)
        db.session.add(device)
        db.session.commit()
        flash('Device registered successfully!', 'success')
        return redirect(url_for('dashboard.user_dashboard'))
    return render_template('dashboard/register_device.html', form=form)

@devices_bp.route('/<int:device_id>/track')
@login_required
def track_device(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id and not current_user.is_admin:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    return render_template('dashboard/device_tracking.html', device=device)

@devices_bp.route('/<int:device_id>/update-location', methods=['POST'])
@login_required
def update_location(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    data = request.get_json() or {}
    lat, lng = data.get('latitude'), data.get('longitude')
    if lat is None or lng is None:
        return jsonify({'error': 'Missing coordinates'}), 400
    device.last_location_lat = lat
    device.last_location_lng = lng
    device.last_location_time = datetime.utcnow()
    db.session.add(LocationHistory(latitude=lat, longitude=lng, device_id=device.id))
    db.session.commit()
    return jsonify({'success': True})

@devices_bp.route('/<int:device_id>/evidence', methods=['GET', 'POST'])
@login_required
def upload_evidence(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id and not current_user.is_admin:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    form = EvidenceForm()
    if form.validate_on_submit():
        f = form.file.data
        ext = f.filename.rsplit('.', 1)[1].lower()
        fname = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
        f.save(path)
        db.session.add(Evidence(
            evidence_type=form.evidence_type.data,
            file_path=fname,
            original_name=secure_filename(f.filename),
            description=form.description.data,
            device_id=device.id, user_id=current_user.id))
        db.session.commit()
        flash('Evidence uploaded. Awaiting verification.', 'success')
        return redirect(url_for('devices.track_device', device_id=device.id))
    return render_template('dashboard/upload_evidence.html', form=form, device=device)

@devices_bp.route('/evidence/<int:evidence_id>/download')
@login_required
def download_evidence(evidence_id):
    ev = Evidence.query.get_or_404(evidence_id)
    if ev.user_id != current_user.id and not current_user.is_admin:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], ev.file_path,
                             as_attachment=True, download_name=ev.original_name or ev.file_path)

@devices_bp.route('/<int:device_id>/report', methods=['GET', 'POST'])
@login_required
def file_report(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard.user_dashboard'))
    form = ReportForm()
    if form.validate_on_submit():
        case = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.session.add(Report(
            case_number=case,
            description=form.description.data,
            police_station=form.police_station.data,
            police_report_number=form.police_report_number.data,
            officer_name=form.officer_name.data,
            officer_contact=form.officer_contact.data,
            device_id=device.id, user_id=current_user.id))
        db.session.commit()
        flash(f'Report filed! Case #: {case}', 'success')
        return redirect(url_for('devices.track_device', device_id=device.id))
    return render_template('dashboard/file_report.html', form=form, device=device)

@devices_bp.route('/<int:device_id>/toggle-lock', methods=['POST'])
@login_required
def toggle_lock(device_id):
    device = Device.query.get_or_404(device_id)
    if device.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403
    device.is_locked = not device.is_locked
    db.session.commit()
    flash('Device lock status updated.', 'success')
    return redirect(url_for('devices.track_device', device_id=device.id))
