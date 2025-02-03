#!/usr/bin/env python3
import json
from eth_account import Account

def generate_wallet():
    account = Account.create()
    wallet = {
        "address": account.address,
        "private_key": account.key.hex()
    }
    return wallet

if __name__ == "__main__":
    wallet = generate_wallet()
    with open("wallet.json", "w") as f:
        json.dump(wallet, f)
    print("Generated wallet:")
    print(wallet)
