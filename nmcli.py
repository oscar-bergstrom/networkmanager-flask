import subprocess
from typing import List, Type, Optional
from dataclasses import dataclass

nmcli_cmd: bytes = b"/usr/bin/nmcli"


@dataclass
class Connection:
    """Class for representing connection information"""
    name: str
    uuid: str
    type: str
    device: str


@dataclass
class Device:
    device: str
    type: str
    state: str
    connection: str

@dataclass
class Network:
    in_use: str
    bssid: str
    ssid: str
    mode: str
    chan: str
    rate: str
    signal: str
    bars: str
    security: str


class CommandException(Exception):
    def __init__(self, command: List[bytes], errcode: int, message: str):
        super().__init__(message)
        self.command = command
        self.errcode = errcode
        self.message = message


def _nmcli(args: List[bytes]) -> str:
    command = [nmcli_cmd, b"-c", b"no"]
    command.extend(args)

    ret = subprocess.run(command, capture_output=True)

    if ret.returncode == 0:
        return ret.stdout.decode("utf-8")
    else:
        raise CommandException(command, ret.returncode, ret.stderr.decode("utf-8"))


def parse_table(text: str) -> List[List[str]]:
    """
    Function that parses table outputs, fields divided by at least 2 spaces
    :param text: raw text ouput from nmcli
    :return: fields[row][col]
    """
    rows = []
    for line in text.splitlines():
        fields = line.rstrip().lstrip().split("  ")
        col = []
        for field in fields:
            if field:
                stripped = field.lstrip().rstrip()
                if stripped:
                    col.append(stripped)
        if len(col):
            rows.append(col)
    return rows


def parse_dict(text: str, delimiter=":") -> dict[str, str]:
    results = {}
    for line in text.splitlines():
        try:
            key, value = line.split(delimiter, maxsplit=1)
            results[key] = value.rstrip().lstrip()
        except ValueError:
            print("Could not parse dict for line: {}".format(line))

    return results


def table_into_class(table: List[List[str]], constructor: Type) -> List[Type]:
    objects = []
    for row in table:
        obj = constructor(*row)
        objects.append(obj)

    return objects


def get_connections() -> List[Connection]:
    output = _nmcli([b"con"])
    table = parse_table(output)
    return table_into_class(table[1:], Connection)


def get_connection_info(connection: str) -> dict[str, str]:
    output = _nmcli([b"con", b"show", connection.encode("utf-8")])
    d = parse_dict(output, ":")
    return d


def get_devices() -> List[Device]:
    output = _nmcli([b"device"])
    table = parse_table(output)
    return table_into_class(table[1:], Device)


def get_device_info(device: str) -> dict[str, str]:
    output = _nmcli([b"device", b"show", device.encode("utf-8")])
    d = parse_dict(output, ":")
    return d


def scan_networks(device_name: Optional[str] = None) -> List[Network]:
    args = [b"device", b"wifi", b"list"]
    if device_name:
        args.append(b"ifname")
        args.append(device_name.encode("utf-8"))
    output = _nmcli(args)
    table = parse_table(output)

    # Putting back first empty column when applicable
    for line in table:
        if line[0] != "*":
            line.insert(0, "")
    return table_into_class(table[1:], Network)


def add_wifi(ssid: str, psk: str, device: Optional[str] = None) -> None:
    assert ssid
    assert psk

    args = [b"device", b"wifi", b"connect", ssid.encode("utf-8"), b"password", psk.encode("utf-8")]
    if device:
        args.append(b"ifname")
        args.append(device.encode("utf-8"))

    _nmcli(args)


def delete_connection(connection: str):
    _nmcli([b"con", b"delete", b"id", connection.encode("utf-8")])



