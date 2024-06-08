import socket
from scapy.all import DNS, DNSQR, DNSRR

#configuram socket-ul UDP
simple_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
simple_udp.bind(('0.0.0.0', 8053)) 

#definim domeniul si subdomeniul pentru care serverul DNS va raspunde
DOMAIN = "www.mazarboard.com."
SUBDOMAIN = "subdomain.mazarboard.com."

while True:
    #primim cerere DNS
    request, adresa_sursa = simple_udp.recvfrom(65535)
    
    #convertim payload-ul in pachet scapy
    packet = DNS(request)
    dns = packet.getlayer(DNS)
    
    if dns is not None and dns.opcode == 0:  #DNS QUERY
        print("Received DNS query:")
        print(packet.summary())
        
        #verificam pt ce domeniu este cererea
        qname = dns.qd.qname.decode('utf-8')
        if qname == DOMAIN or qname == SUBDOMAIN:
            #construim raspunsul DNS
            if qname == DOMAIN:
                ip_address = '127.0.0.1'  #IP pentru www.mazarboard.com
            elif qname == SUBDOMAIN:
                ip_address = '127.0.0.1'  #IP pentru subdomain.mazarboard.com

            dns_answer = DNSRR(
                rrname=dns.qd.qname,  #pt intrebare
                ttl=330,  #durata de viata a inregistrarii DNS
                type="A",
                rclass="IN",
                rdata=ip_address  #IP-ul asociat cu domeniul/subdomeniul
            )

            dns_response = DNS(
                id=packet[DNS].id,  #raspunsul DNS trebuie sa aiba acelasi ID ca cererea
                qr=1,  #1 pentru raspuns, 0 pentru cerere
                aa=1,  #Authoritative Answer
                rcode=0,  #0 -> nicio eroare
                qd=packet.qd,  #cererea originală
                an=dns_answer  #obiectul de raspuns
            )

            print('Sending DNS response:')
            print(dns_response.summary())
            
            #trimitem raspunsul
            simple_udp.sendto(bytes(dns_response), adresa_sursa)

simple_udp.close()

