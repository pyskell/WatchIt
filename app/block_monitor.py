# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License

from collections import namedtuple
from datetime import datetime
from flask_mail import Message
from celery import Celery

from app.networks import Networks
from app.local_settings import BLOCK_CHECK_DELAY, CELERY_BROKER_URL, ETC_WALLET_ADDRESS, ETC_MIN_BLOCK, ETC_RPC_ADDRESS
from app.manage_commands import find_or_create_network
from app.models import User, Wallet
from app.local_settings import MAIL_DEFAULT_SENDER_EMAIL, MAIL_DEFAULT_SENDER
from app.nodes import Parity
from app import db, app, mail


def alert_users(changed_wallets):
    for user, wallet_list in changed_wallets.items():
        message = "Please note that emails are only sent periodically, every {0} minutes \n".format(user.email_limit.seconds / 60)
        message += "The following wallets have had their balances changed: \n"

        for wallet in wallet_list:
            direction = "decreased"
            if wallet.new_balance > wallet.previous_balance:
                direction = "increased"
            message += "The wallet at address {0} has had its balance {1} from {2} to {3}. \n".format(wallet.address, direction, wallet.previous_balance/10**18, wallet.new_balance/10**18)

        send_email(user.email, "Wallet balance has changed", message)
        user.last_emailed_at = time

    db.session.commit()


def send_email(email_address, subject, message):
    print(" Email: {0}\n Subject: {1}\n Message: {2}\n".format(email_address, subject, message))
    msg = Message(subject, [email_address], message, sender=(MAIL_DEFAULT_SENDER, MAIL_DEFAULT_SENDER_EMAIL))
    mail.send(msg)


def make_celery(app):
    celery = Celery(app.import_name, 
                    broker=CELERY_BROKER_URL)
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    
    return celery


celery = make_celery(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Schedule our block checking
    sender.add_periodic_task(BLOCK_CHECK_DELAY, update.s(), name="find new wallets and check blocks every {0} seconds".format(BLOCK_CHECK_DELAY))


@celery.task()
def update():
    changed_wallets = {}
    etc_wallets = update_etc()
    changed_wallets.update(etc_wallets)

    alert_users(changed_wallets)


def update_etc():
    etc_node = Parity(Networks.ETC, ETC_RPC_ADDRESS)
    latest_block = etc_node.get_latest_etc_block()

    etc_users = db.session.query(User).filter(User.wallets.any(Wallet.network == Networks.ETC))
    changed_wallets = etc_node.find_changed_wallets(etc_users, latest_block)

    etc_rpcinfo = find_or_create_network(Networks.ETC, latest_block, ETC_WALLET_ADDRESS)
    if latest_block > etc_rpcinfo.last_block:
        etc_node.record_wallets(Networks.ETC, etc_rpcinfo.address, etc_rpcinfo.last_block + 1, latest_block)
    
        etc_rpcinfo.last_block = latest_block

        db.session.commit()

    return changed_wallets