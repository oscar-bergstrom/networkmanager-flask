from unittest import TestCase
from unittest.mock import Mock
import nmcli

from dataclasses import dataclass


class ParseTableTests(TestCase):
    SINGLE_LINE = "first  second  third"
    UNEVEN_SPACE = "first  second   third"
    TWO_BY_TWO = """R0C0   R0C1
    R1C0     R1C1"""

    def test_single_line(self):
        matrix = nmcli.parse_table(self.SINGLE_LINE)
        assert len(matrix) == 1
        assert len(matrix[0]) == 3

        assert matrix[0][0] == "first"
        assert matrix[0][1] == "second"
        assert matrix[0][2] == "third"

    def test_single_line_uneven_space(self):
        matrix = nmcli.parse_table(self.UNEVEN_SPACE)
        assert len(matrix) == 1
        assert len(matrix[0]) == 3

        assert matrix[0][0] == "first"
        assert matrix[0][1] == "second"
        assert matrix[0][2] == "third"

    def test_two_by_two(self):
        m = nmcli.parse_table(self.TWO_BY_TWO)
        assert m[0][0] == "R0C0"
        assert m[0][1] == "R0C1"
        assert m[1][0] == "R1C0"
        assert m[1][1] == "R1C1"

    def test_trailing_space(self):
        m = nmcli.parse_table("1  2  3 ")
        assert m[0][0] == "1"
        assert m[0][1] == "2"
        assert m[0][2] == "3"

    def test_newline_characters(self):
        b = b"a  b\nc  d\n"
        s = b.decode("utf-8")
        m = nmcli.parse_table(s)

        assert len(m) == 2
        assert m[0][0] == "a"
        assert m[0][1] == "b"
        assert m[1][0] == "c"
        assert m[1][1] == "d"



class TableIntoClassesTest(TestCase):
    class SimpleClass:
        def __init__(self, a: str, b: str):
            self.a = a
            self.b = b

    @dataclass
    class DataClass:
        a: str
        b: str

    def test_simple_class(self):
        classes = nmcli.table_into_class([["a", "b"]], TableIntoClassesTest.SimpleClass)
        self.assertIsInstance(classes[0], TableIntoClassesTest.SimpleClass)
        assert classes[0].a == "a"
        assert classes[0].b == "b"

    def test_with_dataclass(self):
        classes = nmcli.table_into_class([["a", "b"]], TableIntoClassesTest.DataClass)
        self.assertIsInstance(classes[0], TableIntoClassesTest.DataClass)
        assert classes[0].a == "a"
        assert classes[0].b == "b"

    def test_empty_list(self):
        classes = nmcli.table_into_class([], TableIntoClassesTest.SimpleClass)
        assert len(classes) == 0

    def test_multiple_return(self):
        classes = nmcli.table_into_class([["a", "b"], ["c", "d"]], TableIntoClassesTest.SimpleClass)
        assert classes[0].a == "a"
        assert classes[0].b == "b"
        assert classes[1].a == "c"
        assert classes[1].b == "d"


class GetConnectionsTest(TestCase):
    CONNECTIONS = """NAME                UUID                                  TYPE      DEVICE          
    blan                b6f51e11-79d7-4216-9b67-a63a910551fe  wifi      wlx002275ff9588 
    newbie-5            79e22da2-4ebb-4845-b3e4-ec45423f8754  wifi      wlp2s0          
    Wired connection 1  50be8431-404f-3255-a055-4949d051ad1b  ethernet  --    
    """

    def setUp(self) -> None:
        self.nmcli_mock = Mock()
        self.nmcli_mock.return_value = self.CONNECTIONS
        nmcli._nmcli = self.nmcli_mock

    def test_base_command_is_called(self):
        nmcli.get_connections()
        self.nmcli_mock.assert_called()

    def test_number_of_connection(self):
        assert len(nmcli.get_connections()) == 3

    def test_all(self):
        con = nmcli.get_connections()

        assert con[0].name == "blan"
        assert con[0].uuid == "b6f51e11-79d7-4216-9b67-a63a910551fe"
        assert con[0].type == "wifi"
        assert con[0].device == "wlx002275ff9588"

        assert con[1].name == "newbie-5"
        assert con[1].uuid == "79e22da2-4ebb-4845-b3e4-ec45423f8754"
        assert con[1].type == "wifi"
        assert con[1].device == "wlp2s0"

        assert con[2].name == "Wired connection 1"
        assert con[2].uuid == "50be8431-404f-3255-a055-4949d051ad1b"
        assert con[2].type == "ethernet"
        assert con[2].device == "--"


class GetDevicesTest(TestCase):
    DEVICES = """DEVICE           TYPE      STATE         CONNECTION 
wlx002275ff9588  wifi      connected     blan              
lo               loopback  unmanaged     --  """

    def setUp(self) -> None:
        self.nmcli_mock = Mock()
        self.nmcli_mock.return_value = self.DEVICES
        nmcli._nmcli = self.nmcli_mock

    def test_base_command_is_called(self):
        nmcli.get_devices()
        self.nmcli_mock.assert_called()

    def test_number_of_connection(self):
        assert len(nmcli.get_devices()) == 2

    def test_contents(self):
        devices = nmcli.get_devices()

        assert devices[0].device == "wlx002275ff9588"
        assert devices[0].type == "wifi"
        assert devices[0].state == "connected"
        assert devices[0].connection == "blan"

        assert devices[1].device == "lo"
        assert devices[1].type == "loopback"
        assert devices[1].state == "unmanaged"
        assert devices[1].connection == "--"


class ParseDictTest(TestCase):
    def test_single_line(self):
        d = nmcli.parse_dict("KEY:  PARAM")
        assert d["KEY"] == "PARAM"

    def test_multiline(self):
        d = nmcli.parse_dict("A:  B\nC:  D")
        assert d["A"] == "B"
        assert d["C"] == "D"

    def test_no_space(self):
        d = nmcli.parse_dict("A:B")
        assert d["A"] == "B"


    def test_empty_string(self):
        d = nmcli.parse_dict("")
        assert len(d) == 0


    def test_empty_lines(self):
        d = nmcli.parse_dict("A:B\n\n\nC:D\n\n")
        assert d["A"] == "B"
        assert d["C"] == "D"

    def test_separator_in_value(self):
        d = nmcli.parse_dict("GENERAL.HWADDR: 00:22:75:FF:95:88")
        assert d["GENERAL.HWADDR"] == "00:22:75:FF:95:88"


class GetConnectionInfoTest(TestCase):
    OUTPUT = """connection.id:                          blan
connection.uuid:                        b6f51e11-79d7-4216-9b67-a63a910551fe
connection.stable-id:                   --
connection.type:                        802-11-wireless
"""

    def setUp(self) -> None:
        self.nmcli_mock = Mock()
        self.nmcli_mock.return_value = self.OUTPUT
        nmcli._nmcli = self.nmcli_mock

    def test_base_command_is_called(self):
        nmcli.get_connection_info("blan")
        self.nmcli_mock.assert_called_with([b'con', b'show', b'blan'])

    def test_contents(self):
        d = nmcli.get_connection_info("blan")
        assert d["connection.id"] == "blan"
        assert d["connection.uuid"] == "b6f51e11-79d7-4216-9b67-a63a910551fe"
        assert d["connection.stable-id"] == "--"
        assert d["connection.type"] == "802-11-wireless"


class GetDeviceInfo(TestCase):
    OUTPUT = """GENERAL.DEVICE:                         wlx002275ff9588
GENERAL.TYPE:                           wifi
GENERAL.HWADDR:                         00:22:75:FF:95:88
"""

    def setUp(self) -> None:
        self.nmcli_mock = Mock()
        self.nmcli_mock.return_value = self.OUTPUT
        nmcli._nmcli = self.nmcli_mock

    def test_base_command_is_called(self):
        nmcli.get_device_info("wlx002275ff9588")
        self.nmcli_mock.assert_called_with([b'device', b'show', b'wlx002275ff9588'])

    def test_contents(self):
        d = nmcli.get_connection_info("wlx002275ff9588")
        assert d["GENERAL.DEVICE"] == "wlx002275ff9588"
        assert d["GENERAL.TYPE"] == "wifi"
        assert d["GENERAL.HWADDR"] == "00:22:75:FF:95:88"


class ScanNetworkTest(TestCase):
    OUTPUT = """IN-USE  BSSID              SSID                          MODE   CHAN  RATE        SIGNAL  BARS  SECURITY  
        00:22:75:FF:95:88  blan                          Infra  1     54 Mbit/s   100     ▂▄▆█  WPA1 WPA2 
        AC:9E:17:80:E7:48  newbie                        Infra  10    195 Mbit/s  100     ▂▄▆█  WPA2      
*       AC:9E:17:80:E7:4C  newbie-5                      Infra  36    405 Mbit/s  50      ▂▄__  WPA2      
        FC:EC:DA:11:D5:13  ASUS                          Infra  1     195 Mbit/s  37      ▂▄__  WPA2  
"""

    def setUp(self) -> None:
        self.nmcli_mock = Mock()
        self.nmcli_mock.return_value = self.OUTPUT
        nmcli._nmcli = self.nmcli_mock

    def test_base_command_is_called(self):
        nmcli.scan_networks("my_interface")
        self.nmcli_mock.assert_called_with([b"device", b"wifi", b"list", b"ifname", b"my_interface"])

    def test_base_command_is_called_no_interface(self):
        nmcli.scan_networks()
        self.nmcli_mock.assert_called_with([b"device", b"wifi", b"list"])

    def test_network_blan(self):
        networks = nmcli.scan_networks()
        assert networks[0].in_use == ""
        assert networks[0].bssid == "00:22:75:FF:95:88"
        assert networks[0].ssid == "blan"
        assert networks[0].mode == "Infra"
        assert networks[0].chan == "1"
        assert networks[0].rate == "54 Mbit/s"
        assert networks[0].signal == "100"
        assert networks[0].bars == "▂▄▆█"
        assert networks[0].security == "WPA1 WPA2"


