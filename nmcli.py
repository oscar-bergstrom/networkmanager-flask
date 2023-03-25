import subprocess
from typing import List, Type, TypedDict
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


def _nmcli(args: List[bytes]) -> str:
    command = [nmcli_cmd, b"-c", b"no"]
    command.extend(args)

    ret = subprocess.run(command, capture_output=True)

    if ret.returncode == 0:
        return ret.stdout.decode("utf-8")
    else:
        raise IOError("Running {} returned {}".format(command, ret.returncode))


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
            key, value = line.split(delimiter)
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


def get_connection_info(connection: str):
    output = _nmcli([b"con", b"show", connection.encode("utf-8")])
    d = parse_dict(output, ":")
    return d


def get_devices() -> List[Device]:
    output = _nmcli([b"device"])
    table = parse_table(output)
    return table_into_class(table[1:], Device)
