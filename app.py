import os
import logging
from dotenv import load_dotenv
from sentient_agent_framework import DefaultServer
from github_agent.agent import GitHubSummaryAgent
from github_agent.identity import AGENT_DID
from github_agent.utils.execution_logger import ExecutionLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize execution logger
        execution_logger = ExecutionLogger()
        logger.info(f"Starting GitHub Summary Agent with DID: {AGENT_DID}")
        
        # Initialize the agent with execution logger
        agent = GitHubSummaryAgent(
            execution_logger=execution_logger
        )
        
        # Get port from environment variable or use default
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"Agent server starting on {host}:{port}")
        
        # Start the server
        server = DefaultServer(agent)
        server.run(host=host, port=port)
        
    except Exception as e:
        logger.error(f"Failed to start agent server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
