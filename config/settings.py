import os

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
LLM_BACKEND = os.getenv('LLM_BACKEND', 'llama')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
