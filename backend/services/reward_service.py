import os
from web3 import Web3
import logging

PRIVATE_KEY = os.getenv("MANTLE_PRIVATE_KEY")
RPC_URL = os.getenv("MANTLE_RPC_URL")
SENDER_ADDRESS = Web3.to_checksum_address(Web3().eth.account.from_key(PRIVATE_KEY).address)

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def send_reward(to_address: str, amount_eth=0.01):
    if not to_address or not Web3.is_address(to_address):
        logging.warning(f"Invalid wallet address: {to_address}")
        return "invalid_wallet"
    
    logging.info(f"Sending {amount_eth} MNT to {to_address}")
    to_address = Web3.to_checksum_address(to_address)
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
    tx = {
        "nonce": nonce,
        "to": to_address,
        "value": w3.to_wei(amount_eth, "ether"),
        "gas": 21000,
        "gasPrice": w3.to_wei("1", "gwei"),
        "chainId": 5003  # Mantle Sepolia chain ID
    }
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    logging.info(f"Reward sent, tx hash: {tx_hash.hex()}")
    return tx_hash.hex()