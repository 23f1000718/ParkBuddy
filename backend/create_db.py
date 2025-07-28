from app import create_app, db
from models import Admin

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = Admin(username='admin')
    admin.set_password('ChangeMe123')  
    db.session.add(admin)
    db.session.commit()
    print("🗃  Database and tables created. Admin user seeded.")
