import sys

import mining
import test_cases
from block import Blockchain
from mempool import Mempool
from transaction import Input, Output, Transaction, generate_tx_id
from utxo_manager import UTXOManager


def initialize_genesis(utxo_manager):
    """
    Initializes the UTXO set with the Genesis Block values.
    """
    genesis_utxos = [
        ("Alice", 50.0),
        ("Bob", 30.0),
        ("Charlie", 20.0),
        ("David", 10.0),
        ("Eve", 5.0),
    ]

    print("Initializing Genesis UTXOs...")
    for idx, (owner, amount) in enumerate(genesis_utxos):
        utxo_manager.add_utxo("genesis", idx, amount, owner)
        print(f"Created UTXO (genesis, {idx}): {amount} BTC -> {owner}")
    print("-" * 30)


def print_menu(utxo_manager):
    print("\n=== Bitcoin Transaction Simulator ===")
    print("Initial UTXOs (Genesis Block):")

    owners = set()
    for (tx_id, index), (amount, owner) in utxo_manager.utxo_set.items():
        owners.add(owner)

    for owner in sorted(list(owners)):
        balance = utxo_manager.get_balance(owner)
        print(f"{owner}: {balance:.1f} BTC")

    print("\nMain Menu:")
    print("1. Create new transaction")
    print("2. View UTXO set")
    print("3. View mempool")
    print("4. Mine block")
    print("5. Run test scenarios")
    print("6. Exit")


def create_transaction_cli(utxo_manager, mempool):
    """
    Follows the exact workflow from Section 4.1 Example Workflow.
    """
    sender = input("Enter sender: ").strip()
    balance = utxo_manager.get_balance(sender)
    print(f"Available balance: {balance}")

    recipient = input("Enter recipient: ").strip()
    amount_str = input("Enter amount: ").strip()
    try:
        amount = float(amount_str.replace("BTC", "").strip())
    except ValueError:
        print("Invalid amount.")
        return

    FEE = 0.001
    inputs = []
    input_sum = 0.0
    for tx_id, idx, val in utxo_manager.get_utxos_for_owner(sender):
        inputs.append(Input(tx_id, idx, sender))
        input_sum += val
        if input_sum >= (amount + FEE):
            break

    tx_id = generate_tx_id()
    outputs = [Output(amount, recipient), Output(input_sum - amount - FEE, sender)]
    tx = Transaction(tx_id, inputs, outputs)

    print("Creating transaction...")
    success, msg = mempool.add_transaction(tx, utxo_manager)

    if success:
        print(f"Transaction valid! Fee: {FEE} BTC")
        print(f"Transaction ID: {tx_id}")
        print("Transaction added to mempool.")
        print(f"Mempool now has {len(mempool.transactions)} transactions.")
    else:
        print(f"Transaction Rejected: {msg}")


def view_utxo_set(utxo_manager):
    print("\n--- Current UTXO Set ---")
    if not utxo_manager.utxo_set:
        print("No UTXOs.")
    else:
        for (tx_id, idx), (amount, owner) in utxo_manager.utxo_set.items():
            print(f"({tx_id}, {idx}) -> {amount:.3f} BTC ({owner})")


def view_mempool(mempool):
    print("\n--- Mempool Contents ---")
    if not mempool.transactions:
        print("Mempool is empty.")
    else:
        for neg_fee, tx in mempool.transactions:
            fee = -neg_fee
            print(
                f"TX: {tx.tx_id}, Fee: {fee:.4f}, Inputs: {len(tx.inputs)}, Outputs: {len(tx.outputs)}"
            )


def mine_block_cli(mempool, utxo_manager, blockchain):
    """
    Follows the mining workflow from Section 4.1.
    """
    miner = input("Enter miner name: ").strip()
    print("Mining block...")

    tx_count = len(mempool.transactions)

    mining.mine_block(miner, mempool, utxo_manager, blockchain)

    print("Block mined successfully!")
    print(f"Removed {tx_count} transactions from mempool.")


def run_test_scenarios(utxo_manager, mempool):
    print("\n--- Test Scenarios ---")
    print("1. Test 1: Basic Valid Transaction")
    print("2. Test 2: Multiple Inputs")
    print("3. Test 3: Double-Spend in Same Transaction")
    print("4. Test 4: Mempool Double-Spend")
    print("5. Test 5: Insufficient Funds")
    print("6. Test 6: Negative Amount")
    print("7. Test 7: Zero Fee Transaction")
    print("8. Test 8: Race Attack Simulation")
    print("9. Test 9: Complete Mining Flow")
    print("10. Test 10: Unconfirmed Chain")

    try:
        choice = int(input("Select test scenario: "))
    except ValueError:
        return

    print(f"Running Test {choice}...")

    if choice == 1:
        test_cases.test_basic_valid_tx(utxo_manager, mempool)
    elif choice == 2:
        test_cases.test_multiple_inputs(utxo_manager, mempool)
    elif choice == 3:
        test_cases.test_double_spend_same_tx(utxo_manager, mempool)
    elif choice == 4:
        test_cases.test_mempool_double_spend(utxo_manager, mempool)
    elif choice == 5:
        test_cases.test_insufficient_funds(utxo_manager, mempool)
    elif choice == 6:
        test_cases.test_negative_amount(utxo_manager, mempool)
    elif choice == 7:
        test_cases.test_zero_fee(utxo_manager, mempool)
    elif choice == 8:
        test_cases.test_race_attack(utxo_manager, mempool)
    elif choice == 9:
        test_cases.test_complete_mining_flow(utxo_manager, mempool)
    elif choice == 10:
        test_cases.test_unconfirmed_chain(utxo_manager, mempool)
    else:
        print("Invalid test choice.")


def reset_state_for_test(utxo_manager, mempool):
    """Resets mempool for testing logic."""

    mempool.clear()

    pass


def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    blockchain = Blockchain(utxo_manager)
    initialize_genesis(utxo_manager)

    while True:
        print_menu(utxo_manager)
        choice = input("Enter choice : ").strip()

        if choice == "1":
            create_transaction_cli(utxo_manager, mempool)
        elif choice == "2":
            view_utxo_set(utxo_manager)
        elif choice == "3":
            view_mempool(mempool)
        elif choice == "4":
            mine_block_cli(mempool, utxo_manager, blockchain)
        elif choice == "5":
            run_test_scenarios(utxo_manager, mempool)
        elif choice == "6":
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
