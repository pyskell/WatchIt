# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime
import uuid

from sqlalchemy import and_
from app import app, db, manager
from app.models import User, Role, RPCInfo, Wallet
from app.networks import Networks
from app.local_settings import ETC_MIN_BLOCK, ETC_WALLET_ADDRESS

@manager.command
def init_db():
    """ Initialize the database."""
    # Create all tables
    db.create_all()
    # Add all Users
    add_users()
    add_chain_info()


def add_chain_info():
    """ Add the specific info needed for the various blockchains """
    etc = find_or_create_network(Networks.ETC, ETC_MIN_BLOCK, ETC_WALLET_ADDRESS)

    db.session.commit()


def add_users():
    """ Create users when app starts """

    # Adding roles
    admin_role = find_or_create_role("admin", u"Admin")

    # Save to DB
    db.session.commit()


def find_network(network):
    return RPCInfo.query.filter(RPCInfo.id == network).first()


# TODO: Redo this find or create stuff. I don't like it much.
# Should be separate find and create functions.

def find_or_create_network(network, last_block, address):
    entry = find_network(network)

    if not entry:
        entry = RPCInfo(id = network,
                        last_block = last_block,
                        address = address)
        db.session.add(entry)

    db.session.commit()
    return entry


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    db.session.commit()
    return role


def create_user(email, password, role=None):
    user = User(email=email,
                public_uuid=str(uuid.uuid4().hex),
                password=app.user_manager.hash_password(password),
                active=True,
                confirmed_at=datetime.datetime.utcnow())
    if role:
        user.roles.append(role)
    db.session.add(user)
    db.session.commit()
    return user


def find_or_create_user(email, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = create_user(email, password, role)
    return user


def find_wallet(user, network, address):
    return Wallet.query.filter(and_(Wallet.user_id == user.id, Wallet.network == network, Wallet.address == address)).first()

def create_wallet(user, network, address, balance=None):
    wallet = Wallet(user_id=user.id,
                    network=network,
                    address=address)
    if balance:
        wallet.balance = balance

    db.session.add(wallet)
    db.session.commit()
    return wallet
