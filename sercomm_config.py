import base64
import configparser
import requests

from io import StringIO

SERCOMM_B64_TABLE = "ACEGIKMOQSUWYBDFHJLNPRTVXZacegikmoqsuwybdfhjlnprtvxz0246813579=+/"
STD_B64_TABLE     = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

def http_get_sercomm_config(camera_address):
    r = requests.get(f"http://{camera_address}/adm/admcfg.cfg")

    data = r.text

    return data

def http_post_sercomm_config(camera_address, configparser):
    d = None
    with StringIO('') as f:
        configparser.write(f)
        f.seek(0)
        d = f.read()

    d = sercomm_config_encode(d)
    
    r = requests.post(f"http://{camera_address}/adm/upload.cgi", data=d)

    return r.status_code

def sercomm_config_decode(sercomm_b64_config):
    sercomm_config_b64_translated = sercomm_b64_config.translate(str.maketrans(SERCOMM_B64_TABLE, STD_B64_TABLE))

    config_ini = base64.b64decode(sercomm_config_b64_translated)

    return config_ini.decode()

def sercomm_config_encode(config_ini):
    sercomm_b64_table = bytes(SERCOMM_B64_TABLE, 'utf-8')
    std_b64_table     = bytes(STD_B64_TABLE, 'utf-8')

    config_ini_b64 = base64.b64encode(bytes(config_ini, 'utf-8'))

    sercomm_b64_config = config_ini_b64.translate(bytes.maketrans(std_b64_table, sercomm_b64_table))

    return sercomm_b64_config

def top_menu(cfgparser):
    section_dict = {}
    for n in range(len(cfgparser.sections())):
        i = str(n+1)
        section_dict[i] = cfgparser.sections()[n]
        print(f"{i}) {section_dict[i]}")

    print("0) Send config")
    print("q) Quit")

    c = input("Choose a section: ")

    if c.lower() == 'q':
        return 'q'
    elif c == '0':
        return '0'
    elif c in section_dict.keys():
        return section_dict[c]

def items_menu(items):
    items_dict = {}
    for n in range(len(items)):
        i = str(n+1)
        k, v = items[n]
        items_dict[i] = {k: v}
        print(f"{i}) {k} = {v}")

    print("0) Back")

    c = input("Choose an item: ")

    if c == '0':
        return '0'
    elif c in items_dict.keys():
        return items_dict[c]

def main():
    camera_address = "administrator:@10.0.0.37"

    cfgparser = configparser.ConfigParser()
    cfgparser.read_string(sercomm_config_decode(http_get_sercomm_config(camera_address)))

    while True:
        c = top_menu(cfgparser)
        if c == 'q':
            return
        elif c == '0':
            http_post_sercomm_config(camera_address, cfgparser)
        elif c:
            sect = c
            while True:
                i = items_menu(cfgparser.items(c))
                if i == '0':
                    break
                else:
                    opt = list(i.keys())[0]
                    cfgparser.set(sect, opt, input("Enter new value: "))

# Translate and write to config.ini
#config_ini = sercomm_config_decode(sercomm_config_b64)
#with open('config2.ini', 'wb') as f:
#    f.write(config_ini)

# Read from config.ini, b64encode, then translate b64 charset
#data = None
#with open('config.ini', 'rb') as f:
#    data = f.read()

#sercomm_b64_config = sercomm_config_encode(data)

#with open('config.b64', 'wb') as f:
#    f.write(sercomm_b64_config)

#print(sercomm_b64_config)

if __name__ == '__main__':
    main()