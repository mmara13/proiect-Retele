import socket
import requests
import struct
import traceback
import argparse
from traceroute_map_plotter import plot_route


#socket de UDP
udp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

#socket RAW de citire a raspunsurilor ICMP
icmp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

#setam timeout pt caz in care socket ICMP nu primeste nmc in buffer la apelul recvform

#functie pt a verifica dc un IP e privat
def is_private_ip(ip):
    private_ip_ranges = [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255'),
            ('127.0.0.0.', '127.255.255.255')
        ]

    ip_addr = struct.unpack('>I', socket.inet_aton(ip))[0]
    for start, end in private_ip_ranges:
        if struct.unpack('>I', socket.inet_aton(start))[0] <= ip_addr <= struct.unpack('>I', socket.inet_aton(end))[0]:
            return True
        return False

def get_ip_info(ip):
    if is_private_ip(ip):
        return {'city':'Private', 'region':'Private', 'country': 'Private'}

    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        #print(f"IP Info Response for {ip}: {data}") #debug
        return data
    except Exception as e:
        print(f"Failed to get IP info for {ip}: {e}")
        return {'city': 'Unknown', 'region': 'Unknown', 'country': 'Unknown'}

def traceroute(destination, port =33434, max_hops = 30, timeout=2):
    destination_ip = socket.gethostbyname(destination)
    route_locations = []

    #setam timeut pt socket icmp ca sa nu stea prea mult
    icmp_recv_socket.settimeout(timeout)

    for ttl in range(1, max_hops + 1):
        udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        udp_send_sock.sendto(b'salut', (destination_ip, port))

        try:
            data, addr = icmp_recv_socket.recvfrom(65535)
            router_ip = addr[0]
            ip_info=get_ip_info(router_ip)
            location_str = ip_info.get('loc', '') #sirul de coordonate pentru mapa
            if location_str:
                lat_str, lon_str = location_str.split(',')#separam sirul in longitudine si latitudine
                location = {
                        'latitude': float(lat_str), #convertim in numar
                        'longitude': float(lon_str),
                        'city': ip_info.get('city', 'Unknown'),
                        'region' : ip_info.get('region', 'Unknown'),
                        'country' : ip_info.get('country', 'Unknown')
                        }
                route_locations.append(location)
                        
                print(f"{ttl}\t{router_ip}\t{location['city']}, {location['region']}, {location['country']}")

                if router_ip == destination_ip:
                    print("Destination reached.")
                    break
        except socket.timeout:
            print(f"{ttl}\t*")

    #print(route_locations)
    plot_route(route_locations)

    


def main():
    parser = argparse.ArgumentParser(description="Traceroute aplicatie completa.")
    parser.add_argument("destination", help="Destination host or IP address.")
    parser.add_argument("-m", "--max-hops", type=int, default=30, help="Maximum number of hops (default:30).")
    parser.add_argument("-t", "--timeout", type=int, default=2, help="Timeout for each packet in sec (default:2).")
    args = parser.parse_args()

    print(f"Traceroute to {args.destination} (max hops: {args.max_hops}, timeout: {args.timeout} seconds):")
    traceroute(args.destination, port=33434, max_hops=args.max_hops, timeout=args.timeout)

if __name__ == "__main__":
    main()

