# Copyright (c) 2017 Pyskell BSD 2-clause "Simplified" License
import requests
import json
from collections import namedtuple
from datetime import datetime

from app.networks import Networks
from app.models import User, Wallet
from app import db
from app.manage_commands import create_wallet, find_wallet


class Node(object):
    
    def __init__(self, network, node_address, **kwargs):
        self.network = network
        self.node_address = node_address
        self.ChangedWallet = namedtuple("ChangedWallet", "network address previous_balance new_balance")
        return super().__init__(**kwargs)


    def query(self, method, params=[]):
        raise NotImplementedError()


    def get_latest_block(self):
        raise NotImplementedError()


    # We have to get the latest balance here.
    # Getting earlier balances requires keeping the entire trie state
    # which takes up too much storage for a modest node
    # TODO: Revisit if we end up using a better node.
    def get_latest_balance(self, address):
        raise NotImplementedError()


    def get_transaction_hashes(self, address, from_block, to_block):
        raise NotImplementedError()


    def get_transaction(self, transaction_hash):
        raise NotImplementedError()


    def find_changed_wallets(self, users, from_block):
        raise NotImplementedError()


    def record_wallets(self, address, from_block, to_block):
        raise NotImplementedError()


# TODO: See if using filters works better/faster
class Parity(Node):

    def __init__(self, network, node_address, **kwargs):
        return super().__init__(network, node_address, **kwargs)


    def query(self, method, params=[]):
        headers = {"content-type": "application/json"}
        payload = {
            "method":method,
            "params":params,
            "id":1,
            "jsonrpc":"2.0"
        }
        response = requests.post(self.node_address, data=json.dumps(payload), headers=headers).json()

        if "error" in response:
            raise ChildProcessError("Parity node reported an error", response["error"])

        return response


    def get_latest_block(self):
        response = self.query("eth_blockNumber")
        latest_block = int(response["result"], 0)
        
        return latest_block


    # We have to get the latest balance here.
    # Getting earlier balances requires keeping the entire trie state
    # which takes up too much storage for a modest node
    # TODO: Revisit if we end up using a better node.
    def get_latest_balance(self, address):
        response = self.query("eth_getBalance", [address, "latest"])
        balance = int(response["result"], 0)
        
        return balance


    # TODO: Remove "address" argument and adjust latest_block so it's not latest_block+1
    def get_transaction_hashes(self, address, from_block, to_block=None):
        latest_block = to_block
        if latest_block is None:
            latest_block = get_latest_block(self.network)

        for block in range(from_block, latest_block+1):
            response = self.query("eth_getBlockByNumber", [hex(block), False]) 
            transaction_hashes = response["result"]["transactions"]

            for transaction_hash in transaction_hashes:
                yield transaction_hash


    def get_transaction(self, transaction_hash):
        return self.query("eth_getTransactionByHash", [transaction_hash])["result"]


    def find_changed_wallets(self, users, from_block):
        changed_wallets = {}

        for user in users:
            time = datetime.now()
            #import pytest; pytest.set_trace()
            if user.last_emailed_at + user.email_limit < time:
                for wallet in user.wallets.filter(Wallet.network == self.network):
                    latest_balance = self.get_latest_balance(wallet.address)
                    if wallet.balance != latest_balance:
                        w = self.ChangedWallet(wallet.network, wallet.address, wallet.balance, latest_balance)
                        changed_wallets.setdefault(user, []).append(w)
                        wallet.balance = latest_balance
        
                # Need to track the last block we went through.
                # They also need to be individual to each user.
                user.last_etc_block = from_block

        db.session.commit()
        return changed_wallets


    def record_wallets(self, address, from_block, to_block="latest"):
        if isinstance(from_block, int):
            from_block = hex(from_block)

        if isinstance(to_block, int):
            to_block = hex(to_block)

        results = self.query("trace_filter", [{  
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
            wallet = find_wallet(user, self.network, user_address)

            if user is not None and wallet is None:
                balance = self.get_latest_balance(user_address)
                wallet = create_wallet(user, self.network, user_address, balance)

                db.session.add(wallet)

        db.session.commit()

