# Copyright 2014 SolidBuilds.com. All rights reserved
# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License
#
# Authors: Ling Thio <ling.thio@gmail.com>

import uuid
import datetime

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from wtforms import SubmitField
from app.local_settings import ETC_MIN_BLOCK, EMAIL_TIME_LIMIT
from app.networks import Networks
from app import db


def create_uuid():
    return uuid.uuid4().hex


def default_last_emailed_time():
    return datetime.datetime.now() - EMAIL_TIME_LIMIT


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u"", unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default="")
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default="")
    active = db.Column(db.Boolean(), nullable=False, server_default="0")

    # User information
    active = db.Column("is_active", db.Boolean(), nullable=False, server_default="0")
    public_uuid = db.Column(db.String(32), nullable=True, unique=True, default=create_uuid)
    email_limit = db.Column(db.Interval(), nullable=False, default=EMAIL_TIME_LIMIT)
    last_emailed_at = db.Column(db.DateTime(), default=default_last_emailed_time)

    # TODO: Change this to its own table of Network, Last_Block
    last_etc_block = db.Column(db.Integer(), default=ETC_MIN_BLOCK)

    # Relationships
    roles = db.relationship("Role", secondary="users_roles",
                            backref=db.backref("users", lazy="dynamic"))
    wallets = db.relationship("Wallet", backref="wallets", lazy="dynamic")

# Define the Role data model
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u"", unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u"")  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = "users_roles"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    role_id = db.Column(db.Integer(), db.ForeignKey("roles.id", ondelete="CASCADE"))

class Wallet(db.Model):
    __tablename__ = "wallets"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id", ondelete="CASCADE"))
    address = db.Column(db.String(255))
    network = db.Column(db.Enum(Networks))
    balance = db.Column(db.BigInteger(), default=0)

class RPCInfo(db.Model):
    __tablename__ = "rpcinfo"
    id = db.Column(db.Enum(Networks), primary_key=True)
    last_block = db.Column(db.Integer())
    address = db.Column(db.String(255))

# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    pass


# Define the User profile form
class UserProfileForm(FlaskForm):
    submit = SubmitField("Save")

class UserWalletsForm(FlaskForm):
    delete = SubmitField("Delete")
