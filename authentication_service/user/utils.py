import subprocess
import os

SMART_CONTRACT_ADDRESS = 'erd1qqqqqqqqqqqqqpgqujkufkm6yvhnnhz6qsgn03wzeppz724xzrmqzlgsug'

def mx_contract(pem_path, function, args):
    args = [f'str:{arg}' for arg in args]
    cmd = f"mxpy contract call {SMART_CONTRACT_ADDRESS} \
            --recall-nonce --pem=${pem_path} --gas-limit=50000000 \
            --function=\"{function}\" --arguments {' '.join(args)} --send"
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    return

def mx_wallet(id):
    dir_path = os.path.join(os.getcwd(), 'temp')
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{id}.pem"
    filepath = os.path.join(dir_path, filename)
    cmd = f"mxpy wallet new --format pem --outfile {filepath}"
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    return filepath