# CS216 — Bitcoin Transaction & UTXO Simulator

## Team Information

| # | Name | Roll Number |
|---|------|-------------|
| 1 | Kothalkar Bhagyesh Ritesh |240041024 |
| 2 | KVL Sarath Chandra | 240001039 |
| 3 | Khush Kumar Singh  | 240041023 |
| 4 | Yash Bhamare | 240041040 |

**Team Name:** HashBandits

---

## How to Run

```bash
# Make sure you have Python 3.8 or later installed
python --version

# Launch the simulator
python main.py
```

No internet connection or external packages are needed.

---

## Project Structure

```
your-repository/
├── main.py                  # Entry point — interactive menu (Section 4)
├── utxo_manager.py          # Part 1 — UTXO set management (3 marks)
├── transaction.py           # Part 2 — Transaction data model
├── validator.py             # Part 2 — All 5 validation rules (4 marks)
├── mempool.py               # Part 3 — Mempool with conflict detection (3 marks)
├── block.py                 # Part 4 — Mining simulation + fork handling (3 marks)
├── mining.py                # Mining logic and block creation
├── test_scenarios.py        # Part 5 — All 10 mandatory test cases (2 marks)
├── requirements.txt         # (empty — standard library only)
└── README.md                # This file
```

---

## Design Decisions

### Test 10 - Unconfirmed Chain: REJECT

When Bob tries to spend a UTXO that was *created* by an unconfirmed transaction (still in the mempool), we **reject** the transaction.

**Why:** A UTXO only enters the `UTXOManager` when it is confirmed by mining. Until then, it simply does not exist. Rule 1 of validation ("all inputs must exist in the UTXO set") naturally catches this case. This is the simpler and more secure approach - it matches how most Bitcoin nodes behave.

### Mempool Eviction Policy

When the mempool reaches its maximum size (default 50), we evict the transaction with the **lowest fee**. This mirrors real Bitcoin node behaviour where low-fee transactions are dropped to make room for higher-fee ones.

### Race Attack - First-Seen Rule

When two conflicting transactions (spending the same UTXO) arrive, the **first one** to enter the mempool wins, regardless of fee. The second is rejected because its input UTXO is already marked as spent in `mempool.spent_utxos`. This is the standard "first-seen" rule used by Bitcoin nodes.

### Coinbase Reward

The miner receives a single coinbase UTXO equal to the **sum of all transaction fees** in the mined block. In real Bitcoin there is also a block subsidy (currently 3.125 BTC), but the assignment specifies only fee-based rewards.

### Zero Fee

A transaction with zero fee (inputs exactly equal outputs) is **accepted**. This is valid in Bitcoin - zero-fee transactions are simply deprioritised by miners.

### Fork Handling & Chain Reorganization

When multiple chains of equal or longer length are detected, the blockchain implements **longest-chain-wins** consensus with proper reorganization:
- Stores side chains separately for tracking
- Detects forks and maintains alternative chain history
- Performs chain reorganization (reorg) when a longer chain is discovered
- Rolls back transactions from the old main chain
- Re-applies transactions from the new longer chain
- Updates UTXO state correctly during reorg
- Handles orphan blocks (blocks with missing parents)

---

## Parts & Marks Breakdown

| Part | File(s) | What it does |
|------|----------------|--------------|
| 1 | `utxo_manager.py` | CRUD on the UTXO set; balance & ownership queries |
| 2 | `transaction.py` + `validator.py` | Transaction structure + all 5 validation rules |
| 3 | `mempool.py` | Unconfirmed tx storage, conflict detection, fee-based eviction |
| 4 | `block.py` + `mining.py` | Mining: select txs, update UTXOs, coinbase reward, fork handling |
| 5 | `test_scenarios.py` | All 10 mandatory tests including double-spend & race attack |
