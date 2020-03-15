# -*- coding: utf-8 -*-

from as3ninja.jinja2 import J2Ninja


class Test_J2Ninja:
    @staticmethod
    def test_registerfunction():
        @J2Ninja.registerfunction
        def my_function():
            pass

        assert J2Ninja.functions["my_function"] == my_function

    @staticmethod
    def test_registerfilter():
        @J2Ninja.registerfilter
        def my_filter():
            pass

        assert J2Ninja.filters["my_filter"] == my_filter

    @staticmethod
    def test_registertest():
        @J2Ninja.registertest
        def my_test():
            return True

        assert J2Ninja.tests["my_test"] == my_test

    @staticmethod
    def test_registerfilterfunction():
        @J2Ninja.registerfunction
        @J2Ninja.registerfilter
        def my_filterfunction():
            return True

        assert J2Ninja.functions["my_filterfunction"] == my_filterfunction
        assert J2Ninja.filters["my_filterfunction"] == my_filterfunction
