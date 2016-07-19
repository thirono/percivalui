Percival Carrier Board Control Design
=====================================

This document contains design notes to describe the implementation of the Percival carrier board control classes.


The main two classes (PercivalBoard and PercivalParameters) are located in the percival/control.py file.

## PercivalParameters

The PercivalParameters class manages the initialisation files for the Percival control application.  There are currently four BoardParameters instances, one ControlParameters instance and one ChannelParameters instance maintained by this class.  A set of methods are present to provide access to the parameters that are managed by these classes.
The load_ini method will load the specified files into the corresponding instances (currently all ini files are hardcoded, but perhaps the main percival.ini file should in fact contain the others?).

## PercivalBoard

Currently this class provides the overall control of all aspects of the Percival carrier board.  It maintains the TCP connection to the hardware, owns the PercivalParameters instance and sets up the IPC reactor and channels for status monitoring and control.
When a new instance of the PercivalBoard class is created, it constructs an instance of the PercivalParameters class.  It then calls load_ini on that class, before connecting to the hardware, creating all of the appropriate BoardSetting instances as well as the SystemCommand instance, and sets up the status and control IpcChannel classes.
The class provides the method initialise_board, which if called will download all of the ini file settings to the hardware.  It also provides the method load_channels which will loop over the BoardSettings constructing Monitor and Control channel objects for all of the defined channels.

### Status

Global monitoring can be turned on or off.  If global monitoring is turned on then the appropriate system command is sent to the hardware, and the status/values for all monitoring channels are read from the hardware at (currently hardcoded) 10Hz.  This status/value information is encoded into an IpcMessage and published on the status IpcChannel.
The currently implemented status items that are published are described in the carrier_icd document.

### Control

Control of the PercivalBoard class is provided by an IpcChannel registered within the IpcReactor class.  The messages are expected to be IpcMessage type JSON encoded strings.
The currently implemented set of commands can be found in the carrier_icd document.

### Threading

The TxRx class has been updated to include locking, but currently the PercivalBoard implementation uses the tickless IpcReactor which provides timers and message handling within a single thread.  There should be no barriers to implementing a multi-threaded approach for the PercivalBoard class but at this early stage it was not necessary for the level of control and status required.



