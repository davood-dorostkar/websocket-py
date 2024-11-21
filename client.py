import asyncio
import websockets


async def client():
    uri = "ws://<server_ip>:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to the server")
        for i in range(3):
            message = f"Message {i+1}"
            await websocket.send(message)
            print(f"Sent: {message}")
            response = await websocket.recv()
            print(f"Received: {response}")


asyncio.run(client())
