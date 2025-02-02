from curl_cffi import requests
from typing import Optional, Dict, List
from src.utils.proxy_manager import ProxyManager
from src.utils.wallet_manager import WalletManager
from src.utils.captcha_solver import CaptchaSolver
from src.utils.logger import Logger
from src.core.solver import MazeSolver
from src.models.maze import MazeData, MazeSolution
import os

class LensFaucetClient:
    def __init__(self, proxy_file: str = "proxy.txt", wallet_file: str = "wallet.txt"):
        """Initialize the Lens Faucet client with proxy and wallet support."""
        self.proxy_manager = ProxyManager(proxy_file)
        self.wallet_manager = WalletManager(wallet_file)
        self.base_url = "https://testnet.lenscan.io/api/trpc"
        self.captcha_solver = None
        
    def set_captcha_solver(self, api_key: str):
        """Set up the captcha solver with an API key."""
        self.captcha_solver = CaptchaSolver(api_key)
    
    def get_maze(self, difficulty: str = "hard") -> Optional[MazeData]:
        """
        Fetch a maze from the Lens API.
        
        Args:
            difficulty: Maze difficulty level ("easy" or "hard")
            
        Returns:
            MazeData object containing the maze walls and session ID if successful,
            None otherwise
        """
        # Construct the exact query parameters
        query_params = f"batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22difficulty%22%3A%22{difficulty}%22%7D%7D%7D"
        url = f"{self.base_url}/faucet.getMaze?{query_params}"
        
        try:
            # Get a random proxy
            proxy = self.proxy_manager.get_next_proxy()
            if proxy:
                Logger.proxy(f"Using: {proxy['http']}")
            
            # Make the request
            response = requests.get(
                url,
                proxies=proxy,
                timeout=10
            )
            response.raise_for_status()
            
            # Get the response data
            result = response.json()
            # print(f"Raw API Response: {result}")  # Debug print
            # Parse the response
            try:
                # The response format is different, let's handle both possible formats
                if isinstance(result, dict) and "result" in result:
                    maze_info = result["result"]["data"]["json"]
                else:
                    # Try the array format
                    maze_info = result[0]["result"]["data"]["json"]
                
                return MazeData(
                    walls=maze_info["walls"],
                    session_id=maze_info["sessionId"],
                    goal_pos=(maze_info["goalPos"]["row"], maze_info["goalPos"]["col"])
                )
            except (KeyError, IndexError, TypeError) as e:
                Logger.error(f"Error parsing response: {e}")
                Logger.debug(f"Response data: {result}")
                return None
            
        except requests.exceptions.RequestException as e:
            Logger.error(f"Error fetching maze: {e}")
            return None
    
    def solve_maze(self, maze_data: MazeData) -> Optional[List[str]]:
        """
        Solve the given maze using A* algorithm.
        
        Args:
            maze_data: MazeData object containing the maze to solve
            
        Returns:
            List of moves ("up", "down", "left", "right") if solution found,
            None otherwise
        """
        return MazeSolver.solve(maze_data)
    
    def claim_faucet(self, session_id: str, moves: List[str], use_random_wallet: bool = False) -> Optional[Dict]:
        """
        Claim tokens from the faucet using solved maze data.
        
        Args:
            session_id: Maze session ID
            moves: List of moves that solve the maze
            use_random_wallet: Whether to use a random wallet or next in sequence
            
        Returns:
            Response from the claim API if successful, None otherwise
        """
        # Get wallet address
        address = (self.wallet_manager.get_random_wallet() if use_random_wallet 
                  else self.wallet_manager.get_next_wallet())
        
        if not address:
            Logger.error("No wallet address available!")
            return None
            
        Logger.wallet(f"Using address: {address}")
        
        # Solve Cloudflare Turnstile captcha if solver is configured
        captcha_token = None
        if self.captcha_solver:
            Logger.info("Solving Cloudflare Turnstile captcha...")
            captcha_token = self.captcha_solver.solve_turnstile(
                sitekey=os.getenv("TURNSTILE_SITEKEY", "0x4AAAAAAA1z6BHznYZc0TNL"),
                url=os.getenv("PAGE_URL", "https://testnet.lenscan.io/faucet")
            )
            if not captcha_token:
                Logger.error("Failed to solve captcha!")
                Logger.log_failed({
                    "wallet": address,
                    "reason": "captcha_failed",
                    "session_id": session_id
                })
                return None

        url = f"{self.base_url}/faucet.claim?batch=1"
        
        payload = {
            "0": {
                "json": {
                    "address": address,
                    "cfToken": captcha_token,
                    "gameChallenge": {
                        "sessionId": session_id,
                        "moves": moves
                    }
                }
            }
        }
        
        try:
            # Get next best proxy
            proxy = self.proxy_manager.get_next_proxy()
            current_proxy_url = proxy['http'][7:] if proxy else None  # Remove 'http://' prefix
            
            if proxy:
                Logger.proxy(f"Using: {proxy['http']}")
            
            # Make the claim request
            response = requests.post(
                url,
                json=payload,
                proxies=proxy,
                timeout=10
            )
            
            try:
                result = response.json()
            except ValueError:
                Logger.error(f"Invalid JSON response: {response.text[:200]}")  # Show first 200 chars
                Logger.log_failed({
                    "wallet": address,
                    "reason": "invalid_json",
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "session_id": session_id,
                    "proxy": current_proxy_url
                })
                return None
            
            # Check for HTTP errors
            if not response.ok:
                error_msg = f"HTTP {response.status_code}"
                error_detail = None
                
                if isinstance(result, list) and len(result) > 0:
                    error = result[0].get("error", {})
                    if error:
                        error_code = error.get("code", "UNKNOWN")
                        error_message = error.get("message", "Unknown error")
                        error_msg = f"{error_msg}: [{error_code}] {error_message}"
                        error_detail = error
                elif isinstance(result, dict):
                    error_msg = f"{error_msg}: {result.get('message', 'Unknown error')}"
                    error_detail = result
                
                Logger.error(f"Request failed: {error_msg}")
                if error_detail:
                    Logger.debug(f"Error details: {error_detail}")
                
                Logger.log_failed({
                    "wallet": address,
                    "reason": "http_error",
                    "status_code": response.status_code,
                    "error": error_msg,
                    "error_detail": error_detail,
                    "session_id": session_id,
                    "proxy": current_proxy_url
                })
                return None
            
            # Format the response nicely
            if result and isinstance(result, list) and len(result) > 0:
                data = result[0].get("result", {}).get("data", {}).get("json", {})
                error = result[0].get("error")
                
                if error:
                    error_code = error.get("code", "UNKNOWN")
                    error_message = error.get("message", "Unknown error")
                    Logger.error(f"API Error: [{error_code}] {error_message}")
                    Logger.log_failed({
                        "wallet": address,
                        "reason": "api_error",
                        "error_code": error_code,
                        "error_message": error_message,
                        "session_id": session_id,
                        "proxy": current_proxy_url
                    })
                    return None
                
                if data.get("success") and data.get("hash"):
                    tx_hash = data["hash"]
                    tx_url = f"https://testnet.lenscan.io/tx/{tx_hash}"
                    
                    # Log successful attempt
                    Logger.log_success({
                        "wallet": address,
                        "tx_hash": tx_hash,
                        "tx_url": tx_url,
                        "session_id": session_id,
                        "proxy": current_proxy_url
                    })
                    
                    return {
                        "success": True,
                        "wallet": address,
                        "transaction_hash": tx_hash,
                        "transaction_url": tx_url
                    }
            
            # Log failed attempt with raw response for debugging
            Logger.error("Unexpected API response format")
            Logger.debug(f"Raw response: {result}")
            Logger.log_failed({
                "wallet": address,
                "reason": "invalid_response",
                "session_id": session_id,
                "proxy": current_proxy_url,
                "response": result
            })
            return None
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            response = getattr(e, 'response', None)
            
            if response is not None:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, list) and len(error_data) > 0:
                        error = error_data[0].get("error", {})
                        if error:
                            error_code = error.get("code", "UNKNOWN")
                            error_message = error.get("message", "Unknown error")
                            error_msg = f"{error_msg}: [{error_code}] {error_message}"
                    elif isinstance(error_data, dict):
                        error_msg = f"{error_msg}: {error_data.get('message', str(e))}"
                except ValueError:
                    error_msg = f"{error_msg}: {response.text[:200]}"  # Show first 200 chars
            
            Logger.error(f"Request failed: {error_msg}")
            Logger.log_failed({
                "wallet": address,
                "reason": "request_error",
                "error": error_msg,
                "response_text": response.text if response else None,
                "status_code": response.status_code if response else None,
                "session_id": session_id,
                "proxy": current_proxy_url
            })
            return None
    
    def get_and_solve_maze(self, difficulty: str = "hard") -> Optional[MazeSolution]:
        """
        Convenience method to get a maze and solve it in one step.
        
        Returns:
            MazeSolution object containing the solution moves and session ID if successful,
            None otherwise
        """
        maze_data = self.get_maze(difficulty)
        if not maze_data:
            return None
            
        solution = self.solve_maze(maze_data)
        if not solution:
            return None
            
        return MazeSolution(
            moves=solution,
            session_id=maze_data.session_id
        ) 