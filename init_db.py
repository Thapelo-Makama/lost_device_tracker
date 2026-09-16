from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created")
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@lostdevice.com',
            full_name='System Administrator',
            phone_number='+27818795563',
            is_admin=True, is_active=True, is_verified=True)
        admin.set_password('Admin@2024!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: admin / Admin@2024!")
    else:
        print("ℹ️  Admin already exists")
    print("✅ Done!")
