#!/usr/bin/python
""" A thin wrapper around python's built in logger so we can extend it, if needed... """
import logging

class Logger(object):
    """ A wrapper class around python's built in logger so we can extend it, if needed... """
    def __init__(self, filename=None, loglevel=logging.INFO):
        """ constructor """
        self.__level = loglevel
        self.__filename = filename
        if self.__filename != None:
            logging.basicConfig(filename=self.__filename,
                                level=loglevel,
                                filemode='w',
                                format='%(asctime)s %(levelname)-8s %(message)s',
                                datefmt='%a, %d %b %Y %H:%M:%S',)
        else:
            logging.basicConfig(level=loglevel,
                                format='%(asctime)s %(levelname)-8s %(message)s',
                                datefmt='%a, %d %b %Y %H:%M:%S',)

    def __echo_to_console(self, msg):
        """ if the log level is DEBUG and we're using a logfile, echo to the console, too... """
        if self.__level == logging.DEBUG and self.__filename != None:
            print("%s" % msg)

    def info(self, msg):
        """ info level logging """
        logging.info(msg)
        self.__echo_to_console(msg)

    def debug(self, msg):
        """ debug level logging """
        logging.debug(msg)
        self.__echo_to_console(msg)

    def exception(self, msg):
        """ exception level logging """
        logging.exception(msg)
        self.__echo_to_console(msg)

    def error(self, msg):
        """ error level logging """
        logging.error(msg)
        self.__echo_to_console(msg)

    def warning(self, msg):
        """ warning level logging """
        logging.warning(msg)
        self.__echo_to_console(msg)

    def set_level(self, level):
        """ set the log level """
        self.__level = level
        logging.getLogger().setLevel(level)
        self.debug("Set logging level to %d" % level)
