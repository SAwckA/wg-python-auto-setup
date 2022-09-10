from pydoc import cli
from random import choice
from string import ascii_uppercase
from xmlrpc import client

from python_setup import run, file_exists, key_reader, write_file

def format_last_ip(ip:str) -> str:
    ip = ip.split()
    return f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}/32"

def increment_ip(ip:str) -> str:
    last_num = int(ip.split()[::-1][0]) + 1
    second_num = int(ip.split()[::-1][1])
    if last_num >= 255:
        last_num = 1
        second_num += 1 

    new_ip = f"10 0 {str(second_num)} {str(last_num)}"
    write_file(new_ip, './last_ip')
    return new_ip

if not file_exists('./last_ip'):
    run("touch ./last_ip")
    write_file('10 0 0 2', './last_ip')
    last_ip = '10 0 0 2'

else:
    
    last_ip = key_reader('./last_ip')
    last_ip = increment_ip(last_ip)
    print(format_last_ip(last_ip))


def gen_name() -> str:
    return ''.join(choice(ascii_uppercase) for i in range(12))

client_name = gen_name()

run(f"mkdir {client_name}")

run(f"wg genkey | tee ./{client_name}/{client_name}_privatekey | wg pubkey | tee ./{client_name}/{client_name}_publickey")

client_private = key_reader(f'./{client_name}/{client_name}_privatekey')
client_pub = key_reader(f'./{client_name}/{client_name}_publickey')


print(client_private, client_pub)

# Create client.conf
run(f"touch ./{client_name}/{client_name}.conf")

client_conf = f"""[Interface]
PrivateKey = {client_private}
Address = {format_last_ip(last_ip)}
DNS = 8.8.8.8

[Peer]
PublicKey = {key_reader('./server_publickey')}
Endpoint = 1.1.1.1:51830
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 20"""

write_file(client_conf, f'./{client_name}/{client_name}.conf')

print("update wg0.conf")

new_config_peer = f"""
\n[Peer]
PublicKey = {client_pub}
AllowedIPs = {format_last_ip(last_ip)}"""

with open('./wg0.conf', 'a') as config:
    config.seek(0, 2)
    config.write(new_config_peer)
    config.close()