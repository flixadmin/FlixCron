import asyncio
import websockets


async def view_pixel_drain(file_id):
    try:
        # Open a WebSocket connection
        async with websockets.connect("wss://pixeldrain.com/api/file_stats") as websocket:
            # Create the message string
            message = '{"type":"file_stats","data":{"file_id":"' + file_id + '"}}'

            # Send the message to the server
            await websocket.send(message)

            # Wait for 3 seconds as in the original code
            # await asyncio.sleep(3)

    except Exception as e:
        print(f"Error: {e}")

# await view_pixel_drain('8jHWeCeH')
# To run the function
if __name__ == "__main__":
    file_id = "8jHWeCeH"  # Replace with your actual file ID
    asyncio.run(view_pixel_drain(file_id))
