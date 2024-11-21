import asyncio
import websockets


async def server_handler(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            response = f"Echo: {message}"
            await websocket.send(response)
    except websockets.ConnectionClosedOK:
        print("Client disconnected")


async def main():
    server = await websockets.serve(server_handler, "0.0.0.0", 8765)
    print("WebSocket server is running on ws://0.0.0.0:8765")
    await server.wait_closed()


asyncio.run(main())
