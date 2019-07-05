import io
import pkgutil
import select
import subprocess
import re
import os
import sys
import tempfile
import time
from typing import List, Callable, Optional


class WiFiUtils:
    @staticmethod
    def get_console_encoding():
        results = subprocess.check_output(["chcp"], shell=True)
        results = results.decode('ascii', errors='ignore')
        find = re.findall(r'([0-9]+)', results)
        if find:
            cope_page_num = find[0]
            if cope_page_num == '65000':
                return 'utf7'
            elif cope_page_num == '65001':
                return 'utf8'
            else:
                return 'cp'+cope_page_num
        else:
            return sys.getdefaultencoding()

    def __init__(self):
        self.codepage=self.get_console_encoding()

    def get_wifi_list(self):
        results = subprocess.check_output(["netsh", "wlan", "show", "network"])
        results = results.decode(self.codepage)
        results = results.replace("\r","")
        ls = results.split("\n")
        ls = ls[4::5]
        ssids = [sid.split(':')[1].strip() for sid in ls if len(sid)>0]
        return ssids

    @classmethod
    def scan_names(self):
        results = subprocess.check_output(["netsh", "wlan", "show", "network"])
        results = results.decode(self.get_console_encoding())
        results = results.replace("\r","")
        ls = results.split("\n")
        ls = ls[4::5]
        ssids = [sid.split(':')[1].strip() for sid in ls if len(sid)>0]
        return ssids

    @classmethod
    def scan(cls, refresh: bool = False, callback: Callable = lambda x: None) -> List['WiFiAp']:
        if refresh:
            interface: 'WiFiInterface'
            for interface in cls.get_interfaces():
                cls.disable_interface(interface.name)
                cls.enable_interface(interface.name)
            time.sleep(5)
        cp: subprocess.CompletedProcess = cls.netsh(['wlan', 'show', 'networks', 'mode=bssid'])
        callback(cp.stdout)
        return list(map(WiFiAp.parse_netsh, [out for out in cp.stdout.split('\n\n') if out.startswith('SSID')]))

    @classmethod
    def get_interfaces(cls) -> List['WiFiInterface']:
        cp: subprocess.CompletedProcess = cls.netsh(['wlan', 'show', 'interfaces'])
        inters = [out for out in cp.stdout.split('\n\n') if out.startswith('    Name') or out.startswith('    Имя')]
        ifs = map(WiFiInterface.parse_netsh,inters)
        return list(ifs)

    @classmethod
    def get_profile_template(cls) -> str:
        if __package__:
            return pkgutil.get_data(__package__, 'data/profile-template.xml').decode()
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(dir_path+'/data/profile-template.xml', 'r') as fil:
                return fil.read()

    @classmethod
    def netsh(cls, args: List[str], timeout: int = 3, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(['netsh'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=timeout, check=check, encoding=cls.get_console_encoding())

    @classmethod
    def get_profiles(cls, callback: Callable = lambda x: None) -> List[str]:
        profiles: List[str] = []

        raw_data: str = cls.netsh(['wlan', 'show', 'profiles'], check=False).stdout

        line: str
        for line in raw_data.splitlines():
            if ' : ' not in line:
                continue
            profiles.append(line.split(' : ', maxsplit=1)[1].strip())

        callback(raw_data)

        return profiles

    @classmethod
    def gen_profile(cls, ssid: str = '', auth: str = '', encrypt: str = '', passwd: str = '', remember: bool = True) \
            -> str:
        profile: str = cls.get_profile_template()

        profile = profile.replace('{ssid}', ssid)
        profile = profile.replace('{connmode}', 'auto' if remember else 'manual')

        if not passwd:
            profile = profile[:profile.index('<sharedKey>')] + \
                profile[profile.index('</sharedKey>')+len('</sharedKey>'):]
            profile = profile.replace('{auth}', 'open')
            profile = profile.replace('{encrypt}', 'none')
        else:
            if auth == 'WPA2-Personal':
                auth = 'WPA2PSK'
            if encrypt == 'CCMP':
                encrypt = 'AES'
            profile = profile.replace('{auth}', auth)
            profile = profile.replace('{encrypt}', encrypt)
            profile = profile.replace('{passwd}', passwd)

        return profile

    @classmethod
    def add_profile(cls, profile: str):
        fd: io.RawIOBase
        path: str
        fd, path = tempfile.mkstemp()

        os.write(fd, profile.encode())
        cls.netsh(['wlan', 'add', 'profile', 'filename={}'.format(path)])

        os.close(fd)
        os.remove(path)

    @classmethod
    def get_connected_interfaces(cls) -> List['WiFiInterface']:
        return list(filter(lambda i: i.state == WiFiConstant.STATE_CONNECTED or i.state == WiFiConstant.STATE_CONNECTED_RU, cls.get_interfaces()))

    @classmethod
    def disable_interface(cls, interface: str):
        cls.netsh(['interface', 'set', 'interface', 'name={}'.format(interface), 'admin=disabled'], timeout=15)

    @classmethod
    def enable_interface(cls, interface: str):
        cls.netsh(['interface', 'set', 'interface', 'name={}'.format(interface), 'admin=enabled'], timeout=15)

    @classmethod
    def connect(cls, ssid: str, passwd: str = '', remember: bool = True):
        if passwd:
            for i in range(3):
                aps: List['WiFiAp'] = cls.scan()
                if ssid in [ap.ssid for ap in aps]:
                    break
                time.sleep(5)
            else:
                raise RuntimeError('Cannot find Wi-Fi AP')

            if ssid not in cls.get_profiles():
                ap = [ap for ap in aps if ap.ssid == ssid][0]
                cls.add_profile(cls.gen_profile(
                    ssid=ssid, auth=ap.auth, encrypt=ap.encrypt, passwd=passwd, remember=remember))
            try:
                cls.netsh(['wlan', 'connect', 'name={}'.format(ssid)])
            except subprocess.CalledProcessError:
                cls.forget(ssid)

            for i in range(30):
                if list(filter(lambda it: it.ssid == ssid, cls.get_connected_interfaces())):
                    break
                time.sleep(1)
            else:
                raise RuntimeError('Cannot connect to Wi-Fi AP')

    @classmethod
    def disconnect(cls):
        cls.netsh(['wlan', 'disconnect'])

    @classmethod
    def forget(cls, *ssids: str):
        for ssid in ssids:
            cls.netsh(['wlan', 'delete', 'profile', ssid])


class WiFiAp:
    @classmethod
    def parse_netsh(cls, raw_data: str) -> 'WiFiAp':
        ssid: str = ''
        auth: str = ''
        encrypt: str = ''
        bssid: str = ''
        strength: int = 0

        line: str
        for line in raw_data.splitlines():
            if ': ' not in line:
                continue
            value: str = line.split(':', maxsplit=1)[1].strip()
            if line.startswith('SSID'):
                ssid = value
            elif line.startswith('    Authentication') or line.startswith('    Проверка подлинности'):
                auth = value
            elif line.startswith('    Encryption') or line.startswith('    Шифрование'):
                encrypt = value
            elif line.startswith('    BSSID'):
                bssid = value.lower()
            elif line.startswith('         Signal') or  line.startswith('         Сигнал'):
                strength = int(value[:-1])
        return cls(ssid=ssid, auth=auth, encrypt=encrypt, bssid=bssid, strength=strength, raw_data=raw_data)

    def __init__(
            self,
            ssid: str = '',
            auth: str = '',
            encrypt: str = '',
            bssid: str = '',
            strength: int = 0,
            raw_data: str = '',
    ):
        self._ssid: str = ssid
        self._auth: str = auth
        self._encrypt: str = encrypt
        self._bssid: str = bssid
        self._strength: int = strength
        self._raw_data: str = raw_data

    @property
    def ssid(self) -> str:
        return self._ssid

    @property
    def auth(self) -> str:
        return self._auth

    @property
    def encrypt(self) -> str:
        return self._encrypt

    @property
    def bssid(self) -> str:
        return self._bssid

    @property
    def strength(self) -> int:
        return self._strength

    @property
    def raw_data(self) -> str:
        return self._raw_data




class WiFiConstant:
    STATE_CONNECTED = 'connected'
    STATE_DISCONNECTED = 'disconnected'
    STATE_CONNECTED_RU = 'Подключено'
    STATE_DISCONNECTED_RU = 'отключено'


class WiFiInterface:
    @classmethod
    def parse_netsh(cls, raw_data: str) -> 'WiFiInterface':
        name: str = ''
        state: str = ''
        ssid: str = ''
        bssid: str = ''

        line: str
        for line in raw_data.splitlines():
            if ': ' not in line:
                continue
            value: str = line.split(':', maxsplit=1)[1].strip()
            if line.startswith('    Name') or line.startswith('    Имя'):
                name = value
            elif line.startswith('    State') or line.startswith('    Состояние'):
                state = value
            elif line.startswith('    SSID'):
                ssid = value
            elif line.startswith('    BSSID'):
                bssid = value

        c: 'WiFiInterface' = cls(name=name, state=state)
        if ssid:
            c.ssid = ssid
        if bssid:
            c.bssid = bssid
        return c

    def __init__(
            self,
            name: str = '',
            state: str = '',
            ssid: Optional[str] = None,
            bssid: Optional[str] = None,
    ):
        self._name: str = name
        self._state: str = state
        self._ssid: Optional[str] = ssid
        self._bssid: Optional[str] = bssid

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> str:
        return self._state

    @property
    def ssid(self) -> Optional[str]:
        return self._ssid

    @ssid.setter
    def ssid(self, value: str):
        self._ssid = value

    @property
    def bssid(self) -> Optional[str]:
        return self._bssid

    @bssid.setter
    def bssid(self, value: str):
        self._bssid = value



def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

if __name__ == '__main__':
    wifi = WiFiUtils()
    print(wifi.get_wifi_list())
    wifi.connect('Cisco_24','nkt12345',True)
    sys.stdout.write("Download progress: %d%%   \r" % (10))
    sys.stdout.flush()
    sys.stdout.write("Download progress: %d%%   \r" % (20))
    sys.stdout.flush()
