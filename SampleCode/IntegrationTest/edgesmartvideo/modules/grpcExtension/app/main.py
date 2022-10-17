import sys
import logging
from exception_handler import PrintGetExceptionDetails
from inference_server import  InferenceServer
import grpc
import extension_pb2_grpc
from concurrent import futures
import argparse
import os

import asyncio
import signal
import threading
import json
from azure.iot.device.aio import IoTHubModuleClient
from ai_model_path import AI_Model_Path

# Main thread
def Main():
    try:
        # Get application arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', metavar=('grpc_server_port'), help='Port number to serve gRPC server.', type=int, default=5001)
        parser.add_argument('-b', metavar=('batch_size'), help='Batch size.', type=int, default=1)
    
        _arguments = parser.parse_args()

        # Default to port 5001
        grpcServerPort = _arguments.p

        # Default batch size 1
        batchSize = _arguments.b
        
        # Get port from environment variable (overrides argument)
        envPort = os.getenv('port')

        # Get batch size from environment variable (overrides argument)
        envBatchSize = os.getenv('batchSize')

        if(envPort is not None):
            grpcServerPort = envPort
        
        if(envBatchSize is not None):
            batchSize = int(envBatchSize)
       
        logging.info('gRPC server port with: {0}'.format(grpcServerPort))
        logging.info('Batch size set to: {0}'.format(batchSize))

        # create gRPC server and start running
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
        extension_pb2_grpc.add_MediaGraphExtensionServicer_to_server(InferenceServer(batchSize), server)
        server.add_insecure_port(f'[::]:{grpcServerPort}')
        server.start()
        server.wait_for_termination()

    except:
        PrintGetExceptionDetails()
        exit(-1)


# Event indicating client stop
stop_event = threading.Event()
def IoT_Edge_Start():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        # loop.run_until_complete(run_sample(client))
        loop.run_until_complete(asyncio.gather(run_sample(client), Main()))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()

# async def IoT_Edge_Start():
#     try:
#         if not sys.version >= "3.5.3":
#             raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
#         print ( "IoT Hub Client for Python" )

#         # The client object is used to interact with your Azure IoT hub.
#         module_client = IoTHubModuleClient.create_from_edge_environment()

#         # connect the client.
#         await module_client.connect()

#         # Define function for handling received messages
#         async def receive_message_handler(message):
#             print("Message received")
#             size = len(message.data)
#             message_text = message.data.decode('utf-8')
#             print("    Data: <<<{data}>>> & Size={size}".format(data=message.data, size=size))
#             print("    Properties: {}".format(message.custom_properties))

#             if message.input_name == "AIMessageInput":
#                 # message_json = json.loads(message_text)
#                 local_ai_path = "/var/lib/videoanalyzer/" + message_text
#                 AI_Model_Path.SetPath(local_ai_path)
#                 logging.info("############## SET AI MODEL PATH: " + local_ai_path)


#         # Set handler on the client
#         module_client.on_message_received = receive_message_handler
#         logging.info('message_handler listening ...')

#     except:
#         # Cleanup if failure occurs
#         module_client.disconnect()
#         module_client.shutdown()
#         raise

#     return module_client

async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        print("Message received")
        size = len(message.data)
        message_text = message.data.decode('utf-8')
        print("    Data: <<<{data}>>> & Size={size}".format(data=message.data, size=size))
        print("    Properties: {}".format(message.custom_properties))

        if message.input_name == "AIMessageInput":
            message_json = json.loads(message_text)
            
            local_model_path = "/var/lib/videoanalyzer/" + message_json["local_model_path"]
            local_labelmap_path = "/var/lib/videoanalyzer/" + message_json["local_labelmap_path"]

            AI_Model_Path.Set_Model_Path(local_model_path)
            AI_Model_Path.Set_Labelmap_Path(local_labelmap_path)

            logging.info("############## SET AI MODEL PATH: " + local_model_path)
            logging.info("############## SET AI Labelmap PATH: " + local_labelmap_path)

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
        logging.info('message_handler listening ...')
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client

# https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-python-module?view=iotedge-2020-11
# def create_client():
#     client = IoTHubModuleClient.create_from_edge_environment()

#     # Define function for handling received messages
#     async def receive_message_handler(message):
#         print("Message received")
#         size = len(message.data)
#         message_text = message.data.decode('utf-8')
#         print("    Data: <<<{data}>>> & Size={size}".format(data=message.data, size=size))
#         print("    Properties: {}".format(message.custom_properties))

#         if message.input_name == "AIMessageInput":
#             # message_json = json.loads(message_text)
#             local_ai_path = "/var/lib/videoanalyzer/" + message_text
#             AI_Model_Path.SetPath(local_ai_path)
#             logging.info("############## SET AI MODEL PATH: " + local_ai_path)
#     try:
#         # Set handler on the client
#         client.on_message_received = receive_message_handler
#         logging.info('message_handler listening ...')
#     except:
#         # Cleanup if failure occurs
#         client.shutdown()
#         raise

#     return client

if __name__ == "__main__": 
    # Set logging parameters
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)       # write in stdout
        ]
    )
    # Call Main function
    IoT_Edge_Start()