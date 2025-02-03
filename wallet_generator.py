#!/usr/bin/env python3
import json
from solana.keypair import Keypair

def generate_wallet():
    keypair = Keypair.generate()
    wallet = {
        "public_key": str(keypair.public_key),
        "secret_key": list(keypair.secret_key)
    }
    return wallet

if __name__ == "__main__":
    wallet = generate_wallet()
    with open("wallet.json", "w") as f:
        json.dump(wallet, f)
    print("Generated wallet:")
    print(wallet)
