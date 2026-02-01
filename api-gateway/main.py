"""
API Gateway Main Module
Exposes REST endpoint for message ingestion
"""

from flask import Flask, request, jsonify
import logging
from typing import Dict, Any
from auth import validate_api_key, get_authentication_error
from session_manager import session_manager
from router import create_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIGateway:
    """API Gateway for handling incoming requests"""
    
    def __init__(self, scam_detector, intelligence_engine, agent_interface=None):
        """
        Initialize API Gateway
        
        Args:
            scam_detector: Scam detection module
            intelligence_engine: Intelligence extraction module
            agent_interface: Optional agent for generating replies
        """
        self.app = Flask(__name__)
        self.router = create_router(scam_detector, intelligence_engine, agent_interface)
        self._register_routes()
        logger.info("API Gateway initialized")
    
    def _register_routes(self):
        """Register all API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "active_sessions": session_manager.get_active_sessions_count()
            }), 200
        
        @self.app.route('/ingest-message', methods=['POST'])
        def ingest_message():
            """Main message ingestion endpoint"""
            return self._handle_ingest_message()
        
        @self.app.route('/sessions', methods=['GET'])
        def list_sessions():
            """List all active sessions (admin endpoint)"""
            api_key = request.headers.get('x-api-key')
            if not validate_api_key(api_key):
                return jsonify(get_authentication_error()), 401
            
            return jsonify({
                "status": "success",
                "sessions": session_manager.get_session_summary()
            }), 200
    
    def _handle_ingest_message(self) -> tuple:
        """
        Handle incoming message ingestion
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        # Step 1: Authenticate
        api_key = request.headers.get('x-api-key')
        if not validate_api_key(api_key):
            logger.warning("Authentication failed")
            return jsonify(get_authentication_error()), 401
        
        # Step 2: Validate payload
        try:
            payload = request.get_json()
            validation_error = self._validate_payload(payload)
            if validation_error:
                logger.warning(f"Validation failed: {validation_error}")
                return jsonify({
                    "status": "error",
                    "message": validation_error
                }), 400
        except Exception as e:
            logger.error(f"Payload parsing error: {e}")
            return jsonify({
                "status": "error",
                "message": "Invalid JSON payload"
            }), 400
        
        # Step 3: Process message through router
        try:
            response = self.router.process_message(payload)
            logger.info(f"[{payload.get('sessionId')}] Message processed successfully")
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500
    
    def _validate_payload(self, payload: Dict[str, Any]) -> str:
        """
        Validate incoming payload
        
        Args:
            payload: Request payload
            
        Returns:
            Error message if invalid, empty string if valid
        """
        if not payload:
            return "Empty payload"
        
        if "sessionId" not in payload:
            return "Missing sessionId"
        
        if "message" not in payload:
            return "Missing message"
        
        message = payload["message"]
        if not isinstance(message, dict):
            return "Message must be an object"
        
        if "sender" not in message:
            return "Message missing sender"
        
        if "text" not in message:
            return "Message missing text"
        
        return ""
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting API Gateway on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def get_app(self):
        """Get Flask app instance for WSGI servers"""
        return self.app


def create_api_gateway(scam_detector, intelligence_engine, agent_interface=None):
    """Factory function to create API Gateway"""
    return APIGateway(scam_detector, intelligence_engine, agent_interface)
