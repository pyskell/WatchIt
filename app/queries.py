# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License

import requests
import json

from app.networks import Networks
from app.models import User
from app.local_settings import ETC_RPC_ADDRESS
from app import db
from app.manage_commands import create_wallet, find_wallet


# TODO: See if using filters works better/faster
# TODO: Turn this into a class for handling more networks


def get_latest_etc_block():
    return get_latest_block(Networks.ETC)


def etc_query(method, params=[]):
    headers = {"content-type": "application/json"}
    payload = {
        "method":method,
        "params":params,
        "id":1,
        "jsonrpc":"2.0"
    }
    response = requests.post(ETC_RPC_ADDRESS, data=json.dumps(payload), headers=headers).json()

    if "error" in response:
        raise ChildProcessError("ETC node reported an error", response["error"])

    return response


def get_latest_block(network):
    if network == Networks.ETC:
        response = etc_query("eth_blockNumber")
        latest_block = int(response["result"], 0)
        
        return latest_block

    return None


# We have to get the latest balance here.
# Getting earlier balances requires keeping the entire trie state
# which takes up too much storage for a modest node
# TODO: Revisit if we end up using a better node.
def get_latest_balance(network, address):
    if network == Networks.ETC:
        response = etc_query("eth_getBalance", [address, "latest"])
        balance = int(response["result"], 0)
        
        return balance

    return None


def get_transaction_hashes(network, address, from_block, to_block=None):
    if network == Networks.ETC:
        latest_block = to_block
        if latest_block is None:
            latest_block = get_latest_block(Networks.ETC)

        for block in range(from_block, latest_block+1):
            response = etc_query("eth_getBlockByNumber", [hex(block), False]) 
            transaction_hashes = response["result"]["transactions"]

            for transaction_hash in transaction_hashes:
                yield transaction_hash


def get_transaction(network, transaction_hash):
    if network == Networks.ETC:
        return etc_query("eth_getTransactionByHash", [transaction_hash])["result"]


def record_wallets(network, address, from_block, to_block="latest"):
    if isinstance(from_block, int):
        from_block = hex(from_block)

    if isinstance(to_block, int):
        to_block = hex(to_block)

    results = etc_query("trace_filter", [{  
                        "fromBlock": from_block,
                         "toBlock": to_block,
                         "toAddress": [address]}])["result"]

    for result in results:

        # We can't do anything if there's no input data with a UUID
        # Also, python throws an error when parsing "0x" to an int
        # That's why we're checking against the string representation
        # This may have compatibility issues with nodes other than parity, haven't checked
        if result["action"]["input"] == "0x":
            continue
   
        user_address = result["action"]["from"]
        user = User.query.filter(User.public_uuid == result["action"]["input"][2::]).first()
        wallet = find_wallet(user, Networks.ETC, user_address)

        if user is not None and wallet is None:
            balance = get_latest_balance(Networks.ETC, user_address)
            wallet = create_wallet(user, Networks.ETC, user_address, balance)

            db.session.add(wallet)

    db.session.commit()

