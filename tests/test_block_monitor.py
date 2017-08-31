# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License
import pprint

from flask import url_for
from sqlalchemy import and_
from app.block_monitor import find_changed_wallets, alert_users
from app.manage_commands import find_or_create_user
from app.queries import get_latest_block, record_wallets
from app.networks import Networks
from app.local_settings import ETC_WALLET_ADDRESS, ETC_MIN_BLOCK
from app.models import Wallet


# TODO: Fix up these tests, they're crap
def test_find_changed_wallets():
    """See if we properly find wallets with a changed balance"""
    users = []
    lower_balance = find_or_create_user("lower_balance@test.com", "test")
    same_balance = find_or_create_user("same_balance@test.com", "test")
    higher_balance = find_or_create_user("higher_balance@test.com", "test")
    users.append(lower_balance)
    users.append(same_balance)
    users.append(higher_balance)

    latest_block = get_latest_block(Networks.ETC)
    changed_wallets = find_changed_wallets(users, latest_block)

    pprint.pprint(changed_wallets)

    assert lower_balance in changed_wallets.keys()
    assert same_balance not in changed_wallets.keys()
    assert higher_balance in changed_wallets.keys()


def test_alert_users():
    users = []
    lower_balance = find_or_create_user("lower_balance@test.com", "test")
    same_balance = find_or_create_user("same_balance@test.com", "test")
    higher_balance = find_or_create_user("higher_balance@test.com", "test")
    users.append(lower_balance)
    users.append(same_balance)
    users.append(higher_balance)

    latest_block = get_latest_block(Networks.ETC)
    changed_wallets = find_changed_wallets(users, latest_block)

    alert_users(changed_wallets)

    # TODO: Find something worth testing here
    #pprint.pprint(changed_wallets)    


def test_find_new_wallets():
    record_wallets(Networks.ETC, "0x006abDE097cbd31416A0D19533E32670e03A3294", 4370800, 4370850)

    new_subscriber = find_or_create_user("new_subscriber@test.com", "test")
    new_subscriber_wallet = Wallet.query.filter(Wallet.user_id == new_subscriber.id).first()

    assert new_subscriber_wallet is not None


def test_only_add_wallet_once_per_user():
    record_wallets(Networks.ETC, "0x006abDE097cbd31416A0D19533E32670e03A3294", 4370800, 4370850)
    record_wallets(Networks.ETC, "0x006abDE097cbd31416A0D19533E32670e03A3294", 4370800, 4370850)

    new_subscriber = find_or_create_user("new_subscriber@test.com", "test")
    new_subscriber_wallets = Wallet.query.filter(and_(Wallet.user_id == new_subscriber.id, Wallet.network == Networks.ETC, Wallet.address == "0x00baad25efdca6ae7d4e857dc8fde6fd7272a683"))

    assert new_subscriber_wallets.count() == 1
