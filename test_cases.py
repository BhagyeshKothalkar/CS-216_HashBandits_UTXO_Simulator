import mining
from block import Blockchain
from transaction import Input, Output, Transaction


def test_basic_valid_tx(utxo_manager, mempool):
    utxo_manager.add_utxo("test1_setup", 0, 50.0, "Alice_Test1")

    inputs = [Input("test1_setup", 0, "Alice_Test1")]
    outputs = [
        Output(10.0, "Bob_Test1"),
        Output(39.999, "Alice_Test1"),
    ]
    tx = Transaction("tx_test1", inputs, outputs)

    print("Testing Basic Valid Transaction (Alice -> Bob 10 BTC)...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_multiple_inputs(utxo_manager, mempool):
    utxo_manager.add_utxo("test2_in1", 0, 50.0, "Alice_Test2")
    utxo_manager.add_utxo("test2_in2", 0, 20.0, "Alice_Test2")

    inputs = [
        Input("test2_in1", 0, "Alice_Test2"),
        Input("test2_in2", 0, "Alice_Test2"),
    ]
    outputs = [Output(60.0, "Bob_Test2"), Output(9.999, "Alice_Test2")]
    tx = Transaction("tx_test2", inputs, outputs)

    print("Testing Multiple Inputs (50+20 -> 60)...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_double_spend_same_tx(utxo_manager, mempool):
    utxo_manager.add_utxo("test3_setup", 0, 10.0, "Alice_Test3")

    inputs = [
        Input("test3_setup", 0, "Alice_Test3"),
        Input("test3_setup", 0, "Alice_Test3"),
    ]
    outputs = [Output(10.0, "Bob_Test3")]
    tx = Transaction("tx_test3", inputs, outputs)

    print("Testing Double Spend in Same Transaction...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_mempool_double_spend(utxo_manager, mempool):
    utxo_manager.add_utxo("test4_setup", 0, 10.0, "Alice_Test4")

    inputs1 = [Input("test4_setup", 0, "Alice_Test4")]
    outputs1 = [Output(5.0, "Bob_Test4")]
    tx1 = Transaction("tx_test4_1", inputs1, outputs1)

    inputs2 = [Input("test4_setup", 0, "Alice_Test4")]
    outputs2 = [Output(5.0, "Charlie_Test4")]
    tx2 = Transaction("tx_test4_2", inputs2, outputs2)

    print("Testing Mempool Double Spend...")
    s1, m1 = mempool.add_transaction(tx1, utxo_manager)
    print(f"TX1 Add: {s1}, {m1}")

    s2, m2 = mempool.add_transaction(tx2, utxo_manager)
    print(f"TX2 Add (Should Fail): {s2}, {m2}")


def test_insufficient_funds(utxo_manager, mempool):
    utxo_manager.add_utxo("test5_setup", 0, 30.0, "Bob_Test5")

    inputs = [Input("test5_setup", 0, "Bob_Test5")]
    outputs = [Output(35.0, "Alice_Test5")]
    tx = Transaction("tx_test5", inputs, outputs)

    print("Testing Insufficient Funds...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_negative_amount(utxo_manager, mempool):
    utxo_manager.add_utxo("test6_setup", 0, 10.0, "Alice_Test6")

    inputs = [Input("test6_setup", 0, "Alice_Test6")]
    outputs = [Output(-5.0, "Bob_Test6")]
    tx = Transaction("tx_test6", inputs, outputs)

    print("Testing Negative Amount...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_zero_fee(utxo_manager, mempool):
    utxo_manager.add_utxo("test7_setup", 0, 10.0, "Alice_Test7")

    inputs = [Input("test7_setup", 0, "Alice_Test7")]
    outputs = [Output(10.0, "Bob_Test7")]
    tx = Transaction("tx_test7", inputs, outputs)

    print("Testing Zero Fee...")
    success, msg = mempool.add_transaction(tx, utxo_manager)
    print(f"Result: {success}, {msg}")


def test_race_attack(utxo_manager, mempool):
    utxo_manager.add_utxo("test8_setup", 0, 20.0, "Alice_Test8")

    inp = [Input("test8_setup", 0, "Alice_Test8")]
    out1 = [Output(10.0, "Bob_Test8"), Output(9.999, "Alice_Test8")]
    tx1 = Transaction("tx_test8_low", inp, out1)

    out2 = [Output(10.0, "Charlie_Test8"), Output(9.0, "Alice_Test8")]
    tx2 = Transaction("tx_test8_high", inp, out2)

    print("Testing Race Attack (First Seen Rule)...")
    s1, m1 = mempool.add_transaction(tx1, utxo_manager)
    print(f"Low Fee TX Arrives First: {s1}, {m1}")

    s2, m2 = mempool.add_transaction(tx2, utxo_manager)
    print(f"High Fee TX Arrives Second (Should Reject): {s2}, {m2}")


def test_complete_mining_flow(utxo_manager, mempool):
    print("Testing Complete Mining Flow...")
    mempool.clear()
    utxo_manager.add_utxo("test9_setup", 0, 10.0, "Alice_Test9")

    inp = [Input("test9_setup", 0, "Alice_Test9")]
    out = [Output(9.0, "Bob_Test9")]
    tx = Transaction("tx_test9", inp, out)

    mempool.add_transaction(tx, utxo_manager)
    print("Mempool before mining:", len(mempool.transactions))

    print("Mempool before mining:", len(mempool.transactions))

    test_blockchain = Blockchain(utxo_manager)
    mining.mine_block("Miner_Test9", mempool, utxo_manager, test_blockchain)

    print("Mempool after mining:", len(mempool.transactions))

    exists_inp = utxo_manager.exists("test9_setup", 0)

    exists_out = utxo_manager.exists("tx_test9", 0)

    print(f"Input UTXO consumed: {not exists_inp}")
    print(f"Output UTXO created: {exists_out}")


def test_unconfirmed_chain(utxo_manager, mempool):
    print("Testing Unconfirmed Chain (Chained Mempool Transacions)...")

    utxo_manager.add_utxo("test10_setup", 0, 10.0, "Alice_Test10")

    inp1 = [Input("test10_setup", 0, "Alice_Test10")]

    out1 = [Output(10.0, "Bob_Test10")]
    tx1 = Transaction("tx_test10_1", inp1, out1)

    mempool.add_transaction(tx1, utxo_manager)
    print("TX1 (Alice->Bob) added to mempool.")

    inp2 = [Input("tx_test10_1", 0, "Bob_Test10")]
    out2 = [Output(10.0, "Charlie_Test10")]
    tx2 = Transaction("tx_test10_2", inp2, out2)

    success, msg = mempool.add_transaction(tx2, utxo_manager)
    print(f"TX2 (Bob->Charlie) Result: {success}, {msg}")
    print("Explanation: Rejected because input UTXO is not yet confirmed (mined).")
