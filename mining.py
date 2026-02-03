import random

from block import Block, Blockchain
from mempool import Mempool
from utxo_manager import UTXOManager


def mine_block(
    miner_address: str,
    mempool: Mempool,
    utxo_manager: UTXOManager,
    blockchain: Blockchain,
    num_txs=5,
):
    transactions_to_mine = mempool.get_top_transactions(num_txs)
    if not transactions_to_mine:
        print("No transactions to mine.")
        return

    target = 42
    nonce = 0
    while random.randint(1, 100) != target:
        nonce += 1
    print(f"Nonce found: {nonce}")

    total_fees = 0.0
    for tx in transactions_to_mine:
        in_sum = sum(utxo_manager.get_utxo(i.prev_tx, i.index)[0] for i in tx.inputs)
        out_sum = sum(o.amount for o in tx.outputs)
        total_fees += in_sum - out_sum

        for inp in tx.inputs:
            utxo_manager.remove_utxo(inp.prev_tx, inp.index)
        for i, out in enumerate(tx.outputs):
            utxo_manager.add_utxo(tx.tx_id, i, out.amount, out.address)

        mempool.remove_transaction(tx.tx_id)

    reward = total_fees
    coinbase_id = f"coinbase_{blockchain.get_main_chain_tip()}"
    utxo_manager.add_utxo(coinbase_id, 0, reward, miner_address)

    new_block = Block(
        index=len(blockchain.main_chain),
        prev_hash=blockchain.get_main_chain_tip(),
        transactions=transactions_to_mine,
        nonce=nonce,
        miner=miner_address,
    )

    blockchain.add_block(new_block)
