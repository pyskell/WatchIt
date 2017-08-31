# This file contains pytest "fixtures".
# If a test functions specifies the name of a fixture function as a parameter,
# the fixture function is called and its result is passed to the test function.
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import pytest
from app import app as the_app, db as the_db, init_app
#from app.init_app import init_app
from app.manage_commands import init_db, create_user, create_wallet
#from app.models import User, Wallet
from app.networks import Networks


# Initialize the Flask-App with test-specific settings
#init_app(the_app, dict(
#    TESTING=True,  # Propagate exceptions
#    LOGIN_DISABLED=False,  # Enable @register_required
#    MAIL_SUPPRESS_SEND=True,  # Disable Flask-Mail send
#    SERVER_NAME="localhost",  # Enable url_for() without request context
#    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",  # In-memory SQLite DB
#    WTF_CSRF_ENABLED=False,  # Disable CSRF form validation
#))

the_app.config.update(dict(
    TESTING=True,  # Propagate exceptions
    LOGIN_DISABLED=False,  # Enable @register_required
    MAIL_SUPPRESS_SEND=True,  # Disable Flask-Mail send
    SERVER_NAME="localhost",  # Enable url_for() without request context
    SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",  # In-memory SQLite DB
    WTF_CSRF_ENABLED=False,  # Disable CSRF form validation
))

# Setup an application context (since the tests run outside of the webserver context)
the_app.app_context().push()

init_db()

@pytest.fixture(scope="session")
def app():
    return the_app


@pytest.fixture(scope="session")
def db():
    """
    Initializes and returns a SQLAlchemy DB object
    """
    return the_db


@pytest.fixture(scope="session")
def populate_db():
    # Zero
    lower_balance = create_user("lower_balance@test.com", "test")
    lower_wallet = create_wallet(lower_balance, Networks.ETC, "0x00503ECcf0f2430f6244951804c40d898d2470Ce", 100)

    # Zero
    same_balance = create_user("same_balance@test.com", "test")
    same_wallet = create_wallet(same_balance, Networks.ETC, "0x003F31AB5ecEE888C2232bb77A47466E42590d33", 0)

    # Non-zero
    higher_balance = create_user("higher_balance@test.com", "test")
    higher_balance = create_wallet(higher_balance, Networks.ETC, "0x00111741a294BcD5981c451208ccEad59Da4c0E3", 0)

    # New-subscriber
    new_subscriber = create_user("new_subscriber@test.com", "test")
    new_subscriber.public_uuid = "b3cd9bfb119949da96cadf23b5e83090"

# Populate the database with test Users and Wallets
populate_db()