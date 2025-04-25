import logging as log
import os

class Logger:

    def __init__(self, log_file="/app/logs/dash_api.log", level=log.INFO):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        log.basicConfig(
            level=level,
            format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s',
            datefmt='%I:%M:%S %p',
            handlers=[log.StreamHandler(), log.FileHandler(log_file)]
        )
        self.logger = log.getLogger()
    
    def debug(self, message):
        """Log a message with severity 'DEBUG' on the logger"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log a message with severity 'INFO' on the logger"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a message with severity 'WARNING' on the logger"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log a message with severity 'ERROR' on the logger"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log a message with severity 'CRITICAL' on the logger"""
        self.logger.critical(message)