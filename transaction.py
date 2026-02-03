import random
import time


def generate_tx_id():
    """Generate a unique transaction ID."""
    return f"tx_{int(time.time())}_{random.randint(1000, 9999)}"


class Input:
    def __init__(self, prev_tx, index, owner):
        self.prev_tx = prev_tx
        self.index = index
        self.owner = owner

    def __repr__(self):
        return f"Input(prev_tx={self.prev_tx}, index={self.index}, owner={self.owner})"


class Output:
    def __init__(self, amount, address):
        self.amount = amount
        self.address = address

    def __repr__(self):
        return f"Output(amount={self.amount}, address={self.address})"


class Transaction:
    def __init__(self, tx_id, inputs, outputs):
        self.tx_id = tx_id
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        return f"Transaction(tx_id={self.tx_id}, inputs={self.inputs}, outputs={self.outputs})"

    def __lt__(self, other):
        return self.tx_id < other.tx_id
