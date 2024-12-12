import asyncio
import random
import ssl
import json
import time
import uuid
import websockets
from loguru import logger
from fake_useragent import UserAgent
from datetime import datetime

async def connect_to_wss(user_id):
    user_agent = UserAgent(os=['windows', 'macos', 'linux'], browsers='chrome')
    random_user_agent = user_agent.random
    device_id = str(uuid.uuid4())
    logger.info(device_id)
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": random_user_agent,
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            urilist = ["wss://proxy2.wynd.network:4444/","wss://proxy2.wynd.network:4650/"]
            uri = random.choice(urilist)
            server_hostname = "proxy2.wynd.network"
            async with websockets.connect(uri, ssl=ssl_context, extra_headers=custom_headers,
                                          server_hostname=server_hostname) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(send_message)
                        await websocket.send(send_message)
                        await asyncio.sleep(5)

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(message)
                        
                    # Generate the current datetime in UTC
                    now = datetime.utcnow()
                    # Format the datetime as a string in the desired format
                    formatted_time = now.strftime('%a, %d %b %Y %H:%M:%S GMT')

                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "desktop",
                                "version": "4.29.0",
                            }
                        }
                        logger.debug(auth_response)
                        await websocket.send(json.dumps(auth_response))
                        
                    elif message.get("action") == "HTTP_REQUEST":
                        httpreq_response = {
                            "id": message["id"],
                            "origin_action": "HTTP_REQUEST",
                            "result": {
                                "url": message["url"],
                                "status": int(200),
                                "status_text": "OK",
                                "headers": {
                                    "content-type": "application/json; charset=utf-8",
                                    "date": formatted_time,
                                    "keep-alive": "timeout=5",
                                    "proxy-connection": "keep-alive",
                                    "x-powered-by": "Express",
                                }
                            }
                        }
                        logger.debug(httpreq_response)
                        await websocket.send(json.dumps(httpreq_response))

                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(pong_response)
                        await websocket.send(json.dumps(pong_response))
        except Exception as e:
            logger.error(e)


async def main():
    #find user_id on the site in conlose localStorage.getItem('userId') (if you can't get it, write allow pasting)
    _user_id = input('Please Enter your user ID: ')
    await connect_to_wss(_user_id)

if __name__ == '__main__':
    asyncio.run(main())
