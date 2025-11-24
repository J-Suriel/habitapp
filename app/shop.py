from flask import Blueprint, render_template
from flask_login import login_required

shop = Blueprint("shop", __name__)

@shop.route("/shop")
@login_required
def shop_home():
    return render_template("shop.html")
