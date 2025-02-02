from typing import Optional, List
import random
from src.utils.logger import Logger

class WalletManager:
    def __init__(self, wallet_file: str = "wallet.txt"):
        """Initialize the wallet manager."""
        self.wallet_file = wallet_file
        self.wallets: List[str] = []
        self.load_wallets()
        
    def load_wallets(self):
        """Load wallets from the wallet file."""
        try:
            with open(self.wallet_file, 'r') as f:
                self.wallets = [line.strip() for line in f.readlines() if line.strip()]
            Logger.info(f"Loaded {len(self.wallets)} wallets")
        except FileNotFoundError:
            Logger.warning(f"Warning: Wallet file {self.wallet_file} not found")
            self.wallets = []
            
    def get_random_wallet(self) -> Optional[str]:
        """Get a random wallet from the list."""
        return random.choice(self.wallets) if self.wallets else None
        
    def get_next_wallet(self) -> Optional[str]:
        """Get the next wallet in sequence (cycles through the list)."""
        if not self.wallets:
            return None
        wallet = self.wallets.pop(0)
        self.wallets.append(wallet)
        return wallet 