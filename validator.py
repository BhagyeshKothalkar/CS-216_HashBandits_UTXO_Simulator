from transaction import Transaction
from utxo_manager import UTXOManager


def validate_tx(
    tx: Transaction, utxo_manager: UTXOManager, mempool_spent_utxos: set
) -> tuple[bool, str, float]:
    """
    Validates a transaction against the UTXO set and mempool state.
    Returns: (is_valid, message, fee)
    """
    tx_utxos = set()
    input_sum = 0.0

    for inp in tx.inputs:
        prev_tx_id = inp.prev_tx
        idx = inp.index
        utxo_details = (prev_tx_id, idx)

        if not utxo_manager.exists(prev_tx_id, idx):
            return False, f"UTXO {utxo_details} not found in UTXO set", 0.0

        if utxo_details in mempool_spent_utxos:
            return False, f"UTXO {utxo_details} already spent in mempool", 0.0

        if utxo_details in tx_utxos:
            return (
                False,
                f"Double spending in same transaction for UTXO {utxo_details}",
                0.0,
            )

        tx_utxos.add(utxo_details)

        utxo_data = utxo_manager.get_utxo(prev_tx_id, idx)
        input_sum += utxo_data[0]

    output_sum = 0.0
    for output in tx.outputs:
        if output.amount < 0:
            return False, "Output amount cannot be negative", 0.0
        output_sum += output.amount

    if output_sum > input_sum:
        return False, "Output sum exceeds input sum", 0.0

    fee = input_sum - output_sum
    return True, "Transaction Valid", fee
