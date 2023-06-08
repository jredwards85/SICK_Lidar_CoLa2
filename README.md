# Cola2_Session_Handler_V1.0.3.py
Version 1.0.3 created on 10.05.2023 by James Edwards

### What does the 'CoLa2 Session Handler' do?
- This program will allow the set-up of a CoLa2 session, and a request/response between the users PC and a SICK microScan3, outdoorScan3 or nanoScan3 ('device).
- The user is prompted to enter the IP Address of the target device, followed by a request command (e.g., read serial number, read type code, etc.). Provided all values are entered correctly, the program will create a TCP session, CoLa2 session, and append the correct session ID to the request. The program will then display the response in both HEX and ASCII in the command window/IDE.

### How to run the program?
1. Install Python (minimum version 3.10.4). Download Python here: https://www.python.org/downloads/ 
2. Associated .py file extensions with Python (this is usually automatically done).
3. Run the CoLa2_Session_Handler_V#.##.py and the program will open a command window.
4. Follow the prompts in the command window.

- You may also choose to use an IDE such as Pycharm or Visual Studio Code to run this program.

### How to use the program?
Follow the prompts:
1. Firstly enter the IP address of the target device (e.g., microScan3). Press enter.
2. Enter the CoLa2 command. Press enter.
- Note that a complete CoLa2 command must be given. The values give as the session ID do not matter. The command must be in valid HEX.
3. Receive a response. The response is given in both HEX and ASCII (some values are easier to read in ASCII).
4. Choose to send another request by entering 'y', or closing the program by entering 'n'.

### Troubleshooting (software)
In most cases the program will tell you when a problem occurs. The most common errors are:
- Incorrect IP address
- Incorrect command string. E.g., the command provided is not valid HEX (spaces do not matter).
- CoLa2 error.  If an error code is part of the response, the error code is provided by the tool. See the relevant user manual.
- No data responce from the target. If the target sends no data back, this is recognised.

### Troubleshooting (Ethernet)
- Ensure a physical connection is made.
- Ensure an IP address is configured for the PC network interface.
- Ensure an IP address is configured for the target device.
- Ensure the IP addresses of both the PC network interface and target device are in the same subnet.
- Ensure that the IP address range is permitted by IT security policy.

### 'Hard-coded' values in the program.
- The port '2122' is fixed. This is the current port used by the SICK microScan3, outdoorScan3 and nanoScan3.
