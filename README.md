# Ethernet Data Output Viewer
Version 1.0.1 created on 23.06.2023 by James Edwards

### What does the 'Ethernet Data Output Viewer' do?
- This program will either read the configured (via Safety Designer) measurement data output from a SICK microScan3, outdoorScan3 or nanoScan3 ('device') or read a pasted TCP/UDP data output sample, and then save the read/pasted data to a .txt file in a readable format.
- The program makes a single snapshot of the data that is read or pasted. It does not give a live view or show measurement points plotted. Please use Safety Designer or other tools such as the ROS driver for this.

### How can the 'Ethernet Data Output Viewer' support you?
- This tool is intended for diagnostics purposes. Combining the tool with carefully configured data output parameters (in Safety Designer) can allow for the easy assessment of reflector detection, beam # to distance values, etc. In addition, device I/O (both physical and assembly/process image) can be observed to state and validity.
- If the code can assist you with your own implementation of data output handling, please feel free to copy and adjust accordingly.

### How to run the program?
1. Install Python (minimum version 3.10.4). Download Python here: https://www.python.org/downloads/ 
2. Associate .py file extensions with Python (this is usually automatically done).
3. Run the Ethernet_Data_Output_Viewer_V#.##.py and the program will open a command window.
4. Follow the prompts in the command window.

- You may also choose to use an IDE such as Pycharm or Visual Studio Code to run this program.

### How to use the program?
Follow the prompts:

1. To read data from a SICK microScan3, outdoorScan3 or nanoScan3, please enter 'y' (default). Otherwise, enter 'n'.
    - 'y' to read the configured data output via TCP
    - 'n' to paste in a UDP or TCP data sample

#### Reading mode:
**If selecting 'y':**

2. To read the data output, please enter the IP address of the target device below.
3. Channel 0 is default. To change channel (0...3), please enter 'c' instead of the IP address.
    - E.g., '192.168.1.2' to read from the device with this address  
    - 'c' to change the channel
4. If the IP address was entered, the program reads the data, and saves the .txt file.

**If selecting 'c'**

4. Enter the channel (0...3)
   - '1' to read from channel 1. Note that devices may not support more than channel 0, and that 'channel 1' in Safety Designer is actually channel 0.
5. To read the data output, please enter the IP address of the target device below.
   - E.g., '192.168.1.2' to read from the device with this address (from newly entered channel)
6. The program reads the data and saves the .txt file.
    
#### TCP or UDP mode

2. To paste TCP data (as HEX), enter 't'. To paste UDP data (as HEX), enter 'u'.
   - 't' to paste in TCP data
   - 'u' to paste in UDP data
3. Paste in the complete TCP or UDP data and press enter.
4. The program converts the data and saves the .txt file.

### The .txt file
- The .txt file is named DataOutput_DD-MM-YYYY_hh-mm-ss.txt (DAY-MONTH-YEAR_hour_minute_second.txt as per your system time).
- The .txt file is saved in the same directory as the Ethernet_Data_Output_Viewer_V#.##.py file.
- The save location can be changed in code. Please modify to the python open() function parameters to achieve this (optional).

### How to work with TCP or UDP data samples
- The TCP or UDP samples must be provided complete. This means that all frames (if more than one) must be provided together.
- The samples must be provided in HEX. For example: using Wireshark, select each frame, and copy (...as a hex stream) the data to the tool before pressing 'enter. Or copy all to a .txt file first.
- The TCP frames MUST be provided in the correct order.
- The UDP frames can be provided out of order (The tool will use the additional UDP header to reorder data, if necessary).
- The correct mode 't' or 'u' must be selected to match the correct data sample type.

### Troubleshooting
- In most cases, the tool will provide an error message that is easy to understand.
- When reading data with TCP, errors usually only occur if the wrong IP address is entered, or the selected channel is either not supported or inactive.
- When pasting TCP or UDP data, errors usually occur if the wrong data type is selected, or frames are missing.
- The program runs for 250 ms to both obtain the session ID (CoLa2) and read the data output. In the event that network latency is present, this may result in a loss of data. This time can be increased in the code.
- The tool will handle up to 25 UDP frames. At time of writing, this is significantly higher than the maximum expected number of UDP frames from any SICK safety laser scanner.
