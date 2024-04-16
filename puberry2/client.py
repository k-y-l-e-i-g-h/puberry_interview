import asyncio
import websockets
import json

async def send_message(websocket, message):
    try:
        await websocket.send(json.dumps(message))
        print(f"Sent message: {message}")
        response = await websocket.recv()
        print(f"Received response: {response}")
    except websockets.exceptions.ConnectionClosedError:
        print("Connection to server closed unexpectedly")
    except Exception as e:
        print(f"An error occurred: {e}")


async def main():
    uri = "ws://localhost:5000"  # WebSocket server address
    async with websockets.connect(uri) as websocket:
        print("WebSocket connection established")

        # Receive the prompt from the server to enter the player ID
        playerId = input(await websocket.recv())
        await websocket.send(playerId)  # Send the player ID to the server

        while True:
            action = input("Enter action (createLobby, joinLobby, leaveLobby, startGame, notifyPlayers): ")

            if action == "quit":
                print("Exiting client.")
                break
            
            if action == "createLobby":
                lobbyName = input("Enter lobby name: ")
                await send_message(websocket, {"action": action, "playerId": playerId, "lobbyDetails": {"name": lobbyName}})
            
            elif action in ["joinLobby", "leaveLobby"]:
                lobbyId = input("Enter lobbyId (int): ")
                await send_message(websocket, {"action": action, "playerId": playerId, "lobbyId": int(lobbyId)})

            elif action == "startGame":
                lobbyId = input("Enter lobbyId: ")
                await send_message(websocket, {"action": action, "lobbyId": int(lobbyId)})
            
            elif action == "notifyPlayers":
                lobbyId = input("Enter lobbyId (int): ")
                message = input("Enter message to notify: ")
                await send_message(websocket, {"action": action, "lobbyId": int(lobbyId), "message": message})
            
            else:
                print("Invalid action")

asyncio.run(main())
