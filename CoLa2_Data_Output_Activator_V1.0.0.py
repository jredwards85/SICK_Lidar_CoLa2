# CoLa2 Data Output Activator - V1.0.0 
# Written by James Edwards

import math
import re
import socket
import time

# IP address of device to be configured, plus checks
ipAddress = input("Enter IP Address of device : ")
ipAddressCheck = ipAddress.split('.')
if len(ipAddressCheck) == 4:
    for segment in reversed(ipAddressCheck):
        try:
            if int(segment) < 0 or int(segment) > 255:
                print("Error: Part of the IP address was out of range [0 ... 255].")
                input("Press enter to exit.")
                exit()
        except ValueError:
            print("Error: The IP Address contained invalid characters.")
            input("Press enter to exit.")
            exit()
else:
    print("Error: The IP Address was an incorrect size. Please enter a valid IPv4 address.")
    input("Press enter to exit.")
    exit()

# IP Address entry, error handling and conversion
dataAddressIn = input("Enter IP Address (send to): ").split('.')
dataAddress = ""
if len(dataAddressIn) == 4:
    for segment in reversed(dataAddressIn):
        try:
            if int(segment) < 0 or int(segment) > 255:
                print("Error: Part of the IP address was out of range [0 ... 255].")
                input("Press enter to exit.")
                exit()
            else:
                value = hex(int(segment))[2:]
                if len(value) == 1:
                    value = value.zfill(2)
                dataAddress += value
        except ValueError:
            print("Error: The IP Address contained invalid characters.")
            input("Press enter to exit.")
            exit()
else:
    print("Error: The IP Address was an incorrect size. Please enter a valid IPv4 address.")
    input("Press enter to exit.")
    exit()

# Port number entry, error handling and conversion
dataPortIn = input("Enter Port number (send to): ")
dataPort = ""
try:
    if int(dataPortIn) < 0 or int(dataPortIn) > 65535:
        print("Error: Port number was out of range [0 ... 65535].")
        input("Press enter to exit.")
        exit()
    else:
        value = hex(int(dataPortIn))[2:]
        if len(value) < 4:
            value = value.zfill(4)
        dataPort = value[2:4] + value[0:2]
except ValueError:
    print("Error: Port was not a valid integer.")
    input("Press enter to exit.")
    exit()

# Data Interface entry, error handling and conversion
print("Device type selection: EFI-pro: 0 - EtherNet/IP: 1 - EtherCAT: 2 - PROFINET: 3 - Standard Ethernet: 4")
dataInterfaceIn = input("Enter interface type (0 ... 4 as above): ")
dataInterface = ""
try:
    if int(dataInterfaceIn) > -1 or int(dataInterfaceIn) < 5:
        value = hex(int(dataInterfaceIn))[2:]
        if len(value) == 1:
            value = value.zfill(2)
        dataInterface = value
    else:
        print("Error: No valid interface type was given (0 ... 4).")
        input("Press enter to exit.")
        exit()
except ValueError:
        print("Error: The given value was not an integer.")
        input("Press enter to exit.")
        exit()

# Quick run parameters - maximum data load
activateAll = input("Set full data output (F) or set parameters manually? (m)? F/m: ").lower()
if activateAll == "" or activateAll == "f":
    dataPublishing = "0100"
    dataAngleStart = "00000000" 
    dataAngleEnd = "00000000"
    dataBlock = "3f00" 
else:
    # Data sending rate entry, error handling and conversion
    print("Sending rate (1 ... 40): Enter 1 for every measurement,  4 for every 4th measurement, etc.")
    dataPublishingIn = input("Enter the sending rate: ")
    dataPublishing = "00"
    try:
        if int(dataPublishingIn) > 0 and int(dataPublishingIn) < 41:
            value = hex(int(dataPublishingIn))[2:]
            if len(value) == 1:
                value = value.zfill(2)
            dataPublishing = value + dataPublishing
        else:
            print("Error: The sending rate was not in the permitted range (1 ... 40).")
            input("Press enter to exit.")
            exit()
    except ValueError:
            print("Error: The given value was not an integer.")
            input("Press enter to exit.")
            exit()

    # Data starting angle entry, error handling and conversion
    print("Starting and ending angles (from -47.5 ... 227.5). 0 as both for full scanning range.")
    dataAngleStartIn = input("Enter starting angle: ")
    try:
        if float(dataAngleStartIn) > -47.6 and float(dataAngleStartIn) < 227.6:
            pass
        else:
            print("Error: The starting angle was not in the permitted range (-47.5 ... 227.5).")
            input("Press enter to exit.")
            exit()
    except ValueError:
        print("Error: The given value was not a number.")
        input("Press enter to exit.")
        exit()
    angleStartRaw = float(dataAngleStartIn) * 4194304
    angleStartRawInt = math.trunc(angleStartRaw)
    if angleStartRaw > -1:
        valueHex = hex(angleStartRawInt)[2:]
    else:
        valueHex = hex(angleStartRawInt & (2**32-1))[2:]
    if len(valueHex) < 8:
        valueHex = valueHex.zfill(8)
    hexConvert = re.findall('..', valueHex)
    dataAngleStart = hexConvert[3] + hexConvert[2] + hexConvert[1] + hexConvert[0]

    # Data ending angle entry, error handling and conversion
    dataAngleEndIn = input("Enter ending angle: ")
    try:
        if float(dataAngleEndIn) > -47.6 and float(dataAngleEndIn) < 227.6:
            if float(dataAngleEndIn) == float(dataAngleStartIn):
                if float(dataAngleEndIn) == 0.0 and float(dataAngleStartIn) == 0.0:
                    pass
                else:
                    print("Error: The start and end angles cannot be the same (except both given as 0).")
                    input("Press enter to exit.")
                    exit()
            elif float(dataAngleEndIn) < float(dataAngleStartIn):
                print("Error: The start angle cannot be higher than the end angle.")
                input("Press enter to exit.")
                exit() 
            else:
                pass
        else:
            print("Error: The end angle was not in the permitted range (-47.5 ... 227.5).")
            input("Press enter to exit.")
            exit()
    except ValueError:
        print("Error: The given value was not a number.")
        input("Press enter to exit.")
        exit()
    angleEndRaw = float(dataAngleEndIn) * 4194304
    angleEndRawInt = math.trunc(angleEndRaw)
    if angleEndRaw > -1:
        valueHex1 = hex(angleEndRawInt)[2:]
    else:
        valueHex1 = hex(angleEndRawInt & (2**32-1))[2:]
    if len(valueHex1) < 8:
        valueHex1 = valueHex1.zfill(8)
    hexConvert2 = re.findall('..', valueHex1)
    dataAngleEnd = hexConvert2[3] + hexConvert2[2] + hexConvert2[1] + hexConvert2[0]

    # Data block selection entry, error handling and conversion
    dataBlockAll = input("Activate all data blocks? Y/n: ").lower()
    if dataBlockAll == "y" or dataBlockAll == "":
        dataBlock = "3f00"
    else:
        dataBlockBin = "abcdef00000000"
        dataBlock1 = input("Activate 'Device Status'? Y/n: ").lower()
        if dataBlock1 == "y" or dataBlock1 == "":
            dataBlockBin = dataBlockBin.replace('f', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('f', '0')
        dataBlock2 = input("Activate 'Configuration of the data output'? Y/n: ").lower()
        if dataBlock2 == "y" or dataBlock2 == "":
            dataBlockBin = dataBlockBin.replace('e', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('e', '0')
        dataBlock3 = input("Activate 'Measurement data'? Y/n: ").lower()
        if dataBlock3 == "y" or dataBlock3 == "":
            dataBlockBin = dataBlockBin.replace('d', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('d', '0')
        dataBlock4 = input("Activate 'Field interruption'? Y/n: ").lower()
        if dataBlock4 == "y" or dataBlock4 == "":
            dataBlockBin = dataBlockBin.replace('c', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('c', '0')
        dataBlock5 = input("Activate 'Application data'? Y/n: ").lower()
        if dataBlock5 == "y" or dataBlock5 == "":
            dataBlockBin = dataBlockBin.replace('b', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('b', '0')
        dataBlock6 = input("Activate 'Local inputs and outputs'? Y/n: ").lower()
        if dataBlock6 == "y" or dataBlock6 == "":
            dataBlockBin = dataBlockBin.replace('a', '1')
        else: 
            dataBlockBin = dataBlockBin.replace('a', '0')
        if dataBlockBin == "00000000000000":
            print("Error: At least one data block must be selected.")
            input("Press enter to exit.")
            exit()
        dataBlock = hex(int(dataBlockBin, 2))[2:]
        if len(dataBlock) < 4:
            dataBlock = dataBlock.zfill(4)

# Port number for target device
portNumber = int(2122)

# Create CoLa2 session
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.settimeout(1)
try: 
    tcp_socket.connect((ipAddress, portNumber))
    data = bytearray.fromhex("020202020000000d00000000000000014f581e0000") 
    tcp_socket.sendall(data)

    # While reading session ID, allows for fragmented data responses (max. duration 250 ms)
    t_end = time.time() + 0.25
    data = b''
    while time.time() < t_end:
        try:
            part = tcp_socket.recv(2122)
            data += part
        except socket.timeout:
            stop = True
            pass
        except socket.error as e:
            print("Oops, an unknown error occured: Please ensure you entered all values correctly.")
            input("Press enter to exit.")
            exit()

    # Constructs the command request with correct session ID        
    response  = data.hex()
    if response == "" or len(response) < 28:
        print("Error: The target provided no response or an incorrect response to creating a session. Please try again.")
        input("Press enter to exit.")
        exit()
    sessionID = response[20:28]
    dataReqHeader0 = "02020202000000280000"
    dataReqHeader1 = "00034d49b0000000000001"
    commandHex = dataReqHeader0 + sessionID + dataReqHeader1 + dataInterface + "0000" + dataAddress + dataPort + dataPublishing + dataAngleStart + dataAngleEnd + dataBlock + "0000"
    commandData = bytearray.fromhex(commandHex)
    tcp_socket.sendall(commandData)
    
    # While reading request response, allows for fragmented data responses (max. duration 250 ms)
    t_end = time.time() + 0.25
    data = b''
    while time.time() < t_end:
        try:
            part = tcp_socket.recv(2122)
            data += part
        except socket.timeout:
            stop = True
            pass
        except socket.error as e:
            print("Oops, an unknown error occured: Please ensure you entered all values correctly.")
            input("Press enter to exit.")
            exit()
    if data.hex() == "":
        print("Error: The target provided no response to activating the data output.")
        tcp_socket.close()
        input("Press enter to exit.")
        exit()

    # Error handling for CoLa2 error codes. Outputs the error code for the user 
    colaError = data.hex()
    if colaError[32:36] == "4641":
        errorCode = colaError[37:40][::-1]
        print(f"Error code: {errorCode}. Please refer to the data output error codes.")
        tcp_socket.close()
        input("Press enter to exit.")
        exit()

    # Prints the response from port 2122 and closes the TCP session
    commandResponse = data.hex()
    if commandResponse[32:36] == "4149":
        print("Response from device confirms data output over UDP has been activated.")
        print("The data output should now be visible in a tool such as Wireshark.")
    else:
        print("A response was provided, but did not confirm the activation of data output over UDP.")
        data_hex = data.hex()
        data_hex = (' ').join(re.findall('.{1,2}',data_hex))
        print("Reply from target:")
        print("Reply in hex:   ", data_hex)
        print("Reply in ascii: ", data)
        tcp_socket.close()
        input("Press enter to exit.")
        exit()

    # Close CoLa2 Session, sleep 250 ms to allow CoLa2 session close confirmation, close TCP
    closeSession1 = "020202020000000a0000"  
    closeSession2 = "00054358"
    closeSessionHex = closeSession1 + sessionID + closeSession2
    closeSession = bytearray.fromhex(closeSessionHex) 
    tcp_socket.sendall(closeSession) 
    time.sleep(0.25)
    tcp_socket.close()
    print("CoLa2 session closed. TCP connection closed.")
    input("Press enter to exit.")
    exit()   

# Error handling for the TCP session function
except TimeoutError:
    print("Timeout error: The IP Address is probably incorrect.")
    input("Press enter to exit.")
    exit()

except Exception as e:
    print(e)
    print("Oops, an unknown error occured: Please ensure all network devices/parameters are correct and working.")
    input("Press enter to exit.")
    exit()
