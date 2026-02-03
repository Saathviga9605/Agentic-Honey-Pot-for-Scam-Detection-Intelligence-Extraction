"""
Main Application Entry Point
Initializes and runs the Agentic Honeypot System
"""

import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'intelligence-engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api-gateway'))

from bridge import create_scam_detector_bridge, create_agent_interface
from reporter import intelligence_reporter
from main import create_api_gateway


def main():
    """
    Initialize and run the honeypot system
    """
    logger.info("=" * 60)
    logger.info("Starting Agentic Honeypot for Scam Detection System")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("Initializing system components...")
    
    # 1. Scam Detector Bridge
    scam_detector = create_scam_detector_bridge()
    logger.info("[OK] Scam Detector Bridge initialized")
    
    # 2. Intelligence Engine
    intelligence_engine = intelligence_reporter
    logger.info("[OK] Intelligence Engine initialized")
    
    # 3. Agent Interface (optional - mock for now)
    agent_interface = create_agent_interface()
    logger.info("[OK] Agent Interface initialized")
    
    # 4. API Gateway
    api_gateway = create_api_gateway(
        scam_detector=scam_detector,
        intelligence_engine=intelligence_engine,
        agent_interface=agent_interface
    )
    logger.info("[OK] API Gateway initialized")
    
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info("")
    logger.info("System Configuration:")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug: {debug}")
    logger.info("")
    logger.info("API Endpoints:")
    logger.info(f"  POST http://{host}:{port}/ingest-message")
    logger.info(f"  GET  http://{host}:{port}/health")
    logger.info(f"  GET  http://{host}:{port}/sessions")
    logger.info("")
    logger.info("Authentication:")
    logger.info("  Header: x-api-key")
    logger.info("")
    logger.info("=" * 60)
    logger.info("System ready! Starting Flask server...")
    logger.info("=" * 60)
    
    # Run the application
    try:
        api_gateway.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()