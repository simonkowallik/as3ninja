# -*- coding: utf-8 -*-
"""
AS3 Ninja types.
"""
import ipaddress
from typing import Any, Optional

from pydantic import BaseModel

__all__ = [
    "F5IP",
    "F5IPv4",
    "F5IPv6",
]


class BaseF5IP(str):
    """
    F5IP base class.
    Accepts IPv4 and IPv6 IP addresses in F5 notation.
    """

    @staticmethod
    def _get_addr(ipaddr: str) -> str:
        addr = ipaddr.split("%")[0]
        if addr != ipaddr:
            return addr
        return ipaddr.split("/")[0]

    @staticmethod
    def _get_mask(ipaddr: str) -> str:
        try:
            return ipaddr.split("/")[1]
        except IndexError:
            return ""

    @staticmethod
    def _get_rdid(ipaddr: str) -> str:
        try:
            ipaddr = ipaddr.split("/")[0]
            return ipaddr.split("%")[1]
        except IndexError:
            return ""

    @staticmethod
    def _validate_ipv4(value: str) -> None:
        try:
            ipaddress.IPv4Network(value)
        except ValueError:
            raise ValueError(f"invalid address: '{value}'") from None

        if ipaddress.IPv4Network(value).is_loopback is True:
            raise ValueError(f"invalid address: '{value}': loopback not allowed")

    @staticmethod
    def _validate_ipv6(value: str) -> None:
        try:
            ipaddress.IPv6Network(value)
        except ValueError:
            raise ValueError(f"invalid address: '{value}'") from None

        if ipaddress.IPv6Network(value).is_loopback is True:
            raise ValueError(f"invalid address: '{value}': loopback not allowed")

    @classmethod
    def _validate_ipany(cls, value: str) -> None:
        try:
            cls._validate_ipv4(value)
        except ValueError:
            cls._validate_ipv6(value)

    @staticmethod
    def _validate_rdid(rdid: str) -> None:
        if rdid:
            try:
                _rdid = int(rdid)
            except ValueError:
                raise ValueError(f"invalid route domain: '{rdid}'") from None

            if _rdid < 0 or _rdid > 65534:
                raise ValueError(f"invalid route domain: '{rdid}'")

    @classmethod
    def _validate_ip(cls, value: str) -> None:
        cls._validate_ipany(value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                "192.0.2.1",
                "192.0.2.0/24",
                "192.0.2.1%12345",
                "192.0.2.0%12345/24",
                "2001:db8::1",
                "2001:db8::/32",
                "2001:db8::1%12345",
                "2001:db8::%12345/32",
            ]
        )

    @classmethod
    def validate(cls, value):
        """
        Validate method is automatically called pydantic.
        """
        addr = cls._get_addr(value)
        mask = cls._get_mask(value)
        rdid = cls._get_rdid(value)

        cls._validate_rdid(rdid)

        if mask:
            cls._validate_ip(f"{addr}/{mask}")
        else:
            cls._validate_ip(addr)

        return cls(f"{value}")


class BaseF5IPv4(BaseF5IP):
    """
    F5IPv4 base class.
    Accepts IPv4 addresses in F5 notation.
    """

    @classmethod
    def _validate_ip(cls, value: str) -> None:
        cls._validate_ipv4(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                "192.0.2.1",
                "192.0.2.0/24",
                "192.0.2.1%12345",
                "192.0.2.0%12345/24",
            ]
        )


class BaseF5IPv6(BaseF5IP):
    """
    F5IPv6 base class.
    Accepts IPv6 addresses in F5 notation.
    """

    @classmethod
    def _validate_ip(cls, value: str) -> None:
        cls._validate_ipv6(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=[
                "2001:db8::1",
                "2001:db8::/32",
                "2001:db8::1%12345",
                "2001:db8::%12345/32",
            ]
        )


class F5IP(BaseModel):
    """
    Accepts and validates IPv6 and IPv4 addresses in F5 notation.
    """

    f5ip: BaseF5IP
    addr: str
    mask: Optional[Any]
    rdid: Optional[Any]

    def __init__(self, f5ip):
        if not isinstance(f5ip, str):
            raise TypeError("string required")
        super().__init__(
            f5ip=f5ip,
            addr=BaseF5IP._get_addr(f5ip),
            mask=BaseF5IP._get_mask(f5ip),
            rdid=BaseF5IP._get_rdid(f5ip),
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.f5ip.__repr__()})"

    def __str__(self):
        return f"{self.__class__.__name__}({self.f5ip.__repr__()})"


class F5IPv4(F5IP):
    """
    Accepts and validates IPv4 addresses in F5 notation.
    """

    f5ip: BaseF5IPv4


class F5IPv6(F5IP):
    """
    Accepts and validates IPv6 addresses in F5 notation.
    """

    f5ip: BaseF5IPv6
