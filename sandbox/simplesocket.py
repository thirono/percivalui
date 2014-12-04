'''
Created on 2 Dec 2014

@author: up45
'''
import socket

#board_ip_address = "192.168.0.3"
board_ip_address = "percival2.diamond.ac.uk"
board_ip_port = 10001

def bytes_to_str(byte_list):
    return "".join([chr(b) for b in byte_list])

def main():
    numbers = [0x02, 0x8C, 0x00, 0x00, 0x00, 0x00,
               0x02, 0x8D, 0x00, 0x00, 0x00, 0x00,
               0x02, 0x8E, 0x00, 0x00, 0x00, 0x00,
               0x02, 0x8F, 0x00, 0x00, 0x00, 0x00  ]
    #numbers = [0x02, 0x8D, 0x00, 0x00, 0x00, 0x00 ]
    #numbers = [0x03, 0xa4, 0x00, 0x00, 0x00, 0x00 ]
    #numbers = [0x03, 0xb3, 0x00, 0x00, 0x00, 0x00]
    #numbers = [0x03, 0xbd, 0x00, 0x00, 0x00, 0x00]
    
    msg = bytes_to_str(numbers)
    
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.settimeout(1.0)
    client_sock.connect((board_ip_address, board_ip_port))
    print "Sending message: ", numbers
    print " as string:      ", [msg]
    client_sock.send(msg)
    
    print "Waiting for response..."
    response = client_sock.recv(1024)
    
    print "Got response (%dbytes): "%len(response), [response] 
    print " which means: ", [ord(r) for r in response]
    print "  and in hex:", " ".join([hex(ord(r))for r in response])

    client_sock.close()
    
if __name__ == '__main__':
    main()
    