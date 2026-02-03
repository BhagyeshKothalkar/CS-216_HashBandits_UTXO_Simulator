class UTXOManager:
    def __init__(self):
        self.utxo_set = {}

    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str):
        """adds UTXO to the UTXO set"""
        self.utxo_set[(tx_id, index)] = (amount, owner)

    def remove_utxo(self, tx_id: str, index: int) -> bool:
        """removes utxos from the set. Returns True if successful, False otherwise."""
        if self.exists(tx_id, index):
            self.utxo_set.pop((tx_id, index))
            return True
        return False

    def get_balance(self, owner: str):
        """Calculate total balance for an address ."""
        sum = 0

        for amount, utxo_owner in self.utxo_set.values():
            if utxo_owner == owner:
                sum += amount

        return sum

    def exists(self, tx_id, index: int):
        """Check if UTXO exists and is unspent ."""
        return self.utxo_set.get((tx_id, index)) is not None

    def get_utxo(self, tx_id: str, index: int):
        """Returns (amount, owner) or None if not found"""
        return self.utxo_set.get((tx_id, index))

    def get_utxos_for_owner(self, owner: str) -> list:
        """Get all UTXOs owned by an address ."""

        ret = []

        for tx_details, amt_details in self.utxo_set.items():
            tx_id, index = tx_details
            amount, utxo_owner = amt_details
            if utxo_owner == owner:
                ret.append([tx_id, index, amount])

        return ret
