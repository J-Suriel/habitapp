from app import create_app, db
from app.models import Reward

app = create_app()

with app.app_context():
    db.create_all()

    if Reward.query.count() == 0:
        rewards = [
            Reward(name="1 hour Netflix / Games", cost=30, description="Enjoy 1 guilt-free hour."),
            Reward(name="Snack Break", cost=10, description="Pick a favorite snack."),
            Reward(name="30 min Nap", cost=15, description="Recharge time."),
        ]
        db.session.add_all(rewards)
        db.session.commit()

    print("✅ Database initialized!")
