from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Reward, Redemption
from . import db

shop = Blueprint("shop", __name__)

@shop.route("/shop")
@login_required
def shop_home():
    rewards = Reward.query.order_by(Reward.cost.asc()).all()
    history = Redemption.query.filter_by(user_id=current_user.id)\
                              .order_by(Redemption.redeemed_at.desc())\
                              .all()

    return render_template(
        "shop.html",
        rewards=rewards,
        history=history,
        user=current_user
    )

@shop.route("/shop/redeem/<int:reward_id>", methods=["POST"])
@login_required
def redeem_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)

    if current_user.currency < reward.cost:
        flash("Not enough coins for that reward!", "error")
        return redirect(url_for("shop.shop_home"))

    current_user.currency -= reward.cost
    redemption = Redemption(user_id=current_user.id, reward_id=reward.id)

    db.session.add(redemption)
    db.session.commit()

    flash(f"Redeemed: {reward.name} 🎉", "success")
    return redirect(url_for("shop.shop_home"))

# ---------- Reward Management (Create / Edit / Delete) ----------

@shop.route("/shop/manage", methods=["GET", "POST"])
@login_required
def manage_rewards():
    if request.method == "POST":
        name = request.form.get("name")
        cost = request.form.get("cost", type=int)
        description = request.form.get("description", "")

        if not name or cost is None:
            flash("Name and cost are required.", "error")
            return redirect(url_for("shop.manage_rewards"))

        reward = Reward(name=name, cost=cost, description=description)
        db.session.add(reward)
        db.session.commit()
        flash("Reward created.", "success")
        return redirect(url_for("shop.manage_rewards"))

    rewards = Reward.query.order_by(Reward.cost.asc()).all()
    return render_template("manage_rewards.html", rewards=rewards)

@shop.route("/shop/manage/<int:reward_id>/edit", methods=["GET", "POST"])
@login_required
def edit_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)

    if request.method == "POST":
        reward.name = request.form.get("name")
        reward.cost = request.form.get("cost", type=int)
        reward.description = request.form.get("description", "")
        db.session.commit()
        flash("Reward updated.", "success")
        return redirect(url_for("shop.manage_rewards"))

    return render_template("edit_reward.html", reward=reward)

@shop.route("/shop/manage/<int:reward_id>/delete", methods=["POST"])
@login_required
def delete_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)

    db.session.delete(reward)
    db.session.commit()
    flash("Reward deleted.", "success")
    return redirect(url_for("shop.manage_rewards"))
