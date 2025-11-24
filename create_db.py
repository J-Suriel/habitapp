from app import create_app, db
from app import models  # makes sure models are registered

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Database and tables created!")
