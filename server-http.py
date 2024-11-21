import asyncio
import websockets
import json

counter = 0  # Global counter variable
websocket_connection = None  # Store the WebSocket connection


async def handle_http(websocket, path):
    global websocket_connection, counter

    # First, handle the HTTP upgrade request
    try:
        message = await websocket.recv()
        data = json.loads(message)

        if data.get("type") == "establish_connection":
            print("HTTP request received: Establishing WebSocket connection...")
            websocket_connection = websocket
            await websocket.send(json.dumps({"status": "connection_established"}))

            # Start the counter loop
            await counter_loop()
    except Exception as e:
        print(f"HTTP handler error: {e}")


async def counter_loop():
    global counter, websocket_connection

    try:
        while websocket_connection:
            await asyncio.sleep(3)
            counter += 1
            await websocket_connection.send(json.dumps({"type": "counter", "value": counter}))
    except websockets.ConnectionClosed:
        print("Client disconnected. Stopping counter loop.")
        websocket_connection = None


async def handle_websocket_requests(websocket):
    global counter
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "reset_counter":
                print("Reset request received. Counter reset to 0.")
                counter = 0
                await websocket.send(json.dumps({"status": "counter_reset"}))
    except websockets.ConnectionClosed:
        print("WebSocket connection closed")


async def main():
    server = await websockets.serve(handle_http, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    await server.wait_closed()


asyncio.run(main())
