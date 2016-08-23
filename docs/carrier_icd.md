Percival Carrier Interface Control Document
===========================================

This ICD specifies the interface between the Percival Carrier Board control software and the ODIN Parallel Detector Control System.  This software interface is split into two parts, commands sent to the Percival Carrier Board control software and any associated responses, and status published by the Percival Carrier Board control software.  
All messages, whether command, response or status will be constructed from Inter Process Communication Message (IpcMessage) Objects, and are sent as serialized JSON representations of those objects.
Communication channels are constructed using ZeroMQ sockets.  The command channel is a client/server ZeroMQ socket, and the status channel is a publisher ZeroMQ socket.

## Status

A status message will contain at least the following items:
- timestamp.  The timestamp at which the message was constructed
- msg_val.  The message value for an IPC status message (MSG_VAL_CMD_STATUS = 1)
- msg_type.  The message type for an IPC status message (MSG_TYPE_NOTIFY = 3)
- Collection of device objects.  Each object is indexed by name.  The specific values for each device type are presented in the table below

The table below describes the status items for each device that can be published by the Percival Carrier Board control software

|Device|Item|Type|Description|
|------|----|----|-----------|
|MAX31730|device|string|The string representation of the device (always MAX31730)|
|MAX31730|temperature|double|Current temperature reading|
|MAX31730|i2c_comms_error|integer|Communications error on i2c bus|
|MAX31730|low_threshold|integer|1 if current temperature is lower than the specified low_threshold, 0 otherwise|
|MAX31730|extreme_low_threshold|integer|1 if current temperature is lower than the specified extreme_low_threshold, 0 otherwise|
|MAX31730|high_threshold|integer|1 if current temperature is higher than the specified high_threshold, 0 otherwise|
|MAX31730|extreme_high_threshold|integer|1 if current temperature is higher than the specified extreme_high_threshold, 0 otherwise|
|MAX31730|safety_exception|integer|1 if temperature has exceeded the extreme thresholds for the specified number of samples, 0 otherwise|
|MAX31730|unit|string|Units for the current temperature reading|
|LTC2309|device|string|The string representation of the device (always LTC2309)|
|LTC2309|voltage|double|Current voltage reading|
|LTC2309|i2c_comms_error|integer|Communications error on i2c bus|
|LTC2309|low_threshold|integer|1 if current voltage is lower than the specified low_threshold, 0 otherwise|
|LTC2309|extreme_low_threshold|integer|1 if current voltage is lower than the specified extreme_low_threshold, 0 otherwise|
|LTC2309|high_threshold|integer|1 if current voltage is higher than the specified high_threshold, 0 otherwise|
|LTC2309|extreme_high_threshold|integer|1 if current voltage is higher than the specified extreme_high_threshold, 0 otherwise|
|LTC2309|safety_exception|integer|1 if voltage has exceeded the extreme thresholds for the specified number of samples, 0 otherwise|
|LTC2309|unit|string|Units for the current voltage reading|


An example status message is presented below.  The status message contains two devices, one temperature sensor (MAX31730) and one ADC (LTC2309).

```
{
    "timestamp": "2016-06-20T11:28:18.110525",
    "msg_val"  : 1,
    "msg_type" : 3,
    "params"   : {
                   "Temperature1": {
                                     "extreme_low_threshold"  : 0,
                                     "temperature"            : 35.625,
                                     "i2c_comms_error"        : 0,
                                     "device"                 : "MAX31730",
                                     "high_threshold"         : 0,
                                     "low_threshold"          : 1,
                                     "safety_exception"       : 0,
                                     "extreme_high_threshold" : 0,
                                     "unit"                   : "C"
                                   },
                   "VPOT1"       : {
                                     "extreme_low_threshold"  : 0,
                                     "voltage"                : 4.095,
                                     "i2c_comms_error"        : 0,
                                     "device"                 : "LTC2309",
                                     "high_threshold"         : 1,
                                     "low_threshold"          : 0,
                                     "safety_exception"       : 1,
                                     "extreme_high_threshold" : 1,
                                     "unit"                   : "V"
                                   }
                 }
}
```
