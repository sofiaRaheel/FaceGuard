from web3 import Web3
import json
from eth_account import Account

class BlockchainLogger:
    def __init__(self, abi_path, contract_address, private_key=ADD KEY"):
        # Connect to Ganache
        self.web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
        
        # Load ABI
        with open(abi_path) as f:
            contract_json = json.load(f)
            abi = contract_json["abi"]
        
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        self.account = Account.from_key(private_key)

        self.private_key = private_key
    
    def log_attendance(self, name, timestamp, record_hash):
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        
        txn = self.contract.functions.logAttendance(name, timestamp, record_hash).build_transaction({
            'chainId': 1337,
            'gas': 200000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'nonce': nonce
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()
