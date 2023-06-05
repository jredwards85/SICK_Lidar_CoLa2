# CoLa2 Session Handler - V1.0.3 
# Written by James Edwards

import socket
import time
import re

# Initial variables
ipAddress = input("IP Address: ")
status = None

# Option to fix IP address, send another command or exit program
def repeat(status, ipAddress):
    repeat = input("Send another command? (Y/n): ").lower()
    if repeat == "y" or repeat == "":
        if status == "IP":
            ipAddress = input("IP Address: ")
            session_handler(ipAddress)
        else:
            session_handler(ipAddress)
    else:
        exit()

# Session and request handling program
def session_handler(ipAddress):
    portNumber = int(2122)
    requestHex = input("Enter your request as hex: ").lower()
    requestHex = requestHex.replace(" ", "")
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
                print("Oops, an unknown error occured: Please ensure you entered all values correctly.")
                repeat("IP", None)

        # Constructs the command request with correct session ID        
        response  = data.hex()
        if response == "" or len(response) < 28:
            print("Error: The target provided no response or an incorrect response to creating a session. Please try again.")
            repeat("IP", None)

        sessionID = response[20:28]
        requestHex2 = requestHex.replace(" ", "")
        requestPart1 = requestHex2[:20]
        requestPart2 = requestHex2[28:]
        request = requestPart1 + sessionID + requestPart2
        data = bytearray.fromhex(request)
        tcp_socket.sendall(data)

        # While reading request response, allows for fragmented data responses (max. duration 250 ms)
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
                print("Oops, an unknown error occured: Please ensure you entered all values correctly.")
                repeat("IP", None)
        
        if data.hex() == "":
            print("Error: The target provided no response to your request.")
            print("Troubleshooting: This can happen if the request provided was not correct.")
            tcp_socket.close()
            repeat(None, ipAddress)

        # Error handling for CoLa2 error codes. Outputs the error code for the user 
        colaError = data.hex()
        if colaError[32:36] == "4641":
            errorCode = colaError[37:40][::-1]
            print(f"Error code: {errorCode}. Please refer to the data output error codes.")
            tcp_socket.close()
            repeat(None, ipAddress)

        # Prints the response from port 2122 and closes the TCP session
        data_hex = data.hex()
        data_hex = (' ').join(re.findall('.{1,2}',data_hex))
        print("Reply from target:")
        print("Reply in hex:   ", data_hex)
        print("Reply in ascii: ", data)
        tcp_socket.close()
        repeat(None, ipAddress)
    
    # Error handling for the TCP session function
    except TimeoutError:
        print("Timeout error: The IP Address is probably incorrect.")
        repeat("IP", None)

    except ValueError:
        print("Value error: The entered request isn't valid hex.")
        print("Troubleshooting: This can happen if an uneven number of characters is entered.")
        print("Troubleshooting: This can happen if an invalid character is entered (0 - 9, A - F only!).")
        repeat(None, ipAddress)

    except Exception as e:
        print("Oops, an unknown error occured: Please ensure you entered all values correctly.")
        repeat("IP", None)

# Runs the function (as above)
session_handler(ipAddress)
