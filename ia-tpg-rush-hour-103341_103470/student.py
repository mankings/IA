"""Example client."""
import time
import asyncio
import getpass
import json
import os
import websockets

from rush_hour_ai import Bot

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    """Example client loop."""
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        bot_init = False
        while True:
            try:
                # receive game update, this must be called timely or your game will get out of sync with the server
                state = json.loads(await websocket.recv())  
                game_speed = state["game_speed"]

                # if 1st server message coming in, init ai agent
                if not bot_init:
                    agent = Bot(state["dimensions"], state["grid"])
                    bot_init = True
                
                # if agent is on, run the agent to get next move
                else:
                    t0 = time.time()
                    key = agent.run(state)
                    t = time.time() - t0
                    if key == None:
                        continue
                    
                    # dumps useless recvs
                    dumps = int((t * game_speed))
                    for i in range(dumps):
                        await websocket.recv()
                    
                    # if state changed, recalc
                    # send next move/keypress to server
                    await websocket.send(json.dumps({"cmd": "key", "key": key}))

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))