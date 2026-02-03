import heapq

from transaction import Transaction
from utxo_manager import UTXOManager
from validator import validate_tx


class Mempool:
    def __init__(self, max_size=50):
        self.transactions = []
        self.spent_utxos = set()
        self.max_size = max_size

    def add_transaction(
        self, tx: Transaction, utxo_manager: UTXOManager
    ) -> tuple[bool, str]:
        """Validate and add transaction. Return (success, message)."""
        validity_check = validate_tx(tx, utxo_manager, self.spent_utxos)
        if not validity_check[0]:
            return validity_check[0], validity_check[1]

        fee = validity_check[2]

        # Check if mempool is full and handle eviction
        if len(self.transactions) >= self.max_size:
            if self.transactions:
                lowest_fee_entry = self.transactions[0]
                lowest_fee = -lowest_fee_entry[0]  # Extract fee (negate stored negative value)
                
                if fee > lowest_fee:
                    # Evict the lowest fee transaction
                    _, evicted_tx = heapq.heappop(self.transactions)
                    for inp in evicted_tx.inputs:
                        self.spent_utxos.discard((inp.prev_tx, inp.index))
                    print(f"Evicted transaction {evicted_tx.tx_id} with fee {lowest_fee:.6f} BTC to make room for higher fee tx.")
                else:
                    return False, f"Mempool is full. New tx fee ({fee:.6f}) not higher than lowest fee ({lowest_fee:.6f})"
            else:
                return False, "Mempool is full"

        heapq.heappush(self.transactions, (-fee, tx))

        for inp in tx.inputs:
            self.spent_utxos.add((inp.prev_tx, inp.index))

        return True, "Transaction added to MemPool"

    def remove_transaction(self, tx_id: str):
        """
        Remove transaction (when mined).
        Since heapq doesn't support efficient removal by ID, we filter the list
        and re-heapify. This is O(N).
        """
        original_len = len(self.transactions)
        new_transactions = []
        for neg_fee, tx in self.transactions:
            if tx.tx_id == tx_id:
                for inp in tx.inputs:
                    self.spent_utxos.discard((inp.prev_tx, inp.index))
            else:
                new_transactions.append((neg_fee, tx))

        if len(new_transactions) != original_len:
            self.transactions = new_transactions
            heapq.heapify(self.transactions)

    def get_top_transactions(self, n: int) -> list:
        """Return top N transactions by fee (highest first)."""
        top_entries = heapq.nsmallest(n, self.transactions)
        return [entry[1] for entry in top_entries]

    def clear(self):
        """Clear all transactions."""
        self.transactions.clear()
        self.spent_utxos.clear()
