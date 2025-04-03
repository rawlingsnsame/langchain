import asyncio
import json
import ssl
import websockets
from websockets.exceptions import ConnectionClosed
import logging
import uuid
import time
import re
from mainbot import chatbot
from urllib.parse import urlparse, parse_qs

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('chatbot-websocket')

# This is a placeholder for your actual chatbot function
async def process_question(question):
    """
    Replace this with your actual LLM-based PDF chatbot function.
    This should handle the processing of the question and return a response.
    """
    # Simulate some processing time
    await asyncio.sleep(1)
    return f"Here is the answer to: {question}"


class RoutedWebSocketServer:
    def __init__(self, host="0.0.0.0", port=10000):
        self.host = host
        self.port = port
        self.clients = {}  
        self.rate_limits = {}  #

        self.routes = {
            '/chat': self.handle_chat,
            '/status': self.handle_status,
        }
        
    async def router(self, websocket):
        """Main router that delegates to specific handlers based on path"""
        # Extract the base path and query parameters
        path = websocket.request.path
        parsed_url = urlparse(path)
        base_path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        handler = self.routes.get(base_path)
        
        if handler:
            await handler(websocket, query_params)
        else:
            logger.warning(f"Unknown path requested: {base_path}")
            try:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown endpoint: {base_path}"
                }))
            except Exception as e:
                logger.error(f"Error sending error message: {str(e)}")
            finally:
                if not websocket.closed:
                    await websocket.close(1008, "Endpoint not found")
                    
    async def handle_chat(self, websocket, query_params=None):
        """Handler for the /chat endpoint"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = {"socket": websocket, "endpoint": "/chat"}
        
        try:
            logger.info(f"Client {client_id} connected to /chat endpoint")
            await self.send_message(websocket, {"type": "connection", "status": "established", "endpoint": "/chat"})
            
            async for message in websocket:
                try:
                    # Rate limiting
                    if not self.check_rate_limit(client_id):
                        await self.send_message(websocket, {
                            "type": "error", 
                            "message": "Rate limit exceeded. Please wait for 2 minute before sending more requests."
                        })
                        continue
                    
                    data = json.loads(message)
                    
                    if 'type' not in data or 'data' not in data:
                        await self.send_message(websocket, {
                            "type": "error", 
                            "message": "Invalid message format"
                        })
                        continue
                    
                    if data['type'] == 'question':
                        await self.handle_question(websocket, data['data'])
                    else:
                        await self.send_message(websocket, {
                            "type": "error", 
                            "message": f"Unsupported message type: {data['type']}"
                        })
                        
                except json.JSONDecodeError:
                    await self.send_message(websocket, {
                        "type": "error", 
                        "message": "Invalid JSON message"
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await self.send_message(websocket, {
                        "type": "error", 
                        "message": "Server error processing your request"
                    })
                    
        except ConnectionClosed:
            logger.info(f"Client {client_id} disconnected from /chat endpoint")
        finally:

            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.rate_limits:
                del self.rate_limits[client_id]
    
    async def handle_status(self, websocket, query_params=None):
        """Handler for the /status endpoint - system status and metrics"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = {"socket": websocket, "endpoint": "/status"}
        
        try:
            logger.info(f"Client {client_id} connected to /status endpoint")
            await self.send_message(websocket, {"type": "connection", "status": "established", "endpoint": "/status"})
            
            await self.send_system_status(websocket)
            
            # Keep the connection alive and periodically send updates
            while True:
                await asyncio.sleep(10)  # Send updates every 10 seconds
                await self.send_system_status(websocket)
                
        except ConnectionClosed:
            logger.info(f"Client {client_id} disconnected from /status endpoint")
        finally:

            if client_id in self.clients:
                del self.clients[client_id]
    
    async def send_system_status(self, websocket):
        """Send system status information"""
        # Count clients by endpoint
        endpoint_counts = {}
        for client in self.clients.values():
            endpoint = client.get("endpoint", "unknown")
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        status = {
            "type": "status_update",
            "data": {
                "active_connections": len(self.clients),
                "connections_by_endpoint": endpoint_counts,
                # "server_uptime": time.time(), 
                "timestamp": time.time()
            }
        }
        
        await self.send_message(websocket, status)
    
    async def handle_question(self, websocket, question_data):
        """Process a question from the client."""
        if not isinstance(question_data, dict) or 'question' not in question_data:
            await self.send_message(websocket, {
                "type": "error", 
                "message": "Invalid question format"
            })
            return
            
        question = question_data['question']
        
        # Send acknowledgment
        await self.send_message(websocket, {
            "type": "status", 
            "message": "Processing your question..."
        })
        
        try:
            # response = await process_question(question)
            response = await chatbot(question)
            # response = "This is a response"
            
            await self.send_message(websocket, {
                "type": "answer",
                "data": {
                    "question": question,
                    "answer": response,
                    "timestamp": time.time()
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            await self.send_message(websocket, {
                "type": "error", 
                "message": "Error processing your question"
            })
    
    async def send_message(self, websocket, message):
        """Send a JSON message to a client."""
        await websocket.send(json.dumps(message))
    
    def check_rate_limit(self, client_id, max_requests=10, window_seconds=60):
        """Simple rate limiting implementation."""
        current_time = time.time()
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {"count": 1, "window_start": current_time}
            return True
            
        client_data = self.rate_limits[client_id]
        
        # Reset window if it's expired
        if current_time - client_data["window_start"] > window_seconds:
            client_data["count"] = 1
            client_data["window_start"] = current_time
            return True
            
        if client_data["count"] >= max_requests:
            return False
            
        client_data["count"] += 1
        return True
    
    async def start(self):
        """Start the WebSocket server."""
        # SSL context for secure WebSockets (wss://)
        ssl_context = None
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain('cert.pem', 'key.pem')
            logger.info("SSL certificates loaded successfully")
        except FileNotFoundError:
            logger.warning("SSL certificates not found, running in unsecured mode")
            ssl_context = None
        
        # Start the server
        server = await websockets.serve(
            self.router,
            self.host, 
            self.port,
            ssl=ssl_context
        )
        
        logger.info(f"WebSocket server with path routing started on {self.host}:{self.port}")
        return server

async def main():
    server = RoutedWebSocketServer()
    ws_server = await server.start()
    await ws_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())