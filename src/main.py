from src.services.api_client import LensFaucetClient
from src.utils.logger import Logger
from dotenv import load_dotenv
from src.utils.banner import print_banner
import os
import time

def main():
    # Load environment variables from .env file
    load_dotenv()
    print_banner()
    
    # Initialize the client with proxy and wallet support
    client = LensFaucetClient(proxy_file="proxy.txt", wallet_file="wallet.txt")
    
    # Set up captcha solver if API key is available
    captcha_api_key = os.getenv('TWOCAPTCHA_API_KEY')
    if captcha_api_key:
        client.set_captcha_solver(captcha_api_key)
        Logger.info("Captcha solver initialized")
    
    attempt_count = 0
    
    while True:
        attempt_count += 1
        Logger.info(f"Starting attempt #{attempt_count}")
        
        # Get and solve a hard maze
        Logger.maze("Getting and solving hard maze...")
        result = client.get_and_solve_maze(difficulty="hard")
        
        if result:
            Logger.maze("Solution found!")
            Logger.debug(f"Session ID: {result.session_id}")
            Logger.debug(f"Moves: {', '.join(result.moves)}")
            
            Logger.info("Claiming faucet...")
            claim_result = client.claim_faucet(
                session_id=result.session_id,
                moves=result.moves,
                use_random_wallet=False  # Set to True if you want random wallet selection
            )
            
            if claim_result:
                Logger.success("Claim successful!")
                Logger.wallet(f"Address: {claim_result['wallet']}")
                Logger.tx(claim_result['transaction_hash'], claim_result['transaction_url'])
            else:
                Logger.error("Claim failed!")
        else:
            Logger.error("Failed to get or solve maze")
            
        # Wait before next attempt
        wait_time = int(os.getenv('WAIT_TIME', '300'))  # Default to 300 seconds if not set
        Logger.info(f"Waiting {wait_time} seconds before next attempt...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main() 