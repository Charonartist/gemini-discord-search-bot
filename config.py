import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Gemini Discord Search Bot"""
    
    # Discord Configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Bot Configuration
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    
    # Search Configuration
    MAX_SEARCH_QUERIES = int(os.getenv('MAX_SEARCH_QUERIES', '3'))
    AUTO_SEARCH_MIN_LENGTH = int(os.getenv('AUTO_SEARCH_MIN_LENGTH', '10'))
    
    # Memory Configuration
    CONTEXT_HOURS = int(os.getenv('CONTEXT_HOURS', '24'))
    CONTEXT_LIMIT = int(os.getenv('CONTEXT_LIMIT', '5'))
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'conversation_memory.db')
    
    # Response Configuration
    MAX_RESPONSE_LENGTH = int(os.getenv('MAX_RESPONSE_LENGTH', '2000'))
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1900'))
    
    # Gemini Generation Configuration
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    TOP_P = float(os.getenv('TOP_P', '0.8'))
    TOP_K = int(os.getenv('TOP_K', '40'))
    MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', '2048'))
    
    # Cleanup Configuration
    CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', '30'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = ['DISCORD_TOKEN', 'GEMINI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_gemini_config(cls):
        """Get Gemini generation configuration"""
        return {
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P,
            "top_k": cls.TOP_K,
            "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
        }