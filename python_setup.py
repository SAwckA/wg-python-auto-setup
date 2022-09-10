import subprocess
import os


ETH_INTERFACE = 'eth0'

def file_exists(path):
    try:
        os.stat(path)
    except OSError:
        return False
    return True

def run (args):
    result = subprocess.run(args, shell=True)
    return result

def key_reader(path) -> str:
    with open(path) as key_file:
        key = key_file.read().replace('\n', '')
        key_file.close()
    
    return key

def write_file(text, path):
    with open(path, 'w') as file:
        file.write(text)
        file.close()

def setup():
    if not file_exists('./server_privatekey') and not file_exists('./server_publickey'):
        run('wg genkey | tee ./server_privatekey | wg pubkey | tee ./server_publickey')
    else:
        print('server already setuped')
        quit()

    server_private = key_reader('server_privatekey')

    server_public = key_reader('server_publickey')

    run('touch wg0.conf')

    wg_conf = f"""[Interface]
PrivateKey = {server_private}
Address = 10.0.0.1/24
ListenPort = 51830
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {ETH_INTERFACE} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {ETH_INTERFACE} -j MASQUERADE"""

    write_file(wg_conf, 'wg0.conf')

    print('set configuration')

    print('systemd daemon')

    run('systemctl enable wg-quick@wg0.service')
    run('systemctl start wg-quick@wg0.service')
    run('systemctl status wg-quick@wg0.service')

    print('setup ip forward')
    run('echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf')
    run('sysctl -p')

if __name__ == "__main__":
    setup()
