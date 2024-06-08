import socket
import struct

DOMAIN = "mazarboard.com"
IP = "127.0.0.1"
PORT = 53
BUFFER_SIZE = 512

def create_response(data):
    transaction_id = data[:2]
    flags = b'\x81\x80'  #standard raspuns de la query - no error
    questions = data[4:6]
    answer_rrs = b'\x00\x01'
    authority_rrs = b'\x00\x00'
    additional_rrs = b'\x00\x00'
    dns_header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs

    query = data[12:]  #skip header

    #extract requested domain name si query type
    domain_parts = []
    offset = 0
    while True:
        length = query[offset]
        if length == 0:
            offset += 1
            break
        domain_parts.append(query[offset+1:offset+1+length].decode('utf-8'))
        offset += 1 + length

    requested_domain = '.'.join(domain_parts)
    query_type = query[offset:offset+2]
    query_class = query[offset+2:offset+4]
    query_end = query[offset+4:]

    print(f"Requested domain: {requested_domain}")

    if requested_domain.endswith(DOMAIN):
        filename = requested_domain.split('.')[0]
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            txt_data = content.hex()
            print(f"File '{filename}' found, content length: {len(txt_data)}")
        except FileNotFoundError:
            txt_data = "File not found"
            print(f"File '{filename}' not found")

        answer = b'\xc0\x0c'  #pointer la domain name in query
        answer += query_type + query_class
        answer += struct.pack('!I', 300)  #TTL
        txt_length = len(txt_data)
        answer += struct.pack('!H', txt_length + 1)  #TXT length
        answer += struct.pack('B', txt_length)  #TXT length 
        answer += txt_data.encode('utf-8')
    else:
        answer = b''

    dns_response = dns_header + data[12:12+offset+4] + answer
    return dns_response

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print(f"DNS server started on {IP}:{PORT}")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"Received request from {addr}")
        response = create_response(data)
        sock.sendto(response, addr)

if __name__ == "__main__":
    start_server()

