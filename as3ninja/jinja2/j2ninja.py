# -*- coding: utf-8 -*-
"""
J2Ninja collects jinja2 filters, functions an tests in a single class.
"""


class J2Ninja:
    """
    J2Ninja provides decorator methods to register jinja2 filters,
    functions and tests, which are available as class attributes (dict).
    """

    filters: dict = {}
    functions: dict = {}
    tests: dict = {}

    @classmethod
    def registertest(cls, function):
        """Decorator to register a jinja2 test"""
        cls.tests[function.__name__] = function
        return function

    @classmethod
    def registerfilter(cls, function):
        """Decorator to register a jinja2 filter"""
        cls.filters[function.__name__] = function
        return function

    @classmethod
    def registerfunction(cls, function):
        """Decorator to register a jinja2 function"""
        cls.functions[function.__name__] = function
        return function
