import datetime, socket, time

print("To read data from a SICK microScan3, outdoorScan3 or nanoScan3, please enter 'y' (default). Otherwise, enter 'n'")
modeSelect = input("Enter Y/n: ").lower()

if modeSelect == "y" or modeSelect == "":
    modeRead = True
    modeUDP = False
    modeTCP = False
else:
    modeRead = False

if modeRead == False:
    print("To paste TCP data (as HEX), enter 't'. To paste UDP data (as HEX), enter 'u'.")
    modeCopy = input("Enter t/u: ").lower()
    if modeCopy == "t":
        modeTCP = True
        modeUDP = False
    elif modeCopy == "u":
        modeTCP = False
        modeUDP = True
    else:
        input("No function was selected. Press 'Enter' to close the program.")
        exit()

    if modeUDP == True:
        print("Please copy the UDP data below. Note: All UDP frames (for a single scan) must be copied in valid HEX.")
        
        dataDump = input("Please copy the complete UDP data here: ").lower().replace(' ', '').replace('\n', '')
        
        # Extract UDP headers
        udpHeaders = []
        udpIndexes = []
        index = 0

        for i in range(0, 24, 1):
            index = dataDump.find("4d533320", index)
            if index != -1:
                udpHeaders.append(dataDump[index:index+48])
                udpIndexes.append(index)
                index = index + 4
            else:
                break

        # Check all frames share the same identification
        frameCount = len(udpHeaders)
        frameID = "initial"
        for i in range(0, frameCount, 1):
            if frameID == "initial" or frameID == udpHeaders[i][24:32]:
                frameID = udpHeaders[i][24:32]
            else:
                print("Error: Frame ID's didn't match. Program stopped.")
                exit()

        # Check frame order and if necessary reconstruct in correct order (UDP doesn't guarantee delivery sequence!)
        udpHeaderOffsets = []
        for i in range(0, frameCount, 1):
            offsetReorder = udpHeaders[i][38:40] + udpHeaders[i][36:38] + udpHeaders[i][34:36] + udpHeaders[i][32:34]
            offsetInteger = int(offsetReorder, 16)
            udpHeaderOffsets.append(offsetInteger)

        orderCheck = udpHeaderOffsets[:]
        orderCheck.sort()
        if orderCheck == udpHeaderOffsets:
            pass
        else:
            frameFragments = []
            for i in range(0, frameCount, 1):
                try:
                    frameFragments.append(dataDump[udpIndexes[i]:udpIndexes[i + 1]])
                except IndexError:
                    frameFragments.append(dataDump[udpIndexes[i]:])
            dataDump = ""
            for i in range(0, len(orderCheck), 1):
                for j in range(0, len(udpHeaderOffsets), 1):
                    if orderCheck[i] == udpHeaderOffsets[j]:
                        dataDump += frameFragments[j]
                    else:
                        pass
            
            udpHeaders = []
            udpIndexes = []
            index = 0

            for i in range(0, 24, 1):
                index = dataDump.find("4d533320", index)
                if index != -1:
                    udpHeaders.append(dataDump[index:index+48])
                    udpIndexes.append(index)
                    index = index + 4
                else:
                    break

        # Strip UDP headers
        dataOutputHex = ""
        dataOutputFragment = ""

        for i in reversed(range(0, frameCount, 1)):
            dataOutputFragment = dataDump[udpIndexes[i] + 48:]
            dataOutputHex = dataOutputFragment + dataOutputHex
            dataDump = dataDump[:udpIndexes[i]]

    if modeTCP == True:
        print("Please copy the TCP data below. Note: All TCP frames (for a single scan) must be copied in valid HEX.")
        dataDump = input("Please copy the complete TCP data here: ").lower().replace(' ', '').replace('\n', '')
        
        # Removes CoLa2 request response header (i.e. 02020202...)
        dataOutputHex = dataDump[40:]

if modeRead == True:
    print("To read the data output, please enter the IP address of the target device below.")
    print("Channel 0 is default. To change channel (0...3), please enter 'c' instead of the IP address.")
    ipAddress = input("IP Address: ")
    portNumber = int(2122)

    # Allows user to change channel of the measurement data
    if ipAddress.lower() == "c":
        channelSelect = -1

        while int(channelSelect) < 0 or int(channelSelect) > 3:
            channelSelect = input("Enter the channel (0...3): ")
            channelTest = channelSelect.isdigit()
            if channelTest == False:
                channelSelect = -1
                print("Please enter a channel number of 0...3!")

        print(f"Channel {channelSelect} has been selected.")
        print("To read the data output, please enter the IP address of the target device below.")
        ipAddress = input("IP Address: ")
        if int(channelSelect) == 0:
            channel = "b300"
        if int(channelSelect) == 1: 
            channel = "b400"
        if int(channelSelect) == 2: 
            channel = "b500"
        if int(channelSelect) == 3: 
            channel = "b600"
    else:
        channel = "b300"

    # Checks IP address is valid
    ipAddressCheck = ipAddress.split('.')
    if len(ipAddressCheck) == 4:
        for segment in reversed(ipAddressCheck):
            try:
                if int(segment) < 0 or int(segment) > 255:
                    print("Error: Part of the IP address was out of range [0 ... 255].")
                    input("Press 'Enter' to close the program.")
                    exit()
            except ValueError:
                print("Error: The IP Address contained invalid characters.")
                input("Press 'Enter' to close the program.")
                exit()
    else:
        print("Error: The IP Address was entered incorrectly. Please enter a valid IPv4 address.")
        input("Press 'Enter' to close the program.")
        exit()


    # Creates TCP session and reads session ID
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(1)

    try: 
        tcp_socket.connect((ipAddress, portNumber))

        data = bytearray.fromhex("020202020000000d00000000000000014f581e0000") 
        tcp_socket.sendall(data)

        # While reading session ID, allows for fragmented data responses (max. duration 250 ms)
        t_end = time.time() + 0.25
        stop = False
        data = b''

        while time.time() < t_end or stop == False:
            try:
                part = tcp_socket.recv(2122)
                data += part
            except socket.timeout:
                stop = True
                pass
            except socket.error as e:
                print(e)
                input("Press 'Enter' to close the program.")
                exit()

        response  = data.hex()

        # Check the response is correct
        if response == "" or len(response) < 28:
            print("Error: The target provided no response or an incorrect response to creating a session. Please try again.")
            input("Press 'Enter' to close the program.")
            exit()

        # Construct request to read data and send
        sessionID = response[20:28]
        request = "020202020000000c0000" + sessionID + "00015249" + channel
        data = bytearray.fromhex(request)
        tcp_socket.sendall(data)

        # While reading data output, allows for fragmented data responses (max. duration 250 ms)
        t_end = time.time() + 0.25
        stop = False
        data = b''

        while time.time() < t_end or stop == False:
            try:
                part = tcp_socket.recv(2122)
                data += part
            except socket.timeout:
                stop = True
                pass
            except socket.error as e:
                print(e)
                input("Press 'Enter' to close the program.")
                exit()

        if data.hex() == "":
            print("Error: The target provided no response to your request.")
            tcp_socket.close()
            input("Press 'Enter' to close the program.")
            exit()

        # Close CoLa2 Session, sleep 250 ms to allow CoLa2 session close confirmation, close TCP
        closeSessionHex = "020202020000000a0000"  + sessionID + "00054358"
        closeSession = bytearray.fromhex(closeSessionHex) 
        tcp_socket.sendall(closeSession) 
        time.sleep(0.25)
        tcp_socket.close()

        # Convert data response to hex
        dataDump = data.hex()

        # Removes CoLa2 request response header (i.e. 02020202...)
        dataOutputHex = dataDump[40:]
        
    # Error handling for the TCP session function
    except TimeoutError:
        print("Timeout error: The IP Address is probably incorrect.")
        input("Press 'Enter' to close the program.")
        exit()

    except Exception as e:
        print(e)
        input("Press 'Enter' to close the program.")
        exit()

try:
    # Extract header data and check for valid data in header
    # If the wrong channel is used, the header is all 0's.
    dataHeader = dataOutputHex[:112]

    dataVerification = int(dataHeader, 16)
    if dataVerification == 0:
        print("Error: The received data was not correct.")
        print("This may occur if the wrong channel was selected.")
        print("Please try again with another channel. E.g., if you entered channel 1, try channel 0.")
        input("Press 'Enter' to close the program.")
        exit()
    else:
        pass

    # Check data blocks and extract data
    blockStatus = False
    blockStatusOffset = int(dataOutputHex[66:68] + dataOutputHex[64:66], 16) * 2
    blockStatusSize = int(dataOutputHex[70:72] + dataOutputHex[68:70], 16)  * 2

    blockConfig = False
    blockConfigOffset = int(dataOutputHex[74:76] + dataOutputHex[72:74], 16) * 2
    blockConfigSize = int(dataOutputHex[78:80] + dataOutputHex[76:78], 16) * 2

    blockMess = False
    blockMessOffset = int(dataOutputHex[82:84] + dataOutputHex[80:82], 16) * 2
    blockMessSize = int(dataOutputHex[86:88] + dataOutputHex[84:86], 16) * 2

    blockField = False
    blockFieldOffset = int(dataOutputHex[90:92] + dataOutputHex[88:90], 16) * 2
    blockFieldSize = int(dataOutputHex[94:96] + dataOutputHex[92:94], 16) * 2

    blockApp = False
    blockAppOffset = int(dataOutputHex[98:100] + dataOutputHex[96:98], 16) * 2
    blockAppSize = int(dataOutputHex[102:104] + dataOutputHex[100:102], 16) * 2

    blockLocal = False
    blockLocalOffset = int(dataOutputHex[106:108] + dataOutputHex[104:106], 16) * 2
    blockLocalSize = int(dataOutputHex[110:112] + dataOutputHex[108:110], 16) * 2

    # Open .txt file and generate name (DataOutput + date.txt)
    time = datetime.datetime.now()
    nameExtension = time.strftime("%d-%m-%Y_%H-%M-%S")
    file = open(f"DataOutput_{nameExtension}.txt", "w", encoding="utf8")
    file.write("Ethernet data output viewer (V1.0.1) by James Edwards\n\nThe following data blocks are included in addition to the header:\n")

    if blockStatusOffset != 0:
        blockStatus = True
        blockStatusData = dataOutputHex[blockStatusOffset:blockStatusOffset + blockStatusSize]
        file.write("Data output: Block Device status\n")

    if blockConfigOffset != 0:
        blockConfig = True
        blockConfigData = dataOutputHex[blockConfigOffset:blockConfigOffset + blockConfigSize]
        file.write("Data output: Block Configuration of the data output\n")

    if blockMessOffset != 0:
        blockMess = True
        blockMessData = dataOutputHex[blockMessOffset:blockMessOffset + blockMessSize]
        file.write("Data output: Block Measurement data\n")

    if blockFieldOffset != 0:
        blockField = True
        blockFieldData = dataOutputHex[blockFieldOffset:blockFieldOffset + blockFieldSize]
        file.write("Data output: Block Field interruption\n")

    if blockAppOffset != 0:
        blockApp = True
        blockAppData = dataOutputHex[blockAppOffset:blockAppOffset + blockAppSize]
        file.write("Data output: Block Application data\n")

    if blockLocalOffset != 0:
        blockLocal = True
        blockLocalData = dataOutputHex[blockLocalOffset:blockLocalOffset + blockLocalSize]
        file.write("Data output: Block Local inputs and outputs\n")

    # Data output header values
    headerVersion = bytearray.fromhex(dataHeader[0:2]).decode()
    headerMajor = int(dataHeader[2:4], 16)
    headerMinor = int(dataHeader[4:6], 16)
    headerRelease = int(dataHeader[6:8], 16)
    headerDeviceSerial = int(dataHeader[14:16] + dataHeader[12:14] + dataHeader[10:12] + dataHeader[8:10], 16)
    headerPlugSerial = int(dataHeader[22:24] + dataHeader[20:22] + dataHeader[18:20] + dataHeader[16:18], 16)
    headerChannel = int(dataHeader[24:26], 16)
    headerSequenceNo = int(dataHeader[30:32] + dataHeader[28:30] + dataHeader[26:28] + dataHeader[24:26], 16)
    headerScanNo = int(dataHeader[46:48] + dataHeader[44:46] + dataHeader[42:44] + dataHeader[40:42], 16)

    # Data output header values for time stamp - supporting integer and time server values (1972.01.01) with suffix Sync
    headerTimeDate = int(dataHeader[50:52] + dataHeader[48:50], 16)
    headerTimeDateSync = datetime.date(int(1972), 1, 1) + datetime.timedelta(days=headerTimeDate)
    headerTimeTime = int(dataHeader[62:64] + dataHeader[60:62] + dataHeader[58:60] + dataHeader[56:58], 16)
    headerTimeTimeSync = str(datetime.timedelta(milliseconds=headerTimeTime))

    # Write header to file
    file.write("\n\n*** Data output: Header ***\n\n" +
    "Version: " + str(headerVersion) + str(headerMajor) + "." + str(headerMinor) + "." + str(headerRelease) + "\n" + 
    "Device serial number: " + str(headerDeviceSerial) + "\n" 
    "System plug serial number: " + str(headerPlugSerial) + "\n" 
    "Channel number: " + str(headerChannel) + "\n" 
    "Sequence number: " + str(headerSequenceNo) + "\n" 
    "Scan number: " + str(headerScanNo) + "\n" 
    "Date: " + str(headerTimeDate) + " (days since powered on) or " + str(headerTimeDateSync) + " (with time synchronization)" + "\n"
    "Time: " + str(headerTimeTime) + " (ms since current 24h cycle) or " + str(headerTimeTimeSync) + " (with time synchronization)" + "\n\n")

    # Contents of the block Device status. Values as bytes/bits reference. All other bytes/bits are reserved
    if blockStatus == True:
        # Byte 0 device status bits
        statusByte0 = "{0:08b}".format(int(blockStatusData[0:2], 16))
        statusByte0Bit0 = statusByte0[7]
        statusByte0Bit1 = statusByte0[6]
        statusByte0Bit2 = statusByte0[5]
        statusByte0Bit3 = statusByte0[4]
        statusByte0Bit4 = statusByte0[3]
        statusByte0Bit5 = statusByte0[2]

        # Byte 1 device status bits
        statusByte1 = "{0:08b}".format(int(blockStatusData[2:4], 16))
        statusByte1Bit0 = statusByte1[7]
        statusByte1Bit1 = statusByte1[6]
        statusByte1Bit2 = statusByte1[5]
        statusByte1Bit3 = statusByte1[4]
        statusByte1Bit4 = statusByte1[3]
        statusByte1Bit5 = statusByte1[2]
        statusByte1Bit6 = statusByte1[1]
        statusByte1Bit7 = statusByte1[0]

        # Byte 4 device status bits
        statusByte4 = "{0:08b}".format(int(blockStatusData[8:10], 16))
        statusByte4Bit0 = statusByte4[7]
        statusByte4Bit1 = statusByte4[6]
        statusByte4Bit2 = statusByte4[5]
        statusByte4Bit3 = statusByte4[4]
        statusByte4Bit4 = statusByte4[3]
        statusByte4Bit5 = statusByte4[2]
        statusByte4Bit6 = statusByte4[1]
        statusByte4Bit7 = statusByte4[0]

        # Byte 7 device status bits
        statusByte7 = "{0:08b}".format(int(blockStatusData[14:16], 16))
        statusByte7Bit0 = statusByte7[7]
        statusByte7Bit1 = statusByte7[6]
        statusByte7Bit2 = statusByte7[5]
        statusByte7Bit3 = statusByte7[4]
        statusByte7Bit4 = statusByte7[3]
        statusByte7Bit5 = statusByte7[2]
        statusByte7Bit6 = statusByte7[1]
        statusByte7Bit7 = statusByte7[0]

        # Bytes 10 and 11 device status bits
        statusByte10 = int(blockStatusData[20:22], 16)
        statusByte11 = int(blockStatusData[22:24], 16)

        # Byte 15 device status bits
        statusByte15 = "{0:08b}".format(int(blockStatusData[30:32], 16))
        statusByte15Bit0 = statusByte15[7]
        statusByte15Bit1 = statusByte15[6]

        # Write Block Device Status to file
        file.write("\n*** Data output: Block Device Status  ***\n\n" +
        "Status of the safety function: " + str(statusByte0Bit0) + "\n" + 
        "Status sleep mode: " + str(statusByte0Bit1) + "\n" + 
        "Contamination warning: " + str(statusByte0Bit2) + "\n" + 
        "Contamination error: " + str(statusByte0Bit3) + "\n" + 
        "Reference contour monitoring: " + str(statusByte0Bit4) + "\n" + 
        "Manipulation: " + str(statusByte0Bit5) + "\n\n" + 
        "Cut-off path 01 (safe): " + str(statusByte1Bit0) + "\n" + 
        "Cut-off path 02 (safe): " + str(statusByte1Bit1) + "\n" + 
        "Cut-off path 03 (safe): " + str(statusByte1Bit2) + "\n" + 
        "Cut-off path 04 (safe): " + str(statusByte1Bit3) + "\n" + 
        "Cut-off path 05 (safe): " + str(statusByte1Bit4) + "\n" + 
        "Cut-off path 06 (safe): " + str(statusByte1Bit5) + "\n" + 
        "Cut-off path 07 (safe): " + str(statusByte1Bit6) + "\n" + 
        "Cut-off path 08 (safe): " + str(statusByte1Bit7) + "\n\n" + 
        "Cut-off path 01 (non-safe): " + str(statusByte4Bit0) + "\n" + 
        "Cut-off path 02 (non-safe): " + str(statusByte4Bit1) + "\n" + 
        "Cut-off path 03 (non-safe): " + str(statusByte4Bit2) + "\n" + 
        "Cut-off path 04 (non-safe): " + str(statusByte4Bit3) + "\n" + 
        "Cut-off path 05 (non-safe): " + str(statusByte4Bit4) + "\n" + 
        "Cut-off path 06 (non-safe): " + str(statusByte4Bit5) + "\n" + 
        "Cut-off path 07 (non-safe): " + str(statusByte4Bit6) + "\n" + 
        "Cut-off path 08 (non-safe): " + str(statusByte4Bit7) + "\n\n" +
        "Reset required, cut-off path 01: " + str(statusByte7Bit0) + "\n" + 
        "Reset required, cut-off path 02: " + str(statusByte7Bit1) + "\n" + 
        "Reset required, cut-off path 03: " + str(statusByte7Bit2) + "\n" + 
        "Reset required, cut-off path 04: " + str(statusByte7Bit3) + "\n" + 
        "Reset required, cut-off path 05: " + str(statusByte7Bit4) + "\n" + 
        "Reset required, cut-off path 06: " + str(statusByte7Bit5) + "\n" + 
        "Reset required, cut-off path 07: " + str(statusByte7Bit6) + "\n" + 
        "Reset required, cut-off path 08: " + str(statusByte7Bit7) + "\n\n" + 
        "Current monitoring case (table 1): " + str(statusByte10) + "\n" + 
        "Current monitoring case (table 2): " + str(statusByte11) + "\n\n" + 
        "Application error: " + str(statusByte15Bit0) + "\n" + 
        "Device error: " + str(statusByte15Bit1) + "\n\n")

    # Data output: Block configuration of the data output
    if blockConfig == True:
        # Factor        0 - 4
        configFactor  = float(blockConfigData[2:4] + blockConfigData[0:2])
        # Num beams     4 - 8
        configBeams = int(blockConfigData[6:8] + blockConfigData[4:6], 16)
        # Cycle time    8 - 12
        configScanCycle = int(blockConfigData[10: 12] + blockConfigData[8:10], 16)
        # Start angle   16 - 24
        configStart = int.from_bytes(bytes.fromhex(blockConfigData[16:24]), byteorder='little', signed=True) / 4194304
        # Angular res   24 - 32
        configRes = int.from_bytes(bytes.fromhex(blockConfigData[24:32]), byteorder='little', signed=True) / 4194304
        # Beam interval 32 - 40
        configInterval = int(blockConfigData[38:40] + blockConfigData[36:38] + blockConfigData[34:36] + blockConfigData[32:34], 16)
        
        # Write Block configuration of the data output to file
        file.write("\n*** Data output: Block configuration of the data output ***\n\n" +
        "Factor: " + str(configFactor) + " (fixed as 1)\n" +
        "Number of beams: " + str(configBeams) + "\n" +
        "Scan cycle time: " + str(configScanCycle) + " ms\n" +
        "Start angle: " + str(configStart) + " °\n" +
        "Angular resolution: " + str(configRes) + " °\n" +
        "Beam interval: " + str(configInterval) + " µs\n\n")

    # Data output: Block measurement data 
    if blockMess == True:
        
        # Initial values and indexes (location in blockMessData of first beam)
        messBeamNum = 1
        messBeamMMByte2from = 10
        messBeamMMByte2to = 12
        messBeamMMByte1from = 8
        messBeamMMByte1to = 10
        messBeamRSSIByte1From = 12
        messBeamRSSIByte1To = 14
        messBeamStatusByte1from = 14 
        messBeamStatusByte1to = 16

        # First beam data
        messNumberBeams = int(blockMessData[6:8] + blockMessData[4:6] + blockMessData[2:4] + blockMessData[0:2], 16)
        messBeamMM = int(blockMessData[messBeamMMByte2from:messBeamMMByte2to] + blockMessData[messBeamMMByte1from:messBeamMMByte1to], 16)
        messBeamRSSI = int(blockMessData[messBeamRSSIByte1From:messBeamRSSIByte1To], 16)
        messBeamStatus = "{0:08b}".format(int(blockMessData[messBeamStatusByte1from:messBeamStatusByte1to], 16))

        if blockConfig == True:
            messBeamAngle = configStart
            messAngleRes = configRes

        # Data generation for each beam
        file.write("\n*** Data output: Block measurement data ***\n\n")
        
        for i in range(1, messNumberBeams + 1, 1):
            file.write("Beam number: " + str(messBeamNum) + "\n")

            if blockConfig == True:
                file.write("Angle: " + str(messBeamAngle) + " °\n")

            file.write("Distance: " + str(messBeamMM) + " mm\n" +
            "RSSI value: " + str(messBeamRSSI) + "\n")

            if messBeamStatus[7] == "1":
                file.write("Status: Beam is valid\n")
            if messBeamStatus[6] == "1":
                file.write("Status: No reflected light pulse received (do not accept this measurement value.)\n")
            if messBeamStatus[5] == "1":
                file.write("Status: Beam is dazzled\n")
            if messBeamStatus[4] == "1":
                file.write("Status: Contamination error on beam\n")
            if messBeamStatus[3] == "1":
                file.write("Status: Contamination warning on beam\n")
            file.write("\n")        
            
            # Incremented values and indexes (values incremented from initial values, and so on with each beam)
            if i < messNumberBeams:
                messBeamNum = messBeamNum + 1
                messBeamMMByte2from = messBeamMMByte2from + 8
                messBeamMMByte2to = messBeamMMByte2to + 8
                messBeamMMByte1from = messBeamMMByte1from + 8
                messBeamMMByte1to = messBeamMMByte1to + 8
                messBeamRSSIByte1From = messBeamRSSIByte1From + 8
                messBeamRSSIByte1To = messBeamRSSIByte1To + 8
                messBeamStatusByte1from = messBeamStatusByte1from + 8
                messBeamStatusByte1to = messBeamStatusByte1to + 8
                messBeamMM = int(blockMessData[messBeamMMByte2from:messBeamMMByte2to] + blockMessData[messBeamMMByte1from:messBeamMMByte1to], 16)
                messBeamRSSI = int(blockMessData[messBeamRSSIByte1From:messBeamRSSIByte1To], 16)
                messBeamStatus = "{0:08b}".format(int(blockMessData[messBeamStatusByte1from:messBeamStatusByte1to], 16))
                
                if blockConfig == True:
                    messBeamAngle = messBeamAngle + messAngleRes

    # Data output: Block Field interruption
    if blockField == True:
        file.write("\n*** Data output: Block field interruption ***\n")
        intrusion0 = 0
        intrusion2 = 2
        intrusion4 = 4
        intrusion6 = 6
        intrusion8 = 8
        intrusionDataStart = 8
        intrusionLength = int(blockFieldData[intrusion6:intrusion8] + blockFieldData[intrusion4:intrusion6] + blockFieldData[intrusion2:intrusion4]
        + blockFieldData[intrusion0:intrusion2], 16) * 2
        intrusionData = blockFieldData[intrusionDataStart:intrusionDataStart + intrusionLength]

        for k in range(24):
            if intrusionLength != 0:
                intrusionState = False
                file.write("\nCut-off path: " + str(k + 1) + "\n" )
                intrusionBeamNum = 1
                for i in range(0, intrusionLength, 2):
                    intrusionByte = "{0:08b}".format(int(intrusionData[i:i+2], 16))
                    for j in range(0, 8, 1):
                        if intrusionByte[j] == "1":
                            intrusionState = True
                            file.write("Beam " + str(intrusionBeamNum) + " is infringed\n")
                        intrusionBeamNum = intrusionBeamNum + 1
                if intrusionState == False:
                    file.write("No intrusions in this cut-off path.\n")
                intrusion0 = intrusion0 + intrusionLength + 8
                intrusion2 = intrusion2 + intrusionLength + 8
                intrusion4 = intrusion4 + intrusionLength + 8
                intrusion6 = intrusion6 + intrusionLength + 8
                intrusion8 = intrusion8 + intrusionLength + 8
                intrusionLength = int(blockFieldData[intrusion6:intrusion8] + blockFieldData[intrusion4:intrusion6] + blockFieldData[intrusion2:intrusion4]
                + blockFieldData[intrusion0:intrusion2], 16) * 2
                intrusionDataStart =+ intrusionDataStart + intrusionLength + 8
                intrusionData = blockFieldData[intrusionDataStart:intrusionDataStart + intrusionLength]
            else:
                pass
        file.write("\n")  

    # Data output: Block Application data inputs / outputs
    if blockApp == True:
        file.write("\n*** Data output: Block Application data inputs / outputs ***\n\nINPUTS\n\n")
        file.write("Static control inputs (input/flag):\n")
        appControlInput0 = "{0:08b}".format(int(blockAppData[0:2], 16)).replace(' ','0')
        appControlInputFlag0 = "{0:08b}".format(int(blockAppData[8:10], 16)).replace(' ','0')
        if appControlInput0 != "00000000" and appControlInputFlag0 !="00000000":
            file.write("A1: " + str(appControlInput0[7]) + " / " + str(appControlInputFlag0[7]) + "\n")
            file.write("A2: " + str(appControlInput0[6]) + " / " + str(appControlInputFlag0[6]) + "\n")
            file.write("B1: " + str(appControlInput0[5]) + " / " + str(appControlInputFlag0[5]) + "\n")
            file.write("B2: " + str(appControlInput0[4]) + " / " + str(appControlInputFlag0[4]) + "\n")
            file.write("C1: " + str(appControlInput0[3]) + " / " + str(appControlInputFlag0[3]) + "\n")
            file.write("C2: " + str(appControlInput0[2]) + " / " + str(appControlInputFlag0[2]) + "\n")
            file.write("D1: " + str(appControlInput0[1]) + " / " + str(appControlInputFlag0[1]) + "\n")
            file.write("D2: " + str(appControlInput0[0]) + " / " + str(appControlInputFlag0[0]) + "\n")
        else:
            file.write("Inputs A, B, C and D: Not used.\n")

        appControlInputs1 = "{0:08b}".format(int(blockAppData[2:4], 16)).replace(' ','0')
        appControlInputFlag1 = "{0:08b}".format(int(blockAppData[10:12], 16)).replace(' ','0')
        if appControlInputs1 != "00000000" and appControlInputFlag1 !="00000000":
            file.write("E1: " + str(appControlInputs1[7]) + " / " + str(appControlInputFlag1[7]) + "\n")
            file.write("E2: " + str(appControlInputs1[6]) + " / " + str(appControlInputFlag1[6]) + "\n")
            file.write("F1: " + str(appControlInputs1[5]) + " / " + str(appControlInputFlag1[5]) + "\n")
            file.write("F2: " + str(appControlInputs1[4]) + " / " + str(appControlInputFlag1[4]) + "\n")
            file.write("G1: " + str(appControlInputs1[3]) + " / " + str(appControlInputFlag1[3]) + "\n")
            file.write("G2: " + str(appControlInputs1[2]) + " / " + str(appControlInputFlag1[2]) + "\n")
            file.write("H1: " + str(appControlInputs1[1]) + " / " + str(appControlInputFlag1[1]) + "\n")
            file.write("H2: " + str(appControlInputs1[0]) + " / " + str(appControlInputFlag1[0]) + "\n")
        else:
            file.write("Inputs E, F, G and H: Not used.\n")

        file.write("\nMonitoring case number:\n")
        j = 1
        k = True
        for i in range(24, 104, 4):
            appCaseTableNo = int(blockAppData[i+2:i+4] + blockAppData[i:i+2], 16)
            if appCaseTableNo > 0:
                file.write("Monitoring case table " + str(j) + " has case number: " + str(appCaseTableNo) + "\n")
                k = False
            j = j + 1
            # Stops at 4. Upto 4 monitoring cases are currently supported. 
            if j == 4:
                break
        if k == True:
            file.write("No monitoring case number given or static control inputs used.\n\n")

        file.write("Monitoring case number (flags):\n")
        appCaseTableFlag = "{0:32b}".format(int(blockAppData[110:112] + blockAppData[108:110] + blockAppData[106:108] + blockAppData[104:106], 16)).replace(' ','0')
        j = 1
        k = True
        for i in range (31, 0, -1):
            if appCaseTableFlag[i] == "1":
                file.write("Monitoring case table " + str(j) + " is valid.\n")
                k = False
            j = j + 1
            # Stops at 4. Upto 4 monitoring cases are currently supported.
            if j == 4:
                break
        if k == True:
            file.write("No monitoring case number given or static control inputs used.\n")

        appSpeed = "{0:08b}".format(int(blockAppData[120:122], 16))
        file.write("\nDynamic control inputs (Speed 1)\n")
        file.write(str(int(blockAppData[114:116] + blockAppData[112:114], 16)) + " mm/s ")
        if appSpeed[7] == "1":
            file.write("(valid)\n")
        else:
            file.write("(invalid / unused)\n")
        file.write("\nDynamic control inputs (Speed 2)\n")
        file.write(str(int(blockAppData[118:120] + blockAppData[116:118], 16)) + " mm/s ")
        if appSpeed[6] == "1":
            file.write("(valid)\n")
        else:
            file.write("(invalid / unused)\n") 

        appStandby = int(blockAppData[148:150], 16)
        if appStandby == 2:
            file.write("\nStandby mode active.\n")
        else:
            file.write("\nStandby mode inactive.\n")

        file.write("\nOUTPUTS\n\n")

        file.write("Active Cut-off paths (non-safe):\n")
        appCutOff = "{0:32b}".format(int(blockAppData[286:288] + blockAppData[284:286] + blockAppData[282:284] + blockAppData[280:282], 16)).replace(' ','0')
        j = 1
        k = True
        for i in range(31, 0, -1):
            if appCutOff[i] == "1":
                file.write("Cut-off path " + str(j) + " active\n")
                k = False
            j = j + 1
        if k == True:
            file.write("There are no active cut-off paths (non-safe).\n")

        file.write("\nActive Cut-off paths (safe):\n")
        appCutOffSafe = "{0:32b}".format(int(blockAppData[294:296] + blockAppData[292:294] + blockAppData[290:292] + blockAppData[288:290], 16)).replace(' ','0')
        j = 1
        k = True
        for i in range(31, 0, -1):
            if appCutOffSafe[i] == "1":
                file.write("Cut-off path " + str(j) + " active\n")
                k = False
            j = j + 1
        if k == True:
            file.write("There are no active cut-off paths (safe).\n")

        file.write("\nValid Cut-off paths:\n")
        appCutOffValid = "{0:32b}".format(int(blockAppData[302:304] + blockAppData[300:302] + blockAppData[298:300] + blockAppData[296:298], 16)).replace(' ','0')
        j = 1
        k = True
        for i in range(31, 0, -1):
            if appCutOffValid[i] == "1":
                file.write("Cut-off path " + str(j) + " valid\n")
                k = False
            j = j + 1
            # Stops after 8 (maximum number of cut-off paths)
            if j == 8:
                break
        if k == True:
            file.write("There are no valid cut-off paths.\n")

        file.write("\nMonitoring case number:\n")
        j = 1
        for i in range(304, 408, 4):
            appCaseTableNo = int(blockAppData[i+2:i+4] + blockAppData[i:i+2], 16)
            if appCaseTableNo > 0:
                file.write("Monitoring case table " + str(j) + " has case number: " + str(appCaseTableNo) + "\n")
            j = j + 1
            # Stops at 4. Upto 4 monitoring cases are currently supported. 
            if j == 4:
                break

        file.write("\nMonitoring case number (flags):\n")
        appCaseTableFlag = "{0:32b}".format(int(blockAppData[390:392] + blockAppData[388:390] + blockAppData[386:388] + blockAppData[384:386], 16)).replace(' ','0')
        j = 1
        for i in range (31, 0, -1):
            if appCaseTableFlag[i] == "1":
                file.write("Monitoring case table " + str(j) + " valid.\n")
            j = j + 1
            # Stops at 4. Upto 4 monitoring cases are currently supported.
            if j == 4:
                break

        appStandby2 = int(blockAppData[392:394], 16)
        if appStandby2 == 2:
            file.write("\nStandby mode active.\n")
        else:
            file.write("\nStandby mode inactive.\n")

        file.write("\nMessages:\n")
        appMessages = "{0:08b}".format(int(blockAppData[394:396], 16)).replace(' ','0')
        if appMessages[7] == "1":
            file.write("Contamination warning active.\n")
        if appMessages[6] == "1":
            file.write("Contamination error active.\n")
        if appMessages[5] == "1":
            file.write("Manipulation detected.\n")
        if appMessages[4] == "1":
            file.write("Device is dazzled.\n")
        if appMessages[3] == "1":
            file.write("Reference contour monitoring triggered.\n")
        if appMessages[2] == "1":
            file.write("Critical error detected.\n")
        appFlags = "{0:08b}".format(int(blockAppData[512:514], 16)).replace(' ','0')
        if appFlags[7] == "1":
            file.write("Sleep mode active.\n")
        if appFlags[6] == "1":
            file.write("Messages (host) output is valid.\n")
        if appMessages == "00000000" and appFlags == "00000000":
            file.write("There are no messages.\n")

    # Data output: Block Local inputs and outputs
    if blockLocal == True:
        file.write("\n\n*** Data output: Block Local inputs / outputs ***\n\nINPUTS\n\n")
        localInputs = "{0:32b}".format(int(blockLocalData[6:8] + blockLocalData[4:6] + blockLocalData[2:4] + blockLocalData[0:2], 16)).replace(' ', '0')
        localInputsFlags = "{0:32b}".format(int(blockLocalData[14:16] + blockLocalData[12:14] + blockLocalData[10:12] + blockLocalData[8:10], 16)).replace(' ','0')
        file.write("Logical status of the inputs / flags (if connection is configured):\n")
        file.write("MICS3 (XG1, Pin 9 / UNI-I 05) or NANS3 Pro/Core (Pin 5 / UNI I/O 1): " + str(localInputs[27]) + " / " + str(localInputsFlags[27]) + "\n")
        file.write("MICS3 (XG1, Pin 10 / UNI-I 06) or NANS3 Pro/Core (Pin 6 / UNI I/O 2): " + str(localInputs[26]) + " / " + str(localInputsFlags[26]) + "\n")
        file.write("MICS3 (XG1, Pin 11 / UNI-I 07) or NANS3 Pro/Core (Pin 7 / UNI I/O 3): " + str(localInputs[25]) + " / " + str(localInputsFlags[25]) + "\n")
        file.write("MICS3 (XG1, Pin 12 / UNI-I 08) or NANS3 Pro (Pin 8 / UNI I/O 4): " + str(localInputs[24]) + " / " + str(localInputsFlags[24]) + "\n")
        file.write("MICS3 (XG1, Pin 13 / UNI-I 09) or NANS3 Pro (Pin 9 / UNI-I 1): " + str(localInputs[23]) + " / " + str(localInputsFlags[23]) + "\n")
        file.write("MICS3 (XG1, Pin 14 / UNI-I 10) or NANS3 Pro (Pin 10 / UNI-I 2): " + str(localInputs[22]) + " / " + str(localInputsFlags[22]) + "\n")
        file.write("MICS3 (XG1, Pin 5 / UNI-I 01) or NANS3 Pro (Pin 11 / UNI-I 3): " + str(localInputs[21]) + " / " + str(localInputsFlags[21]) + "\n")
        file.write("MICS3 (XG1, Pin 6 / UNI-I 02) or NANS3 Pro (Pin 12 / UNI-I 4): " + str(localInputs[20]) + " / " + str(localInputsFlags[20]) + "\n")
        file.write("MICS3 (XG1, Pin 7 / UNI-I 03) or NANS3 Pro (Pin 13 / UNI-I 5): " + str(localInputs[19]) + " / " + str(localInputsFlags[19]) + "\n")
        file.write("MICS3 (XG1, Pin 8 / UNI-I 04) or NANS3 Pro (Pin 14 / UNI-I 6): " + str(localInputs[18]) + " / " + str(localInputsFlags[18]) + "\n")
        file.write("MICS3 (XG4, Pin 9 / UNI-I 11) or NANS3 Pro (Pin 15 / UNI-I 7): " + str(localInputs[17]) + " / " + str(localInputsFlags[17]) + "\n")
        file.write("MICS3 (XG4, Pin 10 / UNI-I 12) or NANS3 Pro (Pin 16 / UNI-I 8): " + str(localInputs[16]) + " / " + str(localInputsFlags[16]) + "\n")
        file.write("MICS3 (XG4, Pin 11 / UNI-I 13): " + str(localInputs[16]) + " / " + str(localInputsFlags[15]) + "\n")
        file.write("MICS3 (XG4, Pin 12 / UNI-I 14): " + str(localInputs[14]) + " / " + str(localInputsFlags[14]) + "\n")
        file.write("MICS3 (XG4, Pin 13 / UNI-I 15): " + str(localInputs[13]) + " / " + str(localInputsFlags[13]) + "\n")
        file.write("MICS3 (XG4, Pin 14 / UNI-I 16): " + str(localInputs[12]) + " / " + str(localInputsFlags[12]) + "\n")
        file.write("\nDynamic control inputs:\n")
        localSpeedFlags = "{0:16b}".format(int(blockLocalData[24:28] + blockLocalData[22:24], 16)).replace(' ','0')
        file.write("Speed 1: " + str(int(blockLocalData[18:20] + blockLocalData[16:18], 16)) + " mm/s ")
        if localSpeedFlags[15] == "1":
            file.write("(valid)\n")
        else:
            file.write("(invalid / not used)\n")
        file.write("Speed 2: " + str(int(blockLocalData[22:24] + blockLocalData[20:22], 16)) + " mm/s ")
        if localSpeedFlags[14] == "1":
            file.write("(valid)\n")
        else:
            file.write("(invalid / not used)\n")

        file.write("\nOUTPUTS\n\n")
        file.write("OSSD Status:\n")
        localOSSD = "{0:08b}".format(int(blockLocalData[56:58], 16)).replace(' ','0')
        file.write("OSSD 1.A: " + str(localOSSD[7]) + "\n")
        file.write("OSSD 1.B: " + str(localOSSD[6]) + "\n")
        file.write("OSSD 2.A: " + str(localOSSD[5]) + "\n")
        file.write("OSSD 2.B: " + str(localOSSD[4]) + "\n")
        file.write("OSSD 3.A: " + str(localOSSD[3]) + "\n")
        file.write("OSSD 3.B: " + str(localOSSD[2]) + "\n")
        file.write("OSSD 4.A: " + str(localOSSD[1]) + "\n")
        file.write("OSSD 4.B: " + str(localOSSD[0]) + "\n")
        
        file.write("\nNon-safe outputs:\n")
        file.write("nanoScan3 (if applicable):\n")
        localByteArray = blockLocalData[64:]
        localByte4 = (int(localByteArray[8:10]))
        if localByte4 == 0:
            file.write("Universal I/O 1 (Pin 5): Signal level of the output is LOW (0 V).\n")
        elif localByte4 == 1:
            file.write("Universal I/O 1 (Pin 5): Output flashes at 1 Hz.\n")
        elif localByte4 == 2:
            file.write("Universal I/O 1 (Pin 5): Output flashes at 4 Hz.\n")
        elif localByte4 == 3:
            file.write("Universal I/O 1 (Pin 5): Signal level of the output is HIGH (24 V).\n")
        elif localByte4 == 255:
            file.write("Universal I/O 1 (Pin 5): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte5 = (int(localByteArray[10:12]))
        if localByte5 == 0:
            file.write("Universal I/O 2 (Pin 6): Signal level of the output is LOW (0 V).\n")
        elif localByte5 == 1:
            file.write("Universal I/O 2 (Pin 6): Output flashes at 1 Hz.\n")
        elif localByte5 == 2:
            file.write("Universal I/O 2 (Pin 6): Output flashes at 4 Hz.\n")
        elif localByte5 == 3:
            file.write("Universal I/O 2 (Pin 6): Signal level of the output is HIGH (24 V).\n")
        elif localByte5 == 255:
            file.write("Universal I/O 2 (Pin 6): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte6 = (int(localByteArray[12:14]))
        if localByte6 == 0:
            file.write("Universal I/O 3 (Pin 7): Signal level of the output is LOW (0 V).\n")
        elif localByte6 == 1:
            file.write("Universal I/O 3 (Pin 7): Output flashes at 1 Hz.\n")
        elif localByte6 == 2:
            file.write("Universal I/O 3 (Pin 7): Output flashes at 4 Hz.\n")
        elif localByte6 == 3:
            file.write("Universal I/O 3 (Pin 7): Signal level of the output is HIGH (24 V).\n")
        elif localByte6 == 255:
            file.write("Universal I/O 3 (Pin 7): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte7 = (int(localByteArray[14:16]))
        if localByte7 == 0:
            file.write("Universal I/O 4 (Pin 8): Signal level of the output is LOW (0 V).\n")
        elif localByte7 == 1:
            file.write("Universal I/O 4 (Pin 8): Output flashes at 1 Hz.\n")
        elif localByte7 == 2:
            file.write("Universal I/O 4 (Pin 8): Output flashes at 4 Hz.\n")
        elif localByte7 == 3:
            file.write("Universal I/O 4 (Pin 8): Signal level of the output is HIGH (24 V).\n")
        elif localByte7 == 255:
            file.write("Universal I/O 4 (Pin 8): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        file.write("\nmicroScan3 Pro I/O (if applicable):\n")
        localByte24 = (int(localByteArray[48:50]))
        if localByte24 == 0:
            file.write("Universal output 1 (XG1, Pin 15): Signal level of the output is LOW (0 V).\n")
        elif localByte24 == 1:
            file.write("Universal output 1 (XG1, Pin 15): Output flashes at 1 Hz.\n")
        elif localByte24 == 2:
            file.write("Universal output 1 (XG1, Pin 15): Output flashes at 4 Hz.\n")
        elif localByte24 == 3:
            file.write("Universal output 1 (XG1, Pin 15): Signal level of the output is HIGH (24 V).\n")
        elif localByte24 == 255:
            file.write("Universal output 1 (XG1, Pin 15): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte25 = (int(localByteArray[50:52]))
        if localByte25 == 0:
            file.write("Universal output 2 (XG1, Pin 16): Signal level of the output is LOW (0 V).\n")
        elif localByte25 == 1:
            file.write("Universal output 2 (XG1, Pin 16): Output flashes at 1 Hz.\n")
        elif localByte25 == 2:
            file.write("Universal output 2 (XG1, Pin 16): Output flashes at 4 Hz.\n")
        elif localByte25 == 3:
            file.write("Universal output 2 (XG1, Pin 16): Signal level of the output is HIGH (24 V).\n")
        elif localByte25 == 255:
            file.write("Universal output 2 (XG1, Pin 16): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte26 = (int(localByteArray[52:54]))
        if localByte26 == 0:
            file.write("Universal output 3 (XG4, Pin 15): Signal level of the output is LOW (0 V).\n")
        elif localByte26 == 1:
            file.write("Universal output 3 (XG4, Pin 15): Output flashes at 1 Hz.\n")
        elif localByte26 == 2:
            file.write("Universal output 3 (XG4, Pin 15): Output flashes at 4 Hz.\n")
        elif localByte26 == 3:
            file.write("Universal output 3 (XG4, Pin 15): Signal level of the output is HIGH (24 V).\n")
        elif localByte26 == 255:
            file.write("Universal output 3 (XG4, Pin 15): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

        localByte27 = (int(localByteArray[54:56]))
        if localByte27 == 0:
            file.write("Universal output 4 (XG4, Pin 16): Signal level of the output is LOW (0 V).\n")
        elif localByte27 == 1:
            file.write("Universal output 4 (XG4, Pin 16): Output flashes at 1 Hz.\n")
        elif localByte27 == 2:
            file.write("Universal output 4 (XG4, Pin 16): Output flashes at 4 Hz.\n")
        elif localByte27 == 3:
            file.write("Universal output 4 (XG4, Pin 16): Signal level of the output is HIGH (24 V).\n")
        elif localByte27 == 255:
            file.write("Universal output 4 (XG4, Pin 16): Output not in use.\n")
        else:
            file.write("Unexpected value given.\n")

    # Close and save file
    file.close()

    # End program
    print("Data output successfully saved to file.")
    input("Press 'Enter' to close the program.")
    exit()

# Error handling
except ValueError:
    print("An unexpected error occurrred. The data sample received or provided was not correct.")
    print("This may occur if the data sample is missing a frame (e.g., 5 frames expected, but only 4 received).")
    try:
        file.write("\nAn error occurred, and the file may contain invalid data or not be complete.")
        file.close() 
    except Exception as e:
        pass
    input("Press 'Enter' to close the program.")
    exit()

except Exception as e:
    print("An unexpected error occurrred. The following error messages was detected:")
    print(e)
    try:
        file.write("\nAn error occurred, and the file may contain invalid data or not be complete.")
        file.close() 
    except Exception as e:
        pass
    input("Press 'Enter' to close the program.")
    exit()
