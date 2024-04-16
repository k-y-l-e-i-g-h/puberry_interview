Hello!

So.. I ended up rewriting the backend completely in order to implement the front end smoothly :D 

You can test the backend as so:
- in one terminal, run the server
    $ python server.py
- in another terminal, run the client
    $ python client.py
- Follow the promts (they are pretty straight forward)
- You should be able to run multiple clients simultaneously 

Challenges: the web socket connection seems the close after 20 seconds of nonactivity, so beware. 
The server is quite informative-- it will tell you when a connection is closed and which one.

Implementing the frontend:
In my new backend, I used Websocket API with async.io and python in the server with in memory data storage for the lobbies and players. 
and async functions to communicate with the fontend/client. 
- Run the server
    $ python server.py
- Open id_form.html to get started
    double click on the html file to open in browser
- Enter any player ID
- Create or join a lobby
    Within the lobby, players can start game (not implemented), notify players, or leave lobby.
- You should be able to run multiple browsers at once
    side note: make sure you start with id_form.html, otherwise you will have no player ID set andn things may go awry.

Challenges: I could not for the life of me get the frontend to retreive the lobbyID from the server, making the join lobby implementation tough.
At the moment, join lobby only works fo rthe first lobby created (it is hard coded to navigate to th elobby with id = 1)

To infinity and beyond!