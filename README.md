# Lens Protocol Testnet Faucet Bot

An automated bot for claiming tokens from the Lens Protocol testnet faucet. The bot solves maze challenges and handles Cloudflare Turnstile captchas automatically.

## Features

- 🎮 Automated maze solving using A* pathfinding algorithm
- 🔄 Proxy support with rotation
- 👛 Multiple wallet support
- 🤖 Automatic Cloudflare Turnstile captcha solving (via 2captcha)
- 📝 Detailed logging with colored output
- ⏱️ Configurable wait times between attempts

## Prerequisites

- Python 3.8 or higher
- A 2captcha.com API key (optional but recommended)
- Proxies (optional)
- EVM wallet addresses

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tnodes/lens-faucet-bot.git
cd lens-faucet-bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the root directory:
```env
# Your 2captcha API key (optional)
TWOCAPTCHA_API_KEY=your_api_key_here

# Wait time between attempts in seconds
WAIT_TIME=60

# Don't change these
TURNSTILE_SITEKEY=0x4AAAAAAA1z6BHznYZc0TNL
PAGE_URL=https://testnet.lenscan.io/faucet
```

2. Add your wallet addresses to `wallet.txt`:
```
# One wallet address per line
0x1234567890123456789012345678901234567890
0xabcdef0123456789abcdef0123456789abcdef01
```

3. (Optional) Add your proxies to `proxy.txt`:
```
# Format: protocol://username:password@host:port
http://user:pass@proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
```

## Usage

Run the bot using either:
```bash
python run.py
```

The bot will:
1. Load your configuration
2. Initialize the captcha solver if configured
3. Start attempting to claim tokens by:
   - Getting and solving mazes
   - Solving Cloudflare Turnstile captchas
   - Submitting solutions and claiming tokens
4. Wait for the configured time between attempts
5. Log all activities and results

## Logging

The bot maintains two log files in the `logs` directory:
- `success.txt`: Records successful claims with transaction details
- `failed.txt`: Records failed attempts with error information

## Project Structure

```
├── run.py                 # Entry point
├── requirements.txt       # Python dependencies
├── .env                   # Configuration file
├── wallet.txt            # Wallet addresses
├── proxy.txt             # Proxy list
├── src/
│   ├── main.py           # Main program logic
│   ├── core/
│   │   └── solver.py     # Maze solving algorithm
│   ├── models/
│   │   └── maze.py       # Data models
│   ├── services/
│   │   └── api_client.py # API interaction
│   └── utils/
│       ├── banner.py     # ASCII banner
│       ├── logger.py     # Logging utilities
│       ├── proxy_manager.py    # Proxy handling
│       └── wallet_manager.py   # Wallet handling
```

## Error Handling

The bot includes comprehensive error handling for:
- Network issues
- Invalid proxies
- API errors
- Captcha solving failures
- Invalid wallet addresses

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Disclaimer

This bot is for educational purposes only. Use at your own risk and make sure to comply with the Lens Protocol's terms of service. 