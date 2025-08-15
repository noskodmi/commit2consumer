import os
import logging
from web3 import Web3
from config import settings

logger = logging.getLogger(__name__)

# Initialize Web3
try:
    PRIVATE_KEY = settings.MANTLE_PRIVATE_KEY
    RPC_URL = settings.MANTLE_RPC_URL
    
    if not PRIVATE_KEY or not RPC_URL:
        logger.error("Missing MANTLE_PRIVATE_KEY or MANTLE_RPC_URL")
        w3 = None
        SENDER_ADDRESS = None
    else:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        SENDER_ADDRESS = Web3.to_checksum_address(
            w3.eth.account.from_key(PRIVATE_KEY).address
        )
        logger.info(f"Web3 initialized with sender address: {SENDER_ADDRESS}")
        
        # Check connection
        if w3.is_connected():
            chain_id = w3.eth.chain_id
            logger.info(f"Connected to blockchain with chain ID: {chain_id}")
        else:
            logger.error(f"Failed to connect to RPC URL: {RPC_URL}")
            
except Exception as e:
    logger.error(f"Error initializing Web3: {str(e)}")
    w3 = None
    SENDER_ADDRESS = None

def send_reward(to_address: str, amount_eth=0.01):
    """Send a reward to a contributor's wallet address"""
    
    # Validate inputs
    if not w3 or not SENDER_ADDRESS:
        logger.error("Web3 not properly initialized")
        return "web3_not_initialized"
        
    if not to_address:
        logger.warning("No wallet address provided")
        return "no_wallet_address"
        
    if not Web3.is_address(to_address):
        logger.warning(f"Invalid wallet address format: {to_address}")
        return "invalid_wallet"
    
    try:
        logger.info(f"Sending {amount_eth} MNT to {to_address}")
        to_address = Web3.to_checksum_address(to_address)
        
        # Check balance
        balance = w3.eth.get_balance(SENDER_ADDRESS)
        amount_wei = w3.to_wei(amount_eth, "ether")
        
        if balance < amount_wei:
            logger.error(f"Insufficient balance: {w3.from_wei(balance, 'ether')} MNT")
            return "insufficient_balance"
        
        # Prepare transaction
        nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)
        tx = {
            "nonce": nonce,
            "to": to_address,
            "value": amount_wei,
            "gas": 21000,
            "gasPrice": w3.to_wei("1", "gwei"),
            "chainId": settings.CHAIN_ID
        }
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"Reward sent, tx hash: {tx_hash.hex()}")
        return tx_hash.hex()
        
    except Exception as e:
        logger.error(f"Error sending reward: {str(e)}")
        return f"error: {str(e)}"