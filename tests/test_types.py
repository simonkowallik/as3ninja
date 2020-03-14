# -*- coding: utf-8 -*-
import pytest

from as3ninja.types import F5IP, F5IPv4, F5IPv6


class Test_type_F5IPx:
    test_params = [
        # IP version, IP Address, Valid(True/False)
        ["ipv4", "192.168.0.1%123/32", True],
        ["ipv4", "192.168.0.1%123", True],
        ["ipv4", "192.168.0.1/32", True],
        ["ipv4", "0.0.0.0/0", True],
        ["ipv4", "0.0.0.0%123/0", True],
        ["ipv4", "99.99.0.1%123/24", False],  # wrong mask
        ["ipv4", "1.2.3.4%-1/32", False],  # wrong rdid
        ["ipv4", "1.2.3.4%65536/32", False],  # wrong rdid
        ["ipv4", "256.0.0.1", False],  # wrong IPv4
        ["ipv4", "1.2.3.4/33", False],  # wrong mask
        ["ipv4", "127.0.0.1", False],  # loopback not allowed
        ["ipv4", "127.100.0.1", False],  # loopback not allowed
        [
            "ipv4",
            "169.254.0.1",
            True,
        ],  # link-local ok -> https://support.f5.com/csp/article/K13098
        ["ipv6", "2001:db9::%1/120", True],
        ["ipv6", "2001:db9::1%1/128", True],
        ["ipv6", "2001:db9::1%1", True],
        ["ipv6", "::%65534/0", True],
        ["ipv6", "2001:db8::", True],
        ["ipv6", "2001:DB8::", True],  # uppercase IPv6
        ["ipv6", "::", True],
        ["ipv6", "a::g", False],  # wrong IPv6
        ["ipv6", "200::cafe::1", False],  # wrong IPv6
        ["ipv6", "2001:db9::1/129", False],  # wrong mask
        ["ipv6", "2001:db9::1%ABC/cde", False],  # wrong rdid + mask
        ["ipv6", "::1", False],  # loopback not allowed
    ]

    def test_input_type(self):
        with pytest.raises(TypeError):
            F5IP(int(123))

    def test_schema_is_dict(self):
        assert isinstance(F5IP.schema(), dict)
        assert isinstance(F5IPv4.schema(), dict)
        assert isinstance(F5IPv6.schema(), dict)

    def test_schema_examples_IPAny(self):
        for example_ip in F5IP.schema()["properties"]["f5ip"]["examples"]:
            assert isinstance(F5IP(example_ip), F5IP)

    def test_schema_examples_IPv4(self):
        for example_ip in F5IPv4.schema()["properties"]["f5ip"]["examples"]:
            assert isinstance(F5IPv4(example_ip), F5IPv4)

    def test_schema_examples_IPv6(self):
        for example_ip in F5IPv6.schema()["properties"]["f5ip"]["examples"]:
            assert isinstance(F5IPv6(example_ip), F5IPv6)

    def test_dunder_str(self):
        model = F5IP("0.0.0.0")
        assert model.__str__() == "F5IP('0.0.0.0')"

    def test_dunder_repr(self):
        model = F5IP("0.0.0.0")
        assert model.__repr__() == "F5IP('0.0.0.0')"

    @pytest.mark.parametrize("ipv, test_ip, expected_result", test_params)
    def test_ipAny(self, ipv, test_ip, expected_result):
        try:
            model = F5IP(test_ip)
            assert model.addr in repr(model)
            assert model.mask in repr(model)
            assert model.rdid in repr(model)
        except ValueError:
            assert expected_result is False

    @pytest.mark.parametrize("ipv, test_ip, expected_result", test_params)
    def test_ipv4(self, ipv, test_ip, expected_result):
        if ipv == "ipv4":
            try:
                model = F5IPv4(test_ip)
                assert model.addr in repr(model)
                assert model.mask in repr(model)
                assert model.rdid in repr(model)
            except ValueError:
                assert expected_result is False
        else:
            with pytest.raises(ValueError):
                F5IPv4(test_ip)

    @pytest.mark.parametrize("ipv, test_ip, expected_result", test_params)
    def test_ipv6(self, ipv, test_ip, expected_result):
        if ipv == "ipv6":
            try:
                model = F5IPv6(test_ip)
                assert model.addr in repr(model)
                assert model.mask in repr(model)
                assert model.rdid in repr(model)
            except ValueError:
                assert expected_result is False
        else:
            with pytest.raises(ValueError):
                F5IPv6(test_ip)
