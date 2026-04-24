import os
from app import create_app
from app.models import db, User, Tenant

app = create_app()

with app.app_context():
    db.create_all()
    print("Database ready!")

    if not User.query.filter_by(is_masteradmin=True).first():
        admin = User(
            tenant_id      = None,
            email          = 'masteradmin@pos.com',
            role           = 'masteradmin',
            is_masteradmin = True
        )
        admin.set_password('admin@123')
        db.session.add(admin)
        db.session.commit()
        print("=" * 40)
        print("MasterAdmin created!")
        print("Email   : masteradmin@pos.com")
        print("Password: admin@123")
        print("=" * 40)

if __name__ == '__main__':
    app.run(debug=True)