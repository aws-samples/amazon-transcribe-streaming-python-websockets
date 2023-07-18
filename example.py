# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from presigned_url import AWSTranscribePresignedURL
import os
import asyncio
import websockets
import wave
import logging, sys
import string
import random
from eventstream import create_audio_event, decode_event

# Configure logging - change to Logging.DEBUG for details
logging.basicConfig(stream=sys.stderr, level=logging.INFO) 

# Configure access - either from environment variables or define them here.
access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY","")
session_token = os.getenv("AWS_SESSION_TOKEN","")
region = os.getenv("AWS_DEFAULT_REGION","us-east-1")
transcribe_url_generator = AWSTranscribePresignedURL(access_key, secret_key, session_token, region)

# Sound settings
language_code = "en-US"
media_encoding = "pcm"
sample_rate = 8000
number_of_channels = 2
channel_identification = True
bytes_per_sample = 2 # 16 bit audio
chunk_size = sample_rate * 2 * number_of_channels / 10 # roughly 100ms of audio data
file_name = 'example_call_2_channel.wav'

# Async loop that sends file to websocket / Transcribe
async def send(websocket):
    # Open WAVE File to read
    wf = wave.open(file_name, "rb")
    
    while True:
        try:
            audio_chunk = wf.readframes(int(chunk_size))
            if len(audio_chunk) > 0:
                audioEvent = create_audio_event(audio_chunk) 
                await websocket.send(audioEvent)
            await asyncio.sleep(0.1)  # yield control to the event loop, also delay reading audio file
        except websockets.exceptions.ConnectionClosedError:
            logging.exception(f"Connection closed error")
            break;
        except Exception as error:
            logging.exception(f"An exception has occurred")
            break;


# Async loop that listens for responses from Transcribe
async def receive(websocket):
    try:
        while True:
            response = await websocket.recv()
            header, payload = decode_event(response)
            # Process the Transcribe response here.
            if header[':message-type'] == 'event':
                # this is a normal event, either TranscribeEvent or UtteranceEvent or CategoryEvent
                if len(payload['Transcript']['Results']) > 0:
                    logging.info(payload['Transcript']['Results'][0]['Alternatives'][0]['Transcript'])
            elif header[":message-type"] == 'exception':
                logging.error(payload['Message'])
            await asyncio.sleep(0) # Yield to main loop
    except websockets.exceptions.ConnectionClosedError as error:
        logging.error(f"Connection closed error.")
    except Exception as error:
        logging.exception(f"An exception has occurred.")

# This opens the websocket and starts the send and receive sync loops
async def connect_to_websocket():
    # generate random websocket key and headers
    websocket_key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=20))
    extra_headers = {
        "Origin": "https://localhost", # If on the web, replace with streaming url
        "Sec-Websocket-Key": websocket_key,
        "Sec-Websocket-Version":"13",
        "Connection":"keep-alive"
    }
    # generate signed url to connect to
    request_url = transcribe_url_generator.get_request_url(sample_rate, 
                                                           language_code, 
                                                           media_encoding, 
                                                           number_of_channels=number_of_channels,
                                                           enable_channel_identification=channel_identification)
    async with websockets.connect(request_url, 
                                  extra_headers=extra_headers, 
                                  ping_timeout=None,
                                  ) as websocket:  # Connect to the WebSocket
        await asyncio.gather(receive(websocket), send(websocket))

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(connect_to_websocket())
    except KeyboardInterrupt:
        pass