import asyncio
import websockets
import json 
import traceback 

# Class to represent the lobby
class Lobby:
    def __init__(self, lobbyId, hostId, lobbyDetails):
        self.lobbyId = lobbyId
        self.hostId = hostId
        self.details = lobbyDetails
        self.players = [hostId]  # Initially, only the host is in the lobby


# Dictionary to store all active lobbies
active_lobbies = {}
active_connections = {}

# Function to create a new lobby
def createLobby(playerId, lobbyDetails):
    # Unique ID for lobby
    lobbyId = len(active_lobbies) + 1
    new_lobby = Lobby(lobbyId, playerId, lobbyDetails)
    
    # Add the lobby to the active lobbies dict
    active_lobbies[lobbyId] = new_lobby
    
    return lobbyId

# Function to join a lobby
def joinLobby(playerId, lobbyId):
    # Check if lobby exists
    if lobbyId not in active_lobbies:
        return False, "Lobby does not exist"
    
    # Add the player to lobby
    active_lobbies[lobbyId].players.append(playerId)
    
    return True, "Player joined lobby successfully"

# Function to leave a lobby
def leaveLobby(playerId, lobbyId):
    if lobbyId not in active_lobbies:
        return False, "Lobby does not exist"
    
    # Check if player is in lobby
    if playerId not in active_lobbies[lobbyId].players:
        return False, "Player is not in the lobby"
    
    # Remove player from lobby
    active_lobbies[lobbyId].players.remove(playerId)
    
    return True, "Player left the lobby successfully"

# Function to start a game
def startGame(lobbyId):
    if lobbyId not in active_lobbies:
        return False, "Lobby does not exist"
    
    # Check if the lobby has enough players to start game --> uncomment to test in client.py
    # if len(active_lobbies[lobbyId].players) < 2:
    #     return False, "Not enough players to start the game"
    
    # Delete the lobby
    del active_lobbies[lobbyId]
    
    return True, "Game started successfully. Lobby deleted"

# Function to send real-time notifications to players in a lobby
async def notifyPlayers(lobbyId, message):
    if lobbyId not in active_lobbies:
        return False, "Lobby does not exist"

    # Get the lobby object
    lobby = active_lobbies[lobbyId]
    
    # Loop through all players in the lobby and send notification
    for playerId in lobby.players:
        # Get the WebSocket connection associated with the player
        player_ws = active_connections.get(playerId)
        if player_ws:
            try:
                # Send the message to the player's WebSocket connection
                await player_ws.send(message)
            except Exception as e:
                print(f"Failed to send message to player {playerId}: {e}")
                # Handle the exception (e.g., close the connection, remove player from lobby)
                del active_connections[playerId]
                print(f"Player {playerId} disconnected")
        else:
            print(f"No WebSocket connection found for player {playerId}")
        

    return True, "Notifications sent successfully"

async def prompt_user_id(websocket):
    # Prompt the user to enter their player ID
    await websocket.send("Enter your player ID:")
    playerId = await websocket.recv()
    return playerId.strip()  # Remove leading/trailing whitespace

'''
Function to start WebSocket connection
Handles incoming connections and messages from clients
'''
async def handle_connection(websocket, path):
    # Perform any necessary setup
    print("WebSocket connection established")
    try:
        # Receive the initial message containing player ID from the client
        playerId = await prompt_user_id(websocket)

        # Associate the player ID with the WebSocket connection
        if playerId:
            active_connections[playerId] = websocket
            print(f"Player {playerId} connected")

        # Receive messages from the client
        async for message in websocket:
            await handle_message(websocket, message)

    except websockets.exceptions.ConnectionClosedOK:
        print("WebSocket connection closed")
        # Remove the player from active_connections if the connection is closed
        for playerId, conn in active_connections.items():
            if conn == websocket:
                del active_connections[playerId]
                print(f"Player {playerId} disconnected")
                break

    except websockets.exceptions.ConnectionClosedError as e:
        print("WebSocket connection error:", e)
        # Log traceback
        traceback.print_exc()
        # Remove the player from active_connections if the connection is closed unexpectedly
        for playerId, conn in active_connections.items():
            if conn == websocket:
                del active_connections[playerId]
                print(f"Player {playerId} disconnected unexpectedly")
                break

async def handle_message(websocket, message):
    # Parse the received message and perform appropriate actions
    try:
        data = json.loads(message)
        action = data.get("action")
        lobbyId = data.get("lobbyId")
        playerId = data.get("playerId")
        lobbyDetails = data.get("lobbyDetails")

    except json.JSONDecodeError:
        print("Invalid JSON format received")
        return
    
    # Perform appropriate actions based on the message content
    if action == "createLobby":
        # Call createLobby function
        new_lobby = createLobby(playerId, lobbyDetails)
        if new_lobby:
            #await notifyPlayers(new_lobby, "Lobby created")
            await websocket.send(json.dumps({"lobbyId": new_lobby}))
            print(f"Player {playerId} created lobby {new_lobby}.")
        else:
            await websocket.send("Failed to create lobby")

    elif action == "joinLobby":
        # Call joinLobby function
        result, message = joinLobby(playerId, lobbyId)
        if result:
            # await notifyPlayers(lobbyId, f"Player {playerId} joined the lobby")
            await websocket.send("Joined lobby successfully")
        else:
            await websocket.send(f"Failed to join lobby: {message}")

    elif action == "leaveLobby":
        # Call leaveLobby function
        result, message = leaveLobby(playerId, lobbyId)
        if result:
            await notifyPlayers(lobbyId, f"Player {playerId} left the lobby")
            await websocket.send("Left lobby successfully")
        else:
            await websocket.send(f"Failed to leave lobby: {message}")

    elif action == "startGame":
        # Call startGame function
        result, message = startGame(lobbyId)
        if result:
            await notifyPlayers(lobbyId, "Game started")
            await websocket.send("Game started successfully")
        else:
            await websocket.send(f"Failed to start game: {message}")

    elif action == "notifyPlayers":
        # Call notifyPlayers function
        notification_message = data.get("message")
        await notifyPlayers(lobbyId, notification_message)
        await websocket.send("Players notified successfully")
    else:
        await websocket.send("Unknown action")


async def handle_disconnection(websocket):
    # Perform cleanup actions when a WebSocket connection is closed
    print("WebSocket connection closed")

    # Identify the player associated with the disconnected WebSocket connection
    disconnected_playerId = None
    for lobbyId, lobby in active_lobbies.items():
        if websocket in lobby.players:
            disconnected_playerId = websocket
            break

    # If the disconnected player is found, remove them from any active lobbies
    if disconnected_playerId:
        for lobbyId, lobby in active_lobbies.items():
            if disconnected_playerId in lobby.players:
                lobby.players.remove(disconnected_playerId)
                await notifyPlayers(lobbyId, f"Player {disconnected_playerId} left the lobby due to disconnection")

# Start the WebSocket server and keep it running
start_server = websockets.serve(handle_connection, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
