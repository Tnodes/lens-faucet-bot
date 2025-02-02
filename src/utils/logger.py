from datetime import datetime
from typing import Optional, Dict
import os
import json

class Logger:
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'gray': '\033[90m'
    }
    
    # Log file paths
    SUCCESS_LOG = "src/logs/success.txt"
    FAILED_LOG = "src/logs/failed.txt"
    

    @staticmethod
    def _ensure_log_dir():
        """Ensure the logs directory exists."""
        os.makedirs("logs", exist_ok=True)
    
    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now().strftime('%H:%M:%S')
    
    @staticmethod
    def _get_full_timestamp() -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def _format_msg(color: str, prefix: str, message: str) -> str:
        timestamp = Logger._get_timestamp()
        return f"{Logger.COLORS[color]}[{timestamp}] {prefix} | {message}{Logger.COLORS['reset']}"
    
    @staticmethod
    def _log_to_file(filepath: str, data: Dict):
        """Log data to specified file."""
        Logger._ensure_log_dir()
        data['timestamp'] = Logger._get_full_timestamp()
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data) + '\n')
    
    @staticmethod
    def log_success(data: Dict):
        """Log successful attempt to file."""
        Logger._log_to_file(Logger.SUCCESS_LOG, data)
    
    @staticmethod
    def log_failed(data: Dict):
        """Log failed attempt to file."""
        Logger._log_to_file(Logger.FAILED_LOG, data)
    
    @staticmethod
    def info(message: str):
        """Log info message in blue"""
        print(Logger._format_msg('blue', 'INFO', message))
    
    @staticmethod
    def success(message: str):
        """Log success message in green"""
        print(Logger._format_msg('green', 'SUCCESS', message))
    
    @staticmethod
    def error(message: str):
        """Log error message in red"""
        print(Logger._format_msg('red', 'ERROR', message))
    
    @staticmethod
    def warning(message: str):
        """Log warning message in yellow"""
        print(Logger._format_msg('yellow', 'WARNING', message))
    
    @staticmethod
    def proxy(message: str):
        """Log proxy message in purple"""
        print(Logger._format_msg('purple', 'PROXY', message))
    
    @staticmethod
    def wallet(message: str):
        """Log wallet message in cyan"""
        print(Logger._format_msg('cyan', 'WALLET', message))
    
    @staticmethod
    def debug(message: str):
        """Log debug message in gray"""
        print(Logger._format_msg('gray', 'DEBUG', message))
    
    @staticmethod
    def maze(message: str):
        """Log maze-related message in yellow"""
        print(Logger._format_msg('yellow', 'MAZE', message))
    
    @staticmethod
    def tx(hash: str, url: Optional[str] = None):
        """Log transaction info in green"""
        print(Logger._format_msg('green', 'TX', f"Hash: {hash}"))
        if url:
            print(Logger._format_msg('green', 'TX', f"URL: {url}")) 