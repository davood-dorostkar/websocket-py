import asyncio
import websockets
import json


class WebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.counter = 0  # Global counter variable
        self.websocket_connection = None  # Store the WebSocket connection

    async def start(self):
        """
        Starts the WebSocket server and listens for connections.
        """
        print(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        server = await websockets.serve(self.handle_connection, self.host, self.port)
        await server.wait_closed()

    async def handle_connection(self, websocket):
        """
        Handles the WebSocket connection, including HTTP upgrade and WebSocket message processing.
        """
        try:
            # Receive the initial message for connection establishment
            message = await websocket.recv()
            data = json.loads(message)

            if data.get("type") == "establish_connection":
                print("HTTP request received: Establishing WebSocket connection...")
                self.websocket_connection = websocket
                await websocket.send(json.dumps({"status": "connection_established"}))
                self.counter = 0

                # Start the counter loop and listen for WebSocket messages concurrently
                await asyncio.gather(self.counter_loop(), self.handle_websocket_requests(websocket))

        except Exception as e:
            print(f"Connection handler error: {e}")

    async def counter_loop(self):
        """
        Continuously sends the counter value to the client every 3 seconds.
        """
        try:
            while self.websocket_connection:
                await asyncio.sleep(3)
                self.counter += 1
                await self.websocket_connection.send(json.dumps({"type": "counter", "value": self.counter}))
        except websockets.ConnectionClosed:
            print("Client disconnected. Stopping counter loop.")
            self.websocket_connection = None

    async def handle_websocket_requests(self, websocket):
        """
        Listens for messages from the client and handles them based on request type.
        """
        try:
            async for message in websocket:
                data = json.loads(message)
                request_type = data.get("type")

                if request_type == "reset_counter":
                    await self.handle_reset_counter(websocket)
                elif request_type == "custom_task":
                    await self.handle_custom_task(websocket, data)
                elif request_type == "get_status":
                    await self.handle_get_status(websocket)
                else:
                    print(f"Unknown request type: {request_type}")
                    await websocket.send(json.dumps({"error": "Unknown request type"}))

        except websockets.ConnectionClosed:
            print("WebSocket connection closed.")

    async def handle_reset_counter(self, websocket):
        """
        Resets the counter and notifies the client.
        """
        print("Reset request received. Counter reset to 0.")
        self.counter = 0
        await websocket.send(json.dumps({"status": "counter_reset"}))

    async def handle_custom_task(self, websocket, data):
        """
        Performs a custom task based on client input.
        """
        task_name = data.get("task_name", "default_task")
        print(f"Performing custom task: {task_name}")
        # Simulate a task
        await asyncio.sleep(2)
        await websocket.send(json.dumps({"status": "custom_task_completed", "task_name": task_name}))

    async def handle_get_status(self, websocket):
        """
        Sends the current status of the server to the client.
        """
        status = {
            "status": "running",
            "counter_value": self.counter,
        }
        print("Sending status to client.")
        await websocket.send(json.dumps({"type": "status_update", "data": status}))


if __name__ == "__main__":
    server = WebSocketServer()
    asyncio.run(server.start())
