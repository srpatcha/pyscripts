#!/usr/bin/python
""" Deliver some sanity to OS version... """

# pylint: disable=bad-builtin
import sys
import platform

class OSEnvironment(object):
    """ class to encapsulate the various tests for OS version """

    def __init__(self):
        """ constructor """
        self.__is_cygwin = False
        self.__is_windows = False
        self.__is_linux = False
        self.__version = None
        self.__version_number = None

        if sys.platform == 'cygwin':
            self.__is_cygwin = True
        elif sys.platform == 'win32':
            self.__is_windows = True
            self.__version_number = platform.release()
        elif sys.platform == 'linux2':
            self.__is_linux = True
            linux_version = self.linux_distribution()
            self.__version = linux_version[0]
            self.__version_number = linux_version[1]

    def __str__(self):
        """ as string """
        return "%s:%s:%s" % (sys.platform, self.__version, self.__version_number)

    def linux_distribution(self):
        """ if linux, expand it... """
        retval = None
        if self.__is_linux:
            retval = platform.dist()
        return retval

    def is_cygwin(self):
        """ getter """
        return self.__is_cygwin

    def is_linux(self):
        """ getter """
        return self.__is_linux

    def get_version(self):
        """ getter """
        return self.__version

    def get_version_number(self):
        """ getter """
        return self.__version_number

    @staticmethod
    def versiontuple(ver_str):
        """ converts version string (x.y.z) into a tuple for comparison purposes """
        return tuple(map(int, (ver_str.split("."))))

    def check_minimum_version(self, min_version):
        """ make sure that the minimum version of OS is running """
        return self.versiontuple(self.get_version_number()) > self.versiontuple(min_version)

    def is_dms(self):
        """ getter """
        return self.__is_linux and ((self.__version == 'redhat' and self.__version_number == '5.5') or
                                    (self.__version == 'centos' and self.check_minimum_version("7.0.0")))
