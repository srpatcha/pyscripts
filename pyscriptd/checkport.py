#!/usr/bin/python
""" Check to see if a TCP port is open """

import sys
import getopt
import traceback
import socket
import logging
from cdkutils.logger import Logger

TELNET_PORT = 23
SSH_PORT = 22
HTTP_PORT = 80
HTTPS_PORT = 443
HTTP_ALT_PORT = 8080
VM_IP = "192.168.12.12"

class PortCheck(object):
    """ checks to see if a given TCP port is open... """

    def __init__(self, host, port, logger):
        """ constructor """
        self.__host = None
        self.__port = None
        self.__logger = logger
        self.set_port(port)
        self.set_host(host)

    def set_port(self, port):
        """ Set the port """
        self.__port = port

    def set_host(self, host):
        """ Set the host """
        self.__host = host

    def port_open(self):
        """ returns True IFF the port is open """
        retval = False
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.__host, self.__port))
            self.__logger.debug("attempting to open socket '%s'[%d]:%d" %
                                (self.__host, self.__port, result))
            if result == 0:
                retval = True
            else:
                self.__logger.debug("connect_ex result=%d" % result)
        finally:
            if sock != None:
                # if we actually got a socket connection, do a graceful shutdown...
                if retval:
                    sock.shutdown(socket.SHUT_RDWR)
                sock.close()
        return retval

    def get_service_name(self):
        """ display the service associated the port... """
        retval = "Unknown?"
        if self.__port == TELNET_PORT:
            retval = "Telnet"
        elif self.__port == SSH_PORT:
            retval = "SSH"
        elif self.__port == HTTP_PORT:
            retval = "HTTP"
        elif self.__port == HTTPS_PORT:
            retval = "HTTPS"
        elif self.__port == HTTP_ALT_PORT:
            retval = "HTTP/Tomcat"
        return retval

def usage():
    """ Show usage and exit... """
    print("usage: checkport.py [-hp:H:d]")
    print("where:")
    print("\t-d turns on debug level logging")
    print("\t-h shows help (this info)")
    print("\t-p specifies the port to check (defaults to 23 {telnet}")
    print("\t-H species the host (defaults to 12.12.12.12 (vagrantdms)")
    sys.exit()

def main():
    """ main function... """
    logger = Logger()
    try:
        host = VM_IP #'localhost'
        port = 23
        opts, dummy = getopt.getopt(sys.argv[1:], "hp:H:d", ["help", "port=", "host="])
        for opt, arg in opts:
            if opt == '-d':
                logger.set_level(logging.DEBUG)
            elif opt in ('-p', '--port'):
                logger.info("setting port to %s" % arg)
                port = int(arg)
            elif opt in ('-H', '--host'):
                logger.info("setting host to %s" % arg)
                host = arg
            elif opt in ('-h', '--help'):
                usage()
        checker = PortCheck(host, port, logger)
        if checker.port_open():
            print("%s (%s):%s is open" % (host, checker.get_service_name(), port))
        else:
            print("%s (%s):%s is closed" % (host, checker.get_service_name(), port))
    except IOError:
        err = sys.exc_info()[1]
        logger.exception("Error: %s" % err)
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()
