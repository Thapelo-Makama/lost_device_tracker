from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Message, User
from app.forms import MessageForm

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/')
@login_required
def messages():
    msgs = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    for m in msgs:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()
    return render_template('messages.html', messages=msgs)

@messages_bp.route('/send', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    form.recipient_id.choices = [(u.id, u.username) for u in
                                  User.query.filter(User.id != current_user.id).all()]
    if form.validate_on_submit():
        db.session.add(Message(
            subject=form.subject.data,
            content=form.content.data,
            is_private=form.is_private.data,
            sender_id=current_user.id,
            recipient_id=form.recipient_id.data))
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('messages.messages'))
    return render_template('send_message.html', form=form)
