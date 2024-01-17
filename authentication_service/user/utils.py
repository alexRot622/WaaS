import subprocess
import os
import re

SMART_CONTRACT_ADDRESS = 'erd1qqqqqqqqqqqqqpgqujkufkm6yvhnnhz6qsgn03wzeppz724xzrmqzlgsug'
OWNER_KEY = "/home/vlad/Desktop/Blockchain/private_key.pem"
PROXY = "https://testnet-api.multiversx.com"

def get_address(pem_path):
    with open(pem_path, 'r') as f:
        text = f.read()
    match = re.search(r'-----BEGIN PRIVATE KEY for (.*?)-----', text)
    if match:
        return match.group(1)
    return None


def mx_send(recevier):
    cmd = f"mxpy --verbose tx new --pem {OWNER_KEY} --recall-nonce \
        --receiver {recevier} \
        --gas-limit 50000 --value 1500000000000000000 \
        --proxy {PROXY} --chain D \
        --send"
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    return output

def mx_contract(pem_path, function, args):
    args = [f'str:{arg}' if type(arg) == str else str(arg) for arg in args]
    cmd = f"mxpy --verbose contract call {SMART_CONTRACT_ADDRESS} \
            --recall-nonce --pem={pem_path} --gas-limit=50000000 \
            --function=\"{function}\" --arguments {' '.join(args)} --send \
            --proxy={PROXY} --chain=T"
    print(cmd)
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    print(output)
    return output

def mx_query(function, args):
    args = [f'str:{arg}' if type(arg) == str else str(arg) for arg in args]
    cmd = f"mxpy --verbose contract query {SMART_CONTRACT_ADDRESS} --function={function}  --arguments {' '.join(args)}  --proxy={PROXY}"
    print(cmd)
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    print(output)
    return output

def mx_wallet(id):
    dir_path = os.path.join(os.getcwd(), 'temp')
    os.makedirs(dir_path, exist_ok=True)
    filename = f"{id}.pem"
    filepath = os.path.join(dir_path, filename)
    cmd = f"mxpy wallet new --format pem --outfile {filepath}"
    output = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()
    return filepath