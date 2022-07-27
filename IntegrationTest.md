#

## Integration test

Integration testing is a routine work each project and that is frequently asked questions raised because IoT Edge systems are often complex and can be tested in different scenarios, so here are some suggestions.

### Design test cases with event or data driven message

In IoT scenarios, the edge device often can collect some information, such as temperature and humidity data, or some certain data is generated on the device side so we can detect this kind of data, so lets call it event detection, so we can set a threshold on the device side that will trigger an event and we can send an alert when the event triggered.

Or your device is producing a dataset, and these data contains a specific data structure, probably its JSON object data. these data will sent back to the cloud as streaming data or upload as dump file.

So the key here is that whether events or data set will return the information to the IoT Hub.

### Use IoT Edge feature to trigger and send back expect results

For the trigger Please imagine event data mentioned above, we can use the Edge function to dynamically change the threshold. When the temperature and humidity are above the threshold, an alarm is sent. So base on that we can change a lower the threshold number to trigger the alarm and then send the alarm back to IoTHub.

for  dataset We can do a switch that produces a mock Data object that we add into source data flows. For example, simulate a message package that is passed into Edge Module via a routing message.

### Verify the result by IoT hub synchronization data with Edge device
