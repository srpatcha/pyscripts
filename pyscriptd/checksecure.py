#!/usr/bin/python
""" Execute a pgsql query script to see whether or not to disable telnet. """

import os
import re
import getopt
import sys
import logging
from cdkutils.logger import Logger
from cdkutils.xinetsvc import XInetService

BASE_PATH = '/adp/bin/secureDms'
LOG_NAME = '/adp/logs/secureDms/checksecure.log'
SCRIPT_NAME = '/usr/bin/python %s/pyscripts/checksecure.py' % BASE_PATH

LOGGER = Logger(LOG_NAME)

def execute_system_cmd(cmd):
    """ Execute a system cmd. Send all os.system calls through
        here for logging purposes... """
    LOGGER.debug("Executing '%s'..." % cmd)
    os.system(cmd)

class PostgreSQLDatabase(object):
    """ a wrapper around the psql command line utility """
    def __init__(self, user, database):
        """ constructor """
        self.__user = user
        self.__database = database
        self.__tempname = "/adp/tmp/psql.txt"

    def close(self):
        """ zap the temp file... """
        os.remove(self.__tempname)

    def execute_query(self, query):
        """ execute a given query, returning first row """
        exp = re.compile(r'\(.*\)')
        results = None
        execute_system_cmd("psql -U %s -d %s -c \"%s\" > %s" % (self.__user,
                                                                self.__database,
                                                                query,
                                                                self.__tempname))
        found = False
        infile = open(self.__tempname, "r")
        for line in infile:
            line = line.strip()
            LOGGER.debug("line: %s" % line)
            if found:
                re_match = exp.match(line)
                if re_match == None:
                    results = line
                LOGGER.debug("results: %s" % results)
                break
            if line == '------------------':
                found = True
        return results

class CrontabEditor(object):
    """ add/remove entries in crontab """

    # just static methods so could be functions, but encapsulate them together...
    @staticmethod
    def add_entry(schedule, command):
        """ add a command to crontab... """
        #pylint: disable=line-too-long
        cmd = '(crontab -l ; echo "%s %s > /dev/null 2>&1") 2>&1 | grep -v "no crontab" | sort | uniq | crontab -' % (schedule, command)
        LOGGER.info("crontab: Run '%s' on schedule '%s'" % (command, schedule))
        execute_system_cmd(cmd)

    @staticmethod
    def delete_entry(command):
        """ delete an entry from crontab... """
        #pylint: disable=line-too-long
        cmd = '(crontab -l) 2>&1 | grep -v "no crontab" | grep -v "%s" | sort | uniq | crontab -' % command
        LOGGER.info("crontab: Delete entry '%s'" % command)
        execute_system_cmd(cmd)

class FieldChecker(object):
    """ check field and togglet telnet """
    def __init__(self, schedule):
        """ constructor """
        self.__schedule = schedule
        self.__scriptname = SCRIPT_NAME

    @staticmethod
    def fetch_query(code='DisableTelnetService'):
        """ build the query """
        query = """
SELECT configured_value
FROM wi.wi_portal_configuration_value
WHERE portal_configuration_value_code = '%s'""" % code
        return query

    @staticmethod
    def disable_telnet_service(do_disable):
        """ adjust telnet service state """
        svc = XInetService('telnet', LOGGER)
        is_disabled = not svc.is_enabled()
        LOGGER.debug("current telnet status: disabled: %s, new status: %s" % (is_disabled, do_disable))
        # only if the state of the service changes do we do anything...
        if do_disable != is_disabled:
            LOGGER.info("Setting telnet disabled status to '%s'" % do_disable)
            svc.set_service_status(do_disable)
        else:
            LOGGER.info("State of telnet service not changed...")

    def check_for_ssh_field_enabled(self):
        """ check if the DisableTelnetService field is enabled... """
        LOGGER.debug("Checking DisableTelnetService...")
        database = None
        try:
            database = PostgreSQLDatabase('adp_apps', 'adp_dms')
            query = self.fetch_query()
            results = database.execute_query(query)
            # if the row doesn't exist, None will be returned; treat
            # that as unchecked...
            if results is None or len(results) == 0:
                results = 'FALSE'
            LOGGER.debug("query: %s; results='%s'" % (query, results))
            if results == 'TRUE':
                self.disable_telnet_service(True)
            elif results == 'FALSE':
                self.disable_telnet_service(False)
        finally:
            if database != None:
                database.close()
        LOGGER.debug("Finished....")

    def add_crontab_entry(self):
        """ adds a crontab entry for this script """
        CrontabEditor.add_entry(self.__schedule, self.__scriptname)

    def delete_crontab_entry(self):
        """ removes the crontab entry for this script """
        CrontabEditor.delete_entry(self.__scriptname)

def usage():
    """ display usage and exit """
    print("query.py [-d] [-a]")
    print("\t-D turns on debug level logging")
    print("\t-h shows help (this info)")
    print("\t-a adds a crontab entry")
    print("\t-d deletes a crontab entry")
    print("\t-s specifies crontab schedule")
    sys.exit()

def main():
    """ main function """

    add_entry = False
    delete_entry = False
    schedule = "0 * * * *"
    opts, dummy = getopt.getopt(sys.argv[1:], "hDads:",
                                ["help", "debug", "add", "delete", "schedule="])
    for opt, arg in opts:
        if opt in ('-D', '--debug'):
            LOGGER.set_level(logging.DEBUG)
        elif opt in ('-a', '--add'):
            add_entry = True
        elif opt in ('-s', '--schedule'):
            schedule = arg
        elif opt in ('-d', '--delete'):
            delete_entry = True
        elif opt in ('-h', '--help'):
            usage()

    checker = FieldChecker(schedule)
    if add_entry:
        checker.add_crontab_entry()
    elif delete_entry:
        checker.delete_crontab_entry()
    else:
        checker.check_for_ssh_field_enabled()

if __name__ == "__main__":
    main()
