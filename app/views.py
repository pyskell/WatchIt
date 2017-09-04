# Copyright 2014 SolidBuilds.com. All rights reserved
# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required
from app import app, db
from app.models import UserProfileForm, UserWalletsForm, Wallet
from app.local_settings import ETC_WALLET_ADDRESS, EMAIL_TIME_LIMIT

# The Home page is accessible to anyone
@app.route("/")
def home_page():
    return render_template("pages/home_page.html")


# The User page is accessible to authenticated users (users that have logged in)
@app.route("/help")
@login_required  # Limits access to authenticated users
def help_page():
    return render_template("pages/help_page.html", 
                            etc_wallet_address = ETC_WALLET_ADDRESS,
                            email_time_limit = EMAIL_TIME_LIMIT)


# The Admin page is accessible to users with the "admin" role
#@app.route("/admin")
#@roles_accepted("admin")  # Limits access to users with the "admin" role
#def admin_page():
#    return render_template("pages/admin_page.html")


@app.route("/pages/profile", methods=["GET", "POST"])
@login_required
def user_profile_page():
    # Initialize form
    #form = UserProfileForm(request.form, current_user)
    form = UserProfileForm(request.form)

    # Process valid POST
    if request.method == "POST" and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for("user_profile_page"))

    # Process GET or invalid POST
    return render_template("pages/user_profile_page.html",
                           form=form)

@app.route("/pages/wallets", methods=["GET", "POST"])
@login_required
def user_wallets_page():
    #form = UserWalletsForm(request.form, current_user)
    form = UserWalletsForm(request.form)

    if request.method == "POST" and form.validate():
        form.populate_obj(current_user)

        wallet_ids = request.form.getlist("do_delete")
        # Filter the current_user"s wallets to those that were selected for deletion
        current_user.wallets.filter(Wallet.id.in_(wallet_ids)).delete(synchronize_session="fetch")

        # Save user_profile
        db.session.commit()      

        return redirect(url_for("user_wallets_page"))

    return render_template("pages/user_wallets_page.html",
                           form=form)
