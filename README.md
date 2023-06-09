# SICK_Lidar_CoLa2
This respository contains a selection of Python tools for handling the CoLa2 data output on the SICK microScan3, outdoorScan3 and nanoScan3.

There are three tools available, which are described below. Each tool is contained within a branch of this respository, with it's own readme.

### The CoLa2 Session Handler (Versions 1 and 2)
This program will allow the set-up of a CoLa2 session, and a request/response between the users PC and a SICK microScan3, outdoorScan3 or nanoScan3.

With the version one, you can send a direct CoLa2 command, as shown with the examples below. However, version 2 is preprogrammed with all standard indexes, so you can read directly without creating a command string. Additionally, version 2 allows the use of methods as well as custom commands, as was the case in version 1.

Example requests include:
02 02 02 02 00 00 00 0c 00 00 53 49 43 4b 00 01 52 49 + [index]

Example indexes include... 
- 03 00 - Read serial number (sensor and system plug).
- 0d 00 - Read type code.
- b3 00 - Read most recent data output (channel 0).

Find more at SICK.com by searching 8022708 (Technical information for data output via UDP and TCP)

### The CoLa2 Data Output Activator
This program will trigger the UDP data output of a SICK microScan3, outdoorScan3 or nanoScan3 according to the given parameters.

For example, it goes something like this:

* Enter IP Address of device : 192.168.136.2
* Enter IP Address (send to): 192.168.136.254
* Enter Port number (send to): 50000
* Device type selection: EFI-pro: 0 - EtherNet/IP: 1 - EtherCAT: 2 - PROFINET: 3 - Standard Ethernet: 4
* Enter interface type (0 ... 4 as above): 3
* Set full data output (F) or set parameters manually? (m)? F/m: m
* Sending rate (1 ... 40): Enter 1 for every measurement,  4 for every 4th measurement, etc.
* Enter the sending rate: 1
* Starting and ending angles (from -47.5 ... 227.5). 0 as both for full scanning range.
* Enter starting angle: -10
* Enter ending angle: 10
* Activate all data blocks? Y/n: n
* Activate 'Device Status'? Y/n: n
* Activate 'Configuration of the data output'? Y/n: y
* Activate 'Measurement data'? Y/n: y
* Activate 'Field interruption'? Y/n: y
* Activate 'Application data'? Y/n: n
* Activate 'Local inputs and outputs'? Y/n: n
* Response from device confirms data output over UDP has been activated.
* The data output should now be visible in a tool such as Wireshark.
* CoLa2 session closed. TCP connection closed.

### The Ethernet Data Output Viewer
This program will read the most recent scan data from a SICK microScan3, outdoorScan3 or nanoScan3, and save this data to a .txt file in a readable format, i.e., converting the data and giving the values with a description. In addition, it's also possible to paste in a raw hex stream (UDP or TCP data sample) from Wireshark and save this to a .txt file rather than reading from a connected device. 
