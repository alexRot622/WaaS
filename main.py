from dotenv import load_dotenv
from flask import Flask
import subprocess
import secrets

app = Flask(__name__)

load_dotenv()
address = env.get("ADDRESS")
pem = env.get("PEM")


def mx_call(function, args):
    #TODO: need to use "str:[arg]" for string arguments
    #TODO: strings are probably base64 encoded
    cmd = f"mxpy contract call {address} \
            --recall-nonce --pem=${pem} --gas-limit=50000000 \
            --function=\"{function}\" --arguments {' '.join(args)} --send"
    return subproces.run(cmd).stdout


@app.route("/balance")
def balance():
    user = request.args.get("user")
    password = request.args.get("password")
    return mx_call("balance", [user, password])


@app.route("/transfer")
def transfer():
    user = request.args.get("user")
    password = request.args.get("password")
    recipient = request.args.get("recipient")
    amount = request.args.get("amount")
    return mx_call("transfer", [user, password, recipient, amount])


@app.route("/create")
def create():
    user = request.args.get("user")
    password = request.args.get("password")
    return mx_call("create", [user, password])


@app.route("/mint")
def mint():
    recipient = request.args.get("recipient")
    amount = request.args.get("amount")
    return mx_call("mint", [recipient, amount])


@app.route("/history")
def history():
    key = request.args.get("key")
    user = request.args.get("user")
    password = request.args.get("password")
    return mx_call("history", [key, user, password])


if __name__ == "__main__":
    app.run(ssl_context=("cert.pem", "key.pem"))
