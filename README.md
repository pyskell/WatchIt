[Flask-User-starter-app](https://github.com/lingthio/Flask-User-starter-app) was used as a starting point for this code repository.

This project makes use of Flask, Celery, RabbitMQ, and several Flask-based packages.

#What is WatchIt?#
WatchIt is a service that monitors wallets on various blockchains for changes and emails you when these changes happen.
Currently it watches for changes to balances on the Ethereum Classic network (support for Ethereum and Bitcoin is planned).

#How does it work?#
1. Create an account
2. Copy your `Public UUID` from the website
3. Send a transaction from the address you want to monitor with this `Public UUID` in the input data section. You do not need to send any money with the transaction (you can leave ETC sent as 0). You only pay the transaction cost.
4. WatchIt then emails you whenever the balance at this address changes

#Note#
This is very alpha software, as such it may not always work as expected and bugs are to be expected. If you find a bug please let me know.

#License#
BSD 2-clause "Simplified" License