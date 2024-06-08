import socket
import struct

DOMAIN = "mazarboard.com"
SERVER_IP = "127.0.0.1"
PORT = 53
BUFFER_SIZE = 512

def build_query(filename):
    transaction_id = b'\xaa\xbb'  #random transaction ID
    flags = b'\x01\x00'  #query standard
    questions = b'\x00\x01'
    answer_rrs = b'\x00\x00'
    authority_rrs = b'\x00\x00'
    additional_rrs = b'\x00\x00'

    dns_header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs

    domain_parts = filename.split('.')
    qname = b''.join(struct.pack('B', len(part)) + part.encode('utf-8') for part in domain_parts)
    qname += b'\x00'

    query_type = b'\x00\x10'  #TXT
    query_class = b'\x00\x01'  #IN

    dns_query = dns_header + qname + query_type + query_class
    return dns_query

def send_request(filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query = build_query(filename)
    sock.sendto(query, (SERVER_IP, PORT))
    response_data, _ = sock.recvfrom(BUFFER_SIZE)
    sock.close()
    return response_data

def parse_response(data):
    dns_header = data[:12]
    question_count = struct.unpack('!H', dns_header[4:6])[0]
    answer_count = struct.unpack('!H', dns_header[6:8])[0]

    query = data[12:]
    offset = 0

    #dam skip la  query section
    for _ in range(question_count):
        while query[offset] != 0:
            offset += 1
        offset += 5

    #parsam sectiunea de rasp
    answers = []
    for _ in range(answer_count):
        offset += 2
        answer_type = struct.unpack('!H', query[offset:offset+2])[0]
        offset += 8
        rdlength = struct.unpack('!H', query[offset:offset+2])[0]
        offset += 2

        if answer_type == 16:  #TXT record
            txt_length = query[offset]
            offset += 1
            txt_data = query[offset:offset+txt_length].decode('utf-8')
            answers.append(txt_data)
            offset += txt_length
        else:
            offset += rdlength

    return answers

if __name__ == "__main__":
    filename = "testfile.txt.mazarboard.com"
    print(f"Requesting file: {filename}")
    response = send_request(filename)
    answers = parse_response(response)

    if answers:
        print("Response received")
        file_content = bytes.fromhex(answers[0])
        with open("received_testfile.txt", "wb") as f:
            f.write(file_content)
        print("File received successfully!")
    else:
        print("Failed to retrieve the file.")
