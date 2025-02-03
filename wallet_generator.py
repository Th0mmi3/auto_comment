#!/usr/bin/env python3
import json
from solders.keypair import Keypair

def generate_wallet():
    keypair = Keypair()
    wallet = {
        "public_key": str(keypair.pubkey()),
        "secret_key": list(keypair.to_bytes())
    }
    return wallet

if __name__ == "__main__":
    wallet = generate_wallet()
    with open("wallet.json", "w") as f:
        json.dump(wallet, f)
    print("Generated wallet:")
    print(wallet)

