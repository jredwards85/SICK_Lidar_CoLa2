# Cola2_Session_Handler_V1.0.3.py
Version 1.0.0 created on 08.06.2023 by James Edwards

### What does the 'CoLa2 Data Output Activator' do?
- This program will trigger the UDP data output of a SICK microScan3, outdoorScan3 or nanoScan3 ('device) according to the given parameters.
- The user is prompted to enter a select of parameters to configure the UDP data output of the device. In addition, the tool checks that the given parameters are correct and within specification of the device.
- The UDP data output, when activated successfully, is active until power off. This has no impact on the safety functions of the device.

### How to run the program?
1. Install Python (minimum version 3.10.4). Download Python here: https://www.python.org/downloads/ 
2. Associated .py file extensions with Python (this is usually automatically done).
3. Run the CoLa2_Session_Handler_V#.##.py and the program will open a command window.
4. Follow the prompts in the command window.

- You may also choose to use an IDE such as Pycharm or Visual Studio Code to run this program.

### How to use the program?
Follow the prompts:
1. Enter the IP address of the device.
2. Enter the IP address of the target (E.g., your PC).
3. Enter the port number of the target.
4. Select the device type (0 ... 3).
- EFI-pro: 0
- EtherNet/IP: 1
- EtherCAT: 2
- PROFINET: 3
- Standard Ethernet: 4 (e.g., for devices without an industrial fieldbus)
5. Select either full data output or custom data output.
- Full data output provides the full scanning range, every scan and all data blocks
- If selecting full data output, skip to step 11.
6. Select the sending range (1 ... 40).
7. Select the starting angle (min. -47.5 °).
8. Select the ending angle (max. 227.5 °).
9. Activate all data blocks or custom data blocks.
- All data blocks will activate: Device status, configuration of the data output, measurement data, field interruption, application data and local inputs and outputs.
- If activating all data, skip to step 11.
10. Select the desired data blocks via 'y' (yes) or 'n' (no) when prompted.
11. If successful, the following is printed: Response from device confirms data output over UDP has been activated.
12. You can now press enter to close the program.

### How to see the activated data output?
- I recommend using Wireshark on the relevant network interface to view the UDP frames.
- The size, quantify and frequency of UDP frames will vary depending on the device type and parameters given.

### Troubleshooting
- In most cases, inputting invalid values will print an error message and require restarting the program.
- All values provided to the device are checked for validity. This includes IP addresses, ports, angular range, and so on.
- If no data is received, but the program confirms that the data output was activated, then most likely either the IP address is incorrect, the monitored interface is incorrect, or the port is not permitted.
