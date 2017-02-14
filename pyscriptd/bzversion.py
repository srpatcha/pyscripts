#!usr/bin/python
""" support tool for checkbzlac.sh script """
import sys
import traceback
import re
import os
import shutil
from cdkutils.logger import Logger

EXPECTED_BZ_VERSION = "6.2.3.2501"
CONFIG_TARGET_PATH = "/adp/home/www_serv/templates/en_US/jsi/common/includes/modules.d/software"
CFG_FILE_NAME = "cdk_terminal_emulator.xml"
CFG_TARGET_FILE = "%s/%s" % (CONFIG_TARGET_PATH, CFG_FILE_NAME)

#CFG_SOURCE_PATH = "/vagrant"
CFG_SOURCE_PATH = "/adp/bin/secureDms"
CFG_SOURCE_FILE = "%s/%s" % (CFG_SOURCE_PATH, CFG_FILE_NAME)
class BZVerifier(object):
    """ class to verify correct version of BZ is configured """
    def __init__(self, logger):
        """ constructor """
        self.logger = logger

    def update_pc_config(self):
        """ if the correct version of cdk_terminal_emulator.xml isn't configured, update """
        self.execute_pcconfig_cmd(False)
        if not self.check_bz_version():
            self.logger.info("Updating version of BZ using %s" % CFG_SOURCE_FILE)
            # copy the source file into the template location...
            shutil.copy(CFG_SOURCE_FILE, CFG_TARGET_FILE)
            self.execute_pcconfig_cmd(True)
        else:
            self.logger.info("Correct version of cdk_terminal_emulator is already in place")

    def execute_pcconfig_cmd(self, implode):
        """ execute pcconfig.php to implode/explode the pcconfig file """
        if implode:
            cmd = "-i"
        else:
            cmd = "-e"
        self.logger.info("Executing pcconfig.php %s" % cmd)
        os.system("php /adp/bin/pcconfig.php %s -v > /dev/null" % cmd)

    def check_bz_version(self):
        """ check for right version of BZ in config file """
        #<expectedValue>6.2.3.2501</expectedValue>
        eng = re.compile(r".*\<expectedValue\>(.+)\<.*")
        found = False
        cfg_file = open(CFG_TARGET_FILE, "r")
        for line in cfg_file:
            line = line.rstrip()
            self.logger.info("line: %s" % line)
            matched = eng.match(line)
            if matched != None:
                self.logger.info("BZ version: %s, expected: %s" % (matched.group(1), EXPECTED_BZ_VERSION))
                if matched.group(1) >= EXPECTED_BZ_VERSION:
                    found = True
                break
        cfg_file.close()
        return found

def main():
    """ main """
    logger = Logger("/adp/logs/secureDms/checkpcconfig.log")
    try:
        verifier = BZVerifier(logger)
        verifier.update_pc_config()

    except IOError:
        err = sys.exc_info()[1]
        logger.exception("Error: %s" % err)
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()
