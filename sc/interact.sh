ALICE=""
ADDRESS=$(mxpy data load --key=address-testnet)
DEPLOY_TRANSACTION=$(mxpy data load --key=deployTransaction-testnet)
PROXY=https://testnet-api.multiversx.com
PROJECT="/home/alex/Programming/BPDA/WaaS/sc/output/waas.wasm"
TRANSACTION=0b78df53e1dab33c379414a60a685ad4825b9524a43961d1f6604b47068848dc
ADDRESS=erd1qqqqqqqqqqqqqpgqujkufkm6yvhnnhz6qsgn03wzeppz724xzrmqzlgsug

deploy() {
    mxpy --verbose contract deploy --bytecode=${PROJECT} --recall-nonce --pem=${ALICE} --gas-limit=50000000 --send --outfile="deploy-testnet.interaction.json" --proxy=${PROXY} --chain=T || return
}

deploy_upgrade() {
    mxpy --verbose contract upgrade ${ADDRESS} --bytecode=${PROJECT} --recall-nonce --pem=${ALICE} --gas-limit=50000000 --send --outfile="deploy-testnet.interaction.json" --proxy=${PROXY} --chain=T || return
}

get_data() {
    TRANSACTION=$(mxpy data parse --file="deploy-testnet.interaction.json" --expression="data['emittedTransactionHash']")
    ADDRESS=$(mxpy data parse --file="deploy-testnet.interaction.json" --expression="data['contractAddress']")

    mxpy data store --key=address-testnet --value=${ADDRESS}
    mxpy data store --key=deployTransaction-testnet --value=${TRANSACTION}

    echo ""
    echo "Smart contract address: ${ADDRESS}"
}

add_account() {
    mxpy --verbose contract call ${ADDRESS} --recall-nonce --pem=${ALICE} --gas-limit=5000000 --function="add_account" --arguments str:$1 --send --proxy=${PROXY} --chain=T
}

mint() {
    mxpy --verbose contract call ${ADDRESS} --recall-nonce --pem=${ALICE} --gas-limit=5000000 --function="mint" --arguments str:$1 $2 --send --proxy=${PROXY} --chain=T
}

transfer() {
    mxpy --verbose contract call ${ADDRESS} --recall-nonce --pem=${ALICE} --gas-limit=5000000 --function="transfer" --arguments str:$1 str:$2 $3 --send --proxy=${PROXY} --chain=T
}

get_account_balance() {
    mxpy --verbose contract query ${ADDRESS} --function="get_account_balance" --arguments str:$1 --proxy=${PROXY}
}

get_account_history() {
    mxpy --verbose contract query ${ADDRESS} --function="get_account_history" --arguments str:$1 --proxy=${PROXY}
}

get_account_balances() {
    mxpy --verbose contract query ${ADDRESS} --function="getAccountBalance" --proxy=${PROXY}
}

get_history() {
    mxpy --verbose contract query ${ADDRESS} --function="getHistory" --proxy=${PROXY}
}
