import socket, time, datetime, re

# CoLa2 Session handling function
def make_request(ipAddress, commandMode, commandHex):
    portNumber = int(2122)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(0.5)
    try: 
        data = bytearray.fromhex("020202020000000d00000000000000014f581e0000") 
        tcp_socket.connect((ipAddress, portNumber))
        tcp_socket.sendall(data)

        # While reading session ID, allows for fragmented data responses (max. duration 300 ms)
        t_end = time.time() + 0.3
        data = b''

        while time.time() < t_end:
            try:
                part = tcp_socket.recv(portNumber)
                if not part:
                    break
                data += part
            except socket.timeout:
                continue
            except socket.error as e:
                print("An error occurred while receiving data from the socket:")
                print(f"Error code:    {e.errno}")
                print(f"Error message: {e.strerror}")
                input("Press 'Enter' to close the program.")
                exit()

        # Constructs the command request with correct session ID        
        response  = data.hex()
        if not response or len(response) < 28:
            print("Error: The target provided no response or an incorrect response to creating a session. Please try again.")
            input("Press 'Enter' to close the program.")
            exit()
        sessionID = response[20:28]

        if commandMode == "r":
            dataReqHeader0 = "020202020000000c0000"
            dataReqHeader1 = "00015249"
            commandHex = dataReqHeader0 + sessionID + dataReqHeader1 + commandHex 
        elif commandMode == "m1":
            dataReqHeader0 = "020202020000000e0000"
            dataReqHeader1 = "00024d49"
            commandHex = dataReqHeader0 + sessionID + dataReqHeader1 + commandHex
        elif commandMode == "m2":
            dataReqHeader0 = "02020202000000280000"
            dataReqHeader1 = "00034d49b0000000000001"
            commandHex = dataReqHeader0 + sessionID + dataReqHeader1 + commandHex
        elif commandMode == "c":
            requestPart1 = commandHex[:20]
            requestPart2 = commandHex[28:]
            commandHex = requestPart1 + sessionID + requestPart2
        else:
            print("Error: An unexpected command was requested.")
            return
            
        commandData = bytearray.fromhex(commandHex)
        tcp_socket.sendall(commandData)
        
        # While reading request response, allows for fragmented data responses (max. duration 300 ms)
        t_end = time.time() + 0.3
        data = b''
        while time.time() < t_end:
            try:
                part = tcp_socket.recv(portNumber)
                data += part
            except socket.timeout:
                continue
            except socket.error as e:
                print("An unknown error occurred.")
                print(f"Error code:    {e.errno}")
                print(f"Error message: {e.strerror}")
                print("Press 'Enter' to close the program.")
                exit()
        if data.hex() == "":
            tcp_socket.close()
            print("Error: The target provided no response to your request. Please try again")
            input("Press 'Enter' to close the program.")
            exit()

        # Error handling for CoLa2 error codes. Outputs the error code for the user 
        colaError = data.hex()
        if colaError[32:36] == "4641":
            errorCode = colaError[37:40][::-1]
            tcp_socket.close()
            print(f"Error code: {errorCode}. Please refer to the data output error codes.")
            input("Press 'Enter' to close the program.")
            exit()

        # Close CoLa2 Session, sleep 100 ms to allow CoLa2 session close confirmation, close TCP
        closeSession1 = "020202020000000a0000"  
        closeSession2 = "00054358"
        closeSessionHex = closeSession1 + sessionID + closeSession2
        closeSession = bytearray.fromhex(closeSessionHex) 
        tcp_socket.sendall(closeSession) 
        time.sleep(0.1)
        tcp_socket.close()
        return data

    # Error handling for the TCP session function
    except TimeoutError:
        print("Timeout error: The IP Address is probably incorrect.")
        input("Press 'Enter' to close the program.")
        exit()

    except Exception as e:
        print("An unexpected error occured.")
        print(f"Error code:    {str(e)}")
        print(f"Error message: {repr(e)}")
        input("Press 'Enter' to close the program.")
        exit()

# Obtain IP address and verify
def is_valid_ip_address(ip):
    segments = ip.split('.')
    if len(segments) != 4:
        return False
    for segment in segments:
        try:
            value = int(segment)
            if value < 0 or value > 255:
                return False
        except ValueError:
            return False
    return True

def ip_address():
    while True:
        ipAddress = input("Please enter the IP Address of the target device: ")
        if is_valid_ip_address(ipAddress):
            return ipAddress
        else:
            print("Error: The IP Address was entered incorrectly. Please enter a valid IPv4 address.")
        
# Command type selection
def command_selection():
    print("Commands:")
    print("(1) Read variable")
    print("(2) Invoke a method")
    print("(3) Custom CoLa2 command")
    while True:
        try:
            commandNumber = int(input("Select command: "))
            if commandNumber <1 or commandNumber > 3:
                print("Please enter a number between 1 and 3.")
            else:
                break
        except ValueError:
            continue
    return commandNumber

# Read commands
def read_command_selection(ipAddress):
    print("\nBasic read commands...")
    print("(1) Read serial number               (10) Read meta data of the configuration")
    print("(2) Read firmware version            (11) Read application name")
    print("(3) Read type code                   (12) Read user name")
    print("(4) Read part number                 (13) Read device temperature")
    print("(5) Read SOPAS device status         (14) Read device time (nanoScan3 only)")
    print("(6) Read note on troubleshooting     (15) Read saved configuration of the data output channel") 
    print("(7) Read device name                 (16) Read active configuration of the data output channel")
    print("(8) Read project name                (17) Read recent measurement data (HEX dump only)") 
    print("(9) Read status overview")

    while True:
        try:
            commandAction = int(input("Enter read command: "))
            if 1 <= commandAction <= 17:
                break
            else:
                print("Please enter a number between 1 and 17.")
        except ValueError:
            print("Please enter a number between 1 and 17.")

    if commandAction == 1:
        data = make_request(ipAddress, "r", "0300" )
        print(f"\nSensor serial number: {str(data[22:30], 'utf-8')} / System plug serial number: {str(data[31:42], 'utf-8')}")

    elif commandAction == 2:
        data = make_request(ipAddress, "r", "0400" )
        print(f"\nFirmware version: {str(data[21:], 'utf-8')}")

    elif commandAction == 3:
        data = make_request(ipAddress, "r", "0d00" )
        print(f"\nType code: {str(data[21:], 'utf-8')}")

    elif commandAction == 4:
        data = make_request(ipAddress, "r", "0e00" )
        print(f"\nPart number: {str(data[21:], 'utf-8')}")

    elif commandAction == 5:
        data = make_request(ipAddress, "r", "0f00" )
        sopasDeviceStatus = int.from_bytes(data[20:], byteorder='little')
        print("\nSOPAS device status ", end="")
        if sopasDeviceStatus == 0:
            print("'0': Unclear device status")
        elif sopasDeviceStatus == 1:
            print("'1': Device start")
        elif sopasDeviceStatus == 2:
            print("'2': Service mode (e.g., firmware update, optics cover calibration)")
        elif sopasDeviceStatus == 3:
            print("'3': Normal operation")
        elif sopasDeviceStatus == 4:
            print("'4': Device is waiting (e.g., for communication partner or input signal)")
        elif sopasDeviceStatus == 5:
            print("'5': Maintenance recommended (e.g., contamination warning)")
        elif sopasDeviceStatus == 6:
            print("'6': Maintenance required (e.g., configuration incompatible)")
        elif sopasDeviceStatus == 7:
            print("'7': Correctable error (e.g., configuration error, network error)")
        elif sopasDeviceStatus == 8:
            print("'8': Serious error (e.g., contamination error, configuration error, network error)")
        else:
            print("Unexpected data. Please try again")

    elif commandAction == 6:
        data = make_request(ipAddress, "r", "1000" )
        noteTroubleshooting = int.from_bytes(data[20:], byteorder='little')
        print("\nNote on troubleshooting: ", end="")
        if noteTroubleshooting == 0:
            print("None")
        elif noteTroubleshooting == 1:
            print("Configure device, verify configuration")
        elif noteTroubleshooting == 2:
            print("Test configuration, test device variant")
        elif noteTroubleshooting == 4:
            print("Check communication partner, check manipulation")
        elif noteTroubleshooting == 8:
            print("Check input signals, check network and other connections")
        elif noteTroubleshooting == 16:
            print("Check the error messages")
        elif noteTroubleshooting == 32:
            print("Configure device (including network settings)")
        elif noteTroubleshooting == 64:
            print("Checking the firmware")
        elif noteTroubleshooting == 120:
            print("Wait a few seconds")

    elif commandAction == 7:
        data = make_request(ipAddress, "r", "1100" )
        print(f"\nDevice name: {str(data[21:], 'utf-8')}")

    elif commandAction == 8:
        data = make_request(ipAddress, "r", "1200" )
        print(f"\nProject name: {str(data[21:], 'utf-8')}")

    elif commandAction == 9:
        data = make_request(ipAddress, "r", "1700" )
        print(f"\nVersion: {str(data[20:21], 'utf-8')}{int.from_bytes(data[21:22], byteorder='little')}.{int.from_bytes(data[22:23], byteorder='little')}.", end="")
        print(int.from_bytes(data[23:24], byteorder='little'))

        eDeviceState = int.from_bytes(data[24:25], byteorder='little')
        print("Device state: ", end="")
        if eDeviceState == 0:
            print("Normal")
        elif eDeviceState == 1:
            print("Error")
        elif eDeviceState == 2:
            print("Initialization")
        elif eDeviceState == 3:
            print("Switch off")
        elif eDeviceState == 4:
            print("Optics cover calibration")
        else:
            print("Unexpected data. Please try again")

        eConfigState = int.from_bytes(data[25:26], byteorder='little')
        print("Configuration state: ", end="")
        if eConfigState == 0:
            print("Unknown")
        elif eConfigState == 1:
            print("Configuration missing")
        elif eConfigState == 2:
            print("device is being configured")
        elif eConfigState == 3:
            print("Not verified")
        elif eConfigState == 4:
            print("Declined")
        elif eConfigState == 5:
            print("Verified")
        elif eConfigState == 6:
            print("Internal error")
        elif eConfigState == 7:
            print("Configuration is being verified")
        else:
            print("Unexpected data. Please try again")

        eApplicationState = int.from_bytes(data[26:27], byteorder='little')
        print("Application state: ", end="")
        if eApplicationState == 0:
            print("Stopped")
        elif eApplicationState == 1:
            print("Starting")
        elif eApplicationState == 2:
            print("Waiting for partner")
        elif eApplicationState == 3:
            print("Waiting for inputs")
        elif eApplicationState == 4:
            print("Started")
        elif eApplicationState == 5:
            print("Standby state")
        else:
            print("Unexpected data. Please try again")

        print(f"Power on count: {int.from_bytes(data[32:36], byteorder='little')} (number of power cycles)")

        tCurrentTimetTime = int.from_bytes(data[36:40], byteorder='little')
        tCurrentTimetDate = int.from_bytes(data[40:42], byteorder='little')
        print("\nCurrent time and date without synchronization (since device was switched on):")
        print(f"Time: {tCurrentTimetTime} ms since start of current 24 hour cycle")
        print(f"Date: {tCurrentTimetDate} * 24 hour cycles")

        print("\nCurrent time and date with synchronization:")
        print(f"Time: {str(datetime.timedelta(milliseconds=tCurrentTimetTime))}")
        print(f"Date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=tCurrentTimetDate)}")

        print(f"\nError code on display: ", end="")
        tErrorCheck = b'\x00\x00\x00\x00'
        if tErrorCheck == data[44:48]:
            print("None")
        else: 
            errorCode = "".join(["{:02x}".format(x) for x in reversed(data[44:48])])
            print(errorCode.upper())
            tErrorInfotTime = int.from_bytes(data[72:76], byteorder='little')
            tErrorInfotDate = int.from_bytes(data[76:78], byteorder='little')
            print("Time and date of error without synchronization (since device was switched on)")
            print(f"Time: {tErrorInfotTime} ms since start of current 24 hour cycle")
            print(f"Date: {tErrorInfotDate} * 24 hour cycles")
            print("Time and date of error with synchronization:")
            print(f"Time: {str(datetime.timedelta(milliseconds=tErrorInfotTime))}")
            print(f"Date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=tErrorInfotDate)}")

    elif commandAction == 10:
        data = make_request(ipAddress, "r", "1c00" )
        print("\nMeta data of the configuration:")
        tModificationtDate = int.from_bytes(data[24:26], byteorder="little")
        tModificationtTime = int.from_bytes(data[28:32], byteorder="little")
        tTransfertDate = int.from_bytes(data[32:34], byteorder="little")
        tTransfertTime = int.from_bytes(data[36:40], byteorder="little")
        print(f"Modification date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=tModificationtDate)}")
        print(f"Modification time: {str(datetime.timedelta(milliseconds=tModificationtTime))}")
        print(f"Transfer date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=tTransfertDate)}")
        print(f"Transfer time: {str(datetime.timedelta(milliseconds=tTransfertTime))}")
        checksumFunction = "".join(["{:02x}".format(x) for x in data[56:60]])
        print(f"Checksum (function): 0x{checksumFunction.upper()}")
        checksumFunctionNetwork = "".join(["{:02x}".format(x) for x in data[72:76]])
        print(f"Checksum (function and network): 0x{checksumFunctionNetwork.upper()}")
        tIntegrityHash = "".join(["{:02x}".format(x) for x in data[88:104]])
        print(f"MD5 hash: 0x{tIntegrityHash.upper()}")
            
    elif commandAction == 11:
        data = make_request(ipAddress, "r", "2100" )
        tNameLengthApp = int.from_bytes(data[24:28], byteorder="little")
        print(f"\nApplication name: {str(data[28:28 + tNameLengthApp], 'utf-8')}")

    elif commandAction == 12:
        data = make_request(ipAddress, "r", "2300" )
        tNameLengthUser = int.from_bytes(data[24:28], byteorder="little")
        print(f"\nUser name: {str(data[28:28 + tNameLengthUser], 'utf-8')}")

    elif commandAction == 13:
        data = make_request(ipAddress, "r", "6a01" )
        temperature = int.from_bytes(data[26:28], byteorder='little')
        print(f"\nDevice temperature: {temperature/10} °C / {(temperature/10 * 1.8) + 32} °F")

    elif commandAction == 14:
        data = make_request(ipAddress, "r", "cbfa" )
        utcTimetDate = int.from_bytes(data[24:26], byteorder='little')
        utcTimetTime = int.from_bytes(data[28:32], byteorder='little')
        powerOntDate = int.from_bytes(data[52:54], byteorder='little')
        powerOntTime = int.from_bytes(data[56:60], byteorder='little')
        print("\nUTC time without synchronization (since device was switched on)")
        print(f"Time: {utcTimetTime} ms since start of current 24 hour cycle")
        print(f"Date: {utcTimetDate} * 24 hour cycles")
        print("\nUTC time with synchronization:")
        print(f"Time: {str(datetime.timedelta(milliseconds=utcTimetTime))}")
        print(f"Date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=utcTimetDate)}")
        print(f"\nTime difference to UTC: {int.from_bytes(data[36:40], byteorder='little')} minutes")
        print(f"Time zone: {str(data[40:48], 'utf-8')}")
        print("\nPower-on time without synchronization (since device was switched on)")
        print(f"Time: {powerOntTime} ms since start of current 24 hour cycle")
        print(f"Date: {powerOntDate} * 24 hour cycles")
        print("\nPower-on time with synchronization:")
        print(f"Time: {str(datetime.timedelta(milliseconds=powerOntTime))}")
        print(f"Date: {datetime.date(int(1972), 1, 1) + datetime.timedelta(days=powerOntDate)}")

    elif commandAction == 15:
        data = make_request(ipAddress, "r", "b100" )
        outputEnabled = int.from_bytes(data[24:25], byteorder='little')
        outputInterfaceType = int.from_bytes(data[25:26], byteorder='little')
        outputReceiverAddress = [byte for byte in reversed(data[28:32])]
        outputFeatures = "{0:16b}".format(int.from_bytes(data[44:46], byteorder='little'))
        print("\nSaved configuration of the data output:")
        if outputEnabled == 1:
            print("Output enabled: Yes")
        else:
            print("Output enabled: No")
        if outputInterfaceType == 0:
            print("Interface type: EFI-pro")
        elif outputInterfaceType == 1:
            print("Interface type: EtherNet/IP")
        elif outputInterfaceType == 3:
            print("Interface type: PROFINET")
        elif outputInterfaceType == 4:
            print("Interface type: Non-secure Ethernet")
        print(f"Receiver IP Address: {'.'.join(str(byte) for byte in outputReceiverAddress)}")
        print(f"Receiver Port address: {int.from_bytes(data[32:34], byteorder='little')}")
        print(f"Output frequency: Every {int.from_bytes(data[34:36], byteorder='little')} scan(s)")
        print(f"Start angle: {int.from_bytes(data[36:40], byteorder='little', signed=True) / 4194304} °")
        print(f"End angle: {int.from_bytes(data[40:44], byteorder='little', signed=True) / 4194304} °")
        print("Output features including:")
        if outputFeatures[15] == "1":
            print("--> Device status")
        if outputFeatures[14] == "1":
            print("--> Configuration of the data output")
        if outputFeatures[13] == "1":
            print("--> Measurement data")
        if outputFeatures[12] == "1":
            print("--> Field interruption")
        if outputFeatures[11] == "1":
            print("--> Application data") 
        if outputFeatures[10] == "1":
            print("--> Local inputs and outputs")       

    elif commandAction == 16:
        data = make_request(ipAddress, "r", "b200" )
        outputEnabled = int.from_bytes(data[24:25], byteorder='little')
        outputInterfaceType = int.from_bytes(data[25:26], byteorder='little')
        outputInterfaceType = int.from_bytes(data[25:26], byteorder='little')
        outputReceiverAddress = [byte for byte in reversed(data[28:32])]
        outputFeatures = "{0:16b}".format(int.from_bytes(data[44:46], byteorder='little'))
        print("\nActive configuration of the data output (Configured values):")
        if outputEnabled == 1:
            print("Output enabled: Yes")
        else:
            print("Output enabled: No")
        if outputInterfaceType == 0:
            print("Interface type: EFI-pro")
        elif outputInterfaceType == 1:
            print("Interface type: EtherNet/IP")
        elif outputInterfaceType == 3:
            print("Interface type: PROFINET")
        elif outputInterfaceType == 4:
            print("Interface type: Non-secure Ethernet")
        print(f"Receiver IP Address: {'.'.join(str(byte) for byte in outputReceiverAddress)}")
        print(f"Receiver Port address: {int.from_bytes(data[32:34], byteorder='little')}")
        print(f"Output frequency: Every {int.from_bytes(data[34:36], byteorder='little')} scan(s)")
        print(f"Start angle: {int.from_bytes(data[36:40], byteorder='little', signed=True) / 4194304} °")
        print(f"End angle: {int.from_bytes(data[40:44], byteorder='little', signed=True) / 4194304} °")
        print("Output features including:")
        if outputFeatures[15] == "1":
            print("--> Device status")
        if outputFeatures[14] == "1":
            print("--> Configuration of the data output")
        if outputFeatures[13] == "1":
            print("--> Measurement data")
        if outputFeatures[12] == "1":
            print("--> Field interruption")
        if outputFeatures[11] == "1":
            print("--> Application data") 
        if outputFeatures[10] == "1":
            print("--> Local inputs and outputs")
        print("\nActive configuration of the data output (Used values)")
        print(f"Multiplication factor: {int.from_bytes(data[48:50], byteorder='little')}")
        print(f"Number of beams: {int.from_bytes(data[50:52], byteorder='little')}")
        print(f"Scan time: {int.from_bytes(data[52:54], byteorder='little')} ms")
        print(f"Start angle: {int.from_bytes(data[56:60], byteorder='little', signed=True) / 4194304} °")
        print(f"Angular scan beam resolution: {int.from_bytes(data[60:64], byteorder='little', signed=True) / 4194304} °")
        print(f"Interbeam period: {int.from_bytes(data[64:68], byteorder='little')} µs")

    elif commandAction == 17:
        while True:
            try:
                channelNumber = int(input("Enter channel number(0...3): "))
                if 0 <= channelNumber < 4:
                    if channelNumber == 0:
                        messDataChannel = "b300"
                        break
                    elif channelNumber == 1:
                        messDataChannel = "b400"
                        break
                    elif channelNumber == 2:
                        messDataChannel = "b500"
                        break
                    elif channelNumber == 3:
                        messDataChannel = "b600"
                        break
                else: 
                    print("Sorry, no valid channel was selected. Please enter a number betweek 0 and 3.")
            except ValueError:
                print("Sorry, no valid channel was selected. Please enter a number betweek 0 and 3.")
            
        data = make_request(ipAddress, "r", messDataChannel )
        hexDump = data.hex()
        print("\nHEX dump of measurement data:")
        print(hexDump)

def method_command_selection(ipAddress):
    print("\nMethod selection...")
    print("(1) Identifying the device")
    print("(2) Configuring the data output")

    while True:
        try:
            commandAction = int(input("Enter method number: "))
            if 1 <= commandAction <= 2:
                break
            else:
                print("Please enter either 1 or 2.")
        except ValueError:
            print("Please enter either 1 or 2.")


    if commandAction == 1:
        print("\nThis method will activate the display (blue) for a defined time period.")
        while True:
            try:
                durationIdent = int(input("Please enter the identification duration in seconds (1...255): ")) 
                if 1 <= durationIdent <= 255:
                    break
                else:
                    print("Please enter a number between 1 and 255.")   
            except ValueError:
                print("Please enter a number between 1 and 255.")

        duration = hex(durationIdent)[2:].zfill(2)
        command = "0e00" + duration + "00"
        make_request(ipAddress, "m1", command)
        print(f"The device display should now be active for {durationIdent} seconds.")

    elif commandAction == 2:
        print("\nThis method will active the UDP data output as per the given parameters.")
        # IP Address entry, error handling and conversion
        while True:
            dataAddressIn = input("Enter IP Address (send to): ").split('.')
            dataAddress = ""
            if len(dataAddressIn) == 4:
                for segment in reversed(dataAddressIn):
                    try:
                        if int(segment) < 0 or int(segment) > 255:
                            print("Error: Part of the IP address was out of range [0 ... 255].")
                            break
                        else:
                            value = hex(int(segment))[2:]
                            if len(value) == 1:
                                value = value.zfill(2)
                            dataAddress += value
                    except ValueError:
                        print("Error: The IP Address contained invalid characters.")
                        break
                else:
                    break
            else:
                print("Error: The IP Address was an incorrect size. Please enter a valid IPv4 address.")

        # Port number entry, error handling and conversion
        while True:
            dataPortIn = input("Enter Port number (send to): ")
            try:
                dataPort = int(dataPortIn)
                if dataPort < 0 or dataPort > 65535:
                    print("Error: Port number was out of range [0 ... 65535].")
                else:
                    dataPort = "{:04X}".format(dataPort).lower()
                    dataPort = dataPort[2:] + dataPort[:2]
                    break
            except ValueError:
                print("Error: Port was not a valid integer.")

        # Device/interface entry, error handling and conversion
        print("Device type selection: EFI-pro: 0 - EtherNet/IP: 1 - PROFINET: 3 - Standard Ethernet/EtherCAT: 4")
        while True:
            try:
                dataInterface = int(input("Enter interface type (0, 1, 3 or 4): "))
                if dataInterface == 0 or dataInterface == 1 or dataInterface == 3 or dataInterface == 4:
                    dataInterface = "{:02X}".format(dataInterface)
                    break
                else:
                    print("Error: No valid interface type was given (0, 1, 3 or 4).")
            except ValueError:
                print("Error: The given value was not an integer.")

        # Quick run parameters - maximum data load
        activateAll = input("Set full data output (F) or set parameters manually? (m)? F/m: ").lower()
        if activateAll == "" or activateAll == "f":
            dataPublishing = "0100"
            dataAngleStart = "00000000"
            dataAngleEnd = "00000000"
            dataBlock = "3f00"
        else:
            while True:
                print("Sending rate (1 ... 40): Enter 1 for every measurement, 4 for every 4th measurement, etc.")
                dataPublishingIn = input("Enter the sending rate: ")
                try:
                    dataPublishing = int(dataPublishingIn)
                    if 1 <= dataPublishing <= 40:
                        dataPublishing = "{:02X}00".format(dataPublishing).lower()
                        break
                    else:
                        print("Error: The sending rate was not in the permitted range (1 ... 40).")
                except ValueError:
                    print("Error: The given value was not an integer.")

        # Data starting angle entry, error handling and conversion
        print("Starting and ending angles (from -47.5 ... 227.5). 0 as both for full scanning range.")
        while True:
            dataAngleStartIn = input("Enter starting angle: ")
            try:
                angleStartRaw = float(dataAngleStartIn) * 4194304
                if -47.5 <= float(dataAngleStartIn) <= 227.5:
                    valueHex = "{:08X}".format(int(angleStartRaw) & 0xFFFFFFFF).lower()
                    dataAngleStart = valueHex[6:8] + valueHex[4:6] + valueHex[2:4] + valueHex[0:2]
                    break
                else:
                    print("Error: The starting angle was not in the permitted range (-47.5 ... 227.5).")
            except ValueError:
                print("Error: The given value was not a number.")

        # Data ending angle entry, error handling and conversion
        while True:
            dataAngleEndIn = input("Enter ending angle: ")
            try:
                angleEnd = float(dataAngleEndIn)
                if not (-47.5 <= angleEnd <= 227.5):
                    print("Error: The end angle was not in the permitted range (-47.5 ... 227.5).")
                    continue
                if angleEnd == float(dataAngleStartIn):
                    if angleEnd != 0.0 or float(dataAngleStartIn) != 0.0:
                        print("Error: The start and end angles cannot be the same (except both given as 0).")
                        continue
                if angleEnd < float(dataAngleStartIn):
                    print("Error: The start angle cannot be higher than the end angle.")
                    continue
                break
            except ValueError:
                print("Error: The given value was not a number.")
                continue

        angleEndRaw = int(float(dataAngleEndIn) * 4194304)
        valueHex1 = "{:08X}".format(angleEndRaw & 0xFFFFFFFF).lower()
        dataAngleEnd = valueHex1[6:8] + valueHex1[4:6] + valueHex1[2:4] + valueHex1[0:2]

        # Data block selection entry, error handling and conversion
        dataBlockAll = input("Activate all data blocks? Y/n: ").lower()
        if dataBlockAll == "y" or dataBlockAll == "":
            dataBlock = "3f00"
        else:
            dataBlockOptions = {
                "Device Status": 'f',
                "Configuration of the data output": 'e',
                "Measurement data": 'd',
                "Field interruption": 'c',
                "Application data": 'b',
                "Local inputs and outputs": 'a',
            }
            dataBlockBin = "00abcdef00000000"
            for option, bit in dataBlockOptions.items():
                while True:
                    choice = input(f"Activate '{option}'? Y/n: ").lower()
                    if choice == 'y' or choice == 'n' or choice == "":
                        dataBlockBin = dataBlockBin.replace(bit, '1' if choice == 'y' or choice == '' else '0')
                        break
                    else:
                        print("Please enter either 'y' or 'n'.")
                        continue
            if dataBlockBin == "00abcdef00000000":
                print("Error: At least one data block must be selected.")
                input("Press enter to exit.")
                exit()
            dataBlock = hex(int(dataBlockBin, 2))[2:].zfill(4).lower()

        # Construct command from input variables
        command = dataInterface + "0000" + dataAddress + dataPort + dataPublishing + dataAngleStart + dataAngleEnd + dataBlock + "0000"
        make_request(ipAddress, "m2", command)
        print("The UDP data output should now be active.")

# Custom commands
def custom_command_selection(ipAddress):
    print("Please copy the correct CoLa2 command (in HEX).")
    print("Note: The session ID should be populated with a placeholder (e.g., 00000000).")
    pattern = r'^[0-9a-fA-F]+$'
    while True:
        command = input("HEX: ").lower().replace(' ','')
        checkHex = re.match(pattern, command)
        if checkHex:
            data = make_request(ipAddress, "c", command)
            print("\nThe target sensor responded:")
            print(f"In hex:    {data.hex()}")
            print(f"In binary: {data}")
            break
        else: 
            print("Please enter a valid hex response.")

# Program run process
print("CoLa2 Session Handler V2.0.0\n")

ipAddress = ip_address()

while True:
    commandSelect = command_selection()
    if commandSelect == 1:
        read_command_selection(ipAddress)
    elif commandSelect == 2:
        method_command_selection(ipAddress)
    else:
        custom_command_selection(ipAddress)
    repeatRequest = input("Would you like to make another request? Y/n: ").lower()
    if repeatRequest == "y" or repeatRequest == "":
        continue
    else:
        break

input("Press 'enter' to close the program.")
exit()
