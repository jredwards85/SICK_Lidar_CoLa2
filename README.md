# CoLa2 Session Handler
This branch contains two files:
- CoLa2_Session_Handler_V1.0.3
- CoLa2_Session_Handler_V2.0.0
  
The version 2 (V2.0.0) supersedes version 1, however, version 1 can be continued if the user intends to send custom commands only (i.e., the user has constructed a valid CoLa2 command in HEX) 

### What does the 'CoLa2 Session Handler' do?
- This program will allow the set-up of a CoLa2 session, and a request/response between the user's PC and a SICK microScan3, outdoorScan3 or nanoScan3 ('device').
- The user is prompted to enter the IP Address of the target device, followed by a selection of commands (e.g., read serial number, read type code, etc.).
- Provided all values are entered correctly, the program will create a TCP session, a CoLa2 session, and append the correct session ID to the given request or method.
- The program will then display the response in both HEX and ASCII in the command window/IDE.

### How to run the program?
1. Install Python (minimum version 3.10.4). Download Python [here.](https://www.python.org/downloads/) 
2. Associated .py file extensions with Python (this is usually automatically done).
3. Run the CoLa2_Session_Handler_V#.##.py and the program will open a command window.
4. Follow the prompts in the command window.
- You may also choose to use an IDE such as Pycharm or Visual Studio Code to run this program.

### More details of each tool can be found below:

<details><summary>CoLa2_Session_Handler V1 (V1.x.x)</summary>

  ## Cola2_Session_Handler_V1.0.3.py
Version 1.0.3 created on 10.05.2023 by James Edwards

  ### How to use the program?
Follow the prompts:
1. Firstly enter the IP address of the target device (e.g., microScan3). Press enter.
2. Enter the CoLa2 command. Press enter.
- Note that a complete CoLa2 command must be given. The values give as the session ID do not matter, however, all characters in the command must be in valid HEX.
3. Receive a response. The response is given in both HEX and ASCII (some values are easier to read in ASCII).
4. Choose to send another request by entering 'y' or closing the program by entering 'n'.
</details>

<details><summary>CoLa2_Session_Handler V2 (V2.x.x)</summary>
  
  ## Cola2_Session_Handler_V2.0.0.py
Version 2.0.0 created on 05.07.2023 by James Edwards

  ### What are the benefits of version 2 of the CoLa2 session handler?
  - Allows the user to make all 17 standard read variables, both methods and even custom CoLA2 commands such as write commands, or yet to be released variables.
  - The tool prints the results of all 17 standard read variables in an easy to read manner. 
  - Any data that requires conversion is automatically converted into the correct values.
  - This tool can be used in place of the CoLa2 Data Output Activator tool.
  - This tool can be used in combination to read TCP measurement data frames to use in the Ethernet Data Output Viewer (please see the other branch).
  - Lastly, the code has been refined and optimised.

  ### How to use the program?
Follow the prompts:
1. Firstly enter the IP address of the target device (e.g., microScan3). Press enter.
2. Enter the command type (Read variable, invoking a method or custom CoLa2 command). press enter.
3. If selection 'Read variable':
   - Enter a number between 1 and 17 according to the table of commands.
   - In most cases, the data result is printed directly. In other cases, you may need to enter an additional parameter, such as choosing the correct channel.
4. If selection 'Invoke a method':
   - Enter a number between 1 and 2 according to the table of commands.
   - In both cases (Identifying a device and configuring the data output) further parameters will need to be entered.
   - Depending on the method, either the display will flash blue for the given time, or the UDP data output will be activated/changed according to the given parameters.
5. If selection 'Custom CoLa2 command':
   - Copy the CoLa2 command in valid HEX. The session ID is not important (e.g., 00000000 would be suitable).
   - The data result is printed directly in both HEX and ASCII.
6. Choose to send another request by entering 'y' or closing the program.
</details>

### Troubleshooting (software)
In most cases the program will tell you when a problem occurs. The most common errors are:
- Incorrect IP address
- Incorrect command string. E.g., the command provided is not valid HEX (spaces do not matter).
- CoLa2 error.  If an error code is part of the response, the error code is provided by the tool. See the relevant user manual.
- No data response from the target. If the target sends no data back, this is recognised.

### Troubleshooting (Ethernet)
- Ensure a physical connection is made.
- Ensure an IP address is configured for the PC network interface.
- Ensure an IP address is configured for the target device.
- Ensure the IP addresses of both the PC network interface and target device are in the same subnet.
- Ensure that the IP address range is permitted by IT security policy.

### 'Hard-coded' values in the program.
- The port '2122' is fixed. This is the current port used by the SICK microScan3, outdoorScan3 and nanoScan3.

### Availability and lifecycle of this tool
- This tool is available to all for business or personal usage.
- The tool may not be maintained in the future, so in case of issues with the data, please review the Data Output manual at SICK.com.
