class Block:
    def __init__(self, index, prev_hash, transactions, nonce, miner):
        self.index = index
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.nonce = nonce
        self.miner = miner
        self.block_id = f"block_{index}_{nonce}"


class Blockchain:
    def __init__(self, utxo_manager):
        self.main_chain = []
        self.side_chains = {}  # Maps tip_block_id -> list of blocks
        self.utxo_manager = utxo_manager
        self.block_map = {}    # Maps block_id -> Block for quick lookup

    def add_block(self, new_block):
        """
        Add a block and handle fork resolution with chain reorganization.
        Implements "longest chain wins" rule with proper reorg.
        """
        
        # Check if this block extends the main chain
        if not self.main_chain or new_block.prev_hash == self.main_chain[-1].block_id:
            self.main_chain.append(new_block)
            self.block_map[new_block.block_id] = new_block
            print(f"Block {new_block.index} added to main chain.")
            return True
        
        # Check if this block extends any existing chain (main or side)
        if new_block.prev_hash in self.block_map:
            parent_block = self.block_map[new_block.prev_hash]
            
            # Check if parent is in main chain
            if self._is_in_main_chain(new_block.prev_hash):
                # This creates a side chain at the fork point
                self.side_chains[new_block.block_id] = [new_block]
                self.block_map[new_block.block_id] = new_block
                print(f"Side chain detected. Storing block {new_block.index}.")
            else:
                # Parent is in a side chain, extend it
                for chain_tip, chain in list(self.side_chains.items()):
                    if chain[-1].block_id == new_block.prev_hash:
                        chain.append(new_block)
                        self.block_map[new_block.block_id] = new_block
                        print(f"Block {new_block.index} extends side chain.")
                        break
            
            # Check if reorganization is needed
            self._check_and_reorganize()
            return False
        
        # Orphan block (parent not found) - could be stored for later
        print(f"Block {new_block.index} is orphaned (parent {new_block.prev_hash} not found).")
        return False

    def _is_in_main_chain(self, block_id):
        """Check if a block_id is in the main chain."""
        for block in self.main_chain:
            if block.block_id == block_id:
                return True
        return False

    def _check_and_reorganize(self):
        """
        Check if any side chain is longer than or equal to main chain.
        If so, perform chain reorganization (reorg).
        """
        if not self.side_chains:
            return
        
        # Find longest side chain
        longest_side_chain = None
        longest_length = 0
        longest_tip = None
        
        for chain_tip, chain in self.side_chains.items():
            if len(chain) > longest_length:
                longest_length = len(chain)
                longest_side_chain = chain
                longest_tip = chain_tip
        
        # If a side chain is longer than main chain, reorganize
        if longest_side_chain and longest_length >= len(self.main_chain):
            # Find common ancestor
            common_ancestor_idx = self._find_common_ancestor(longest_side_chain[0].prev_hash)
            
            print(f"\n--- CHAIN REORGANIZATION (REORG) ---")
            print(f"Main chain length: {len(self.main_chain)}")
            print(f"Side chain length: {longest_length}")
            print(f"Common ancestor at main chain index: {common_ancestor_idx}\n")
            
            # Rollback main chain blocks after fork point
            blocks_to_rollback = self.main_chain[common_ancestor_idx + 1:]
            self._rollback_blocks(blocks_to_rollback)
            print(f"Rolled back {len(blocks_to_rollback)} blocks from main chain.")
            
            # Truncate main chain at fork point
            self.main_chain = self.main_chain[:common_ancestor_idx + 1]
            
            # Apply side chain blocks to UTXO manager
            for block in longest_side_chain:
                self._apply_block_to_utxo(block)
            
            # Promote side chain to main chain
            self.main_chain.extend(longest_side_chain)
            
            # Remove this side chain
            del self.side_chains[longest_tip]
            
            print(f"Main chain updated. New tip: {self.main_chain[-1].block_id}")
            print(f"--- END REORG ---\n")

    def _find_common_ancestor(self, block_id):
        """
        Find the index of common ancestor between a side chain and main chain.
        Returns index in main_chain where fork occurred.
        """
        current_id = block_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            # Check if current_id is in main chain
            for idx, main_block in enumerate(self.main_chain):
                if main_block.block_id == current_id:
                    return idx
            
            # Move to parent block
            if current_id in self.block_map:
                current_id = self.block_map[current_id].prev_hash
            else:
                break
        
        return -1  # No common ancestor (shouldn't happen)

    def _apply_block_to_utxo(self, block):
        """Apply a block's transactions to the UTXO manager."""
        for tx in block.transactions:
            # Remove spent inputs
            for inp in tx.inputs:
                self.utxo_manager.remove_utxo(inp.prev_tx, inp.index)
            
            # Add new outputs
            for i, out in enumerate(tx.outputs):
                self.utxo_manager.add_utxo(tx.tx_id, i, out.amount, out.address)

    def _rollback_blocks(self, blocks):
        """
        Rollback blocks by reversing their UTXO changes.
        Removes outputs and re-adds spent inputs.
        """
        for block in reversed(blocks):
            # Rollback transactions in reverse order
            for tx in reversed(block.transactions):
                # Remove outputs added by this transaction
                for i, out in enumerate(tx.outputs):
                    self.utxo_manager.remove_utxo(tx.tx_id, i)
                
                # Re-add spent inputs from previous blocks
                for inp in tx.inputs:
                    # Find the UTXO in the remaining main chain
                    utxo_data = self._find_utxo_before_fork(inp.prev_tx, inp.index)
                    if utxo_data:
                        amount, owner = utxo_data
                        self.utxo_manager.add_utxo(inp.prev_tx, inp.index, amount, owner)
            
            # Remove coinbase reward
            coinbase_id = f"coinbase_{block.block_id}"
            self.utxo_manager.remove_utxo(coinbase_id, 0)

    def _find_utxo_before_fork(self, tx_id, index):
        """Find a UTXO in the current main chain."""
        for block in self.main_chain:
            for tx in block.transactions:
                if tx.tx_id == tx_id and index < len(tx.outputs):
                    return (tx.outputs[index].amount, tx.outputs[index].address)
        return None

    def get_main_chain_tip(self):
        return self.main_chain[-1].block_id if self.main_chain else "0"
