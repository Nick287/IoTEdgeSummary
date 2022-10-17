import asyncio
from logging import disable
from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubConsumerClient
import json
import threading

# Define callbacks to process events
async def on_event_batch(partition_context, events):
    for event in events:
        print("Received event from partition: {}.".format(partition_context.partition_id))
        print("Telemetry received: ", event.body_as_str())
        print("Properties (set by device): ", event.properties)
        print("System properties (set by IoT Hub): ", event.system_properties)
        # hubjson = json.loads(event.system_properties)
        print()
        
        try:
            data = json.loads(event.body_as_str())
            if data['inferences'][0]['subtype'] == 'MS_Logo_Detected':
                # loop.call_soon_threadsafe(loop.stop)  # here
                global is_detected
                with lock:
                    is_detected = True
                for task in asyncio.all_tasks():
                    task.cancel()
            return
        except Exception:
            continue

    await partition_context.update_checkpoint()

async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))

async def Run_Timer():  
    print("Timer Start")  
    await asyncio.sleep(120)
    global is_detected
    with lock:
        is_detected = False
    print("Timer Stop")
    for task in asyncio.all_tasks():
        task.cancel()


def test_edge_ava_device(config_iot_ava_device):
    CONNECTION_STR = config_iot_ava_device["IOTHUB_EVENTHUB_CONNECTION_STRING"]
    client = EventHubConsumerClient.from_connection_string(
    conn_str = CONNECTION_STR,
    consumer_group = "$default",
    )
    try:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.gather(client.receive_batch(on_event_batch=on_event_batch, on_error=on_error), Run_Timer()))
        # loop.run_until_complete(client.receive_batch(on_event_batch=on_event_batch, on_error=on_error))
    except KeyboardInterrupt:
        print("Receiving has stopped.")
    except asyncio.CancelledError:
        pass
    finally:
        loop.run_until_complete(client.close())
        loop.stop()
    
    if is_detected:
        print("Congratulations! Get AVA AI message.")

    assert is_detected


lock = threading.Lock()
is_detected = False