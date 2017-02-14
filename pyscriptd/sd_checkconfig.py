#!usr/bin/python
""" support tool for checkbzlac.sh script """
import os
import sys
import traceback
import re
import logging
from cdkutils.logger import Logger

class PackageChecker(object):
    """ package checker class """

    def __init__(self, logger):
        """ constructor """
        self.logger = logger
        self._packages = self.read_packages()

    @staticmethod
    def is_numeric(value):
        """ checks if a value is numeric... """
        is_a_number = True
        try:
            dummy = int(value)
        except ValueError:
            is_a_number = False
        return is_a_number

    def read_packages(self):
        """ read all packages from vtrack """
        packages = {}
        eng = re.compile(r"(\w+)\s+(\w+)")
        tmp_file = "/adp/tmp/pkg.txt"
        vtrack = "/adp/bin/vtrack"
        os.system("%s > %s" % (vtrack, tmp_file))
        vfile = open(tmp_file, "r")
        for line in vfile:
            line = line.rstrip()
            matched = eng.match(line)
            if matched != None:
                self.logger.debug("%s: %s" % (matched.group(1), matched.group(2)))
                packages[matched.group(1)] = matched.group(2)
        vfile.close()
        os.remove(tmp_file)
        return packages

    def check_package(self, package, package_type):
        """ check for individual package """
        self.logger.info("Checking for package: %s, package_type: %s" % (package, package_type))
        found = False
        if package_type in self._packages:
            found = self._packages[package_type] >= package
            if not found:
                self.logger.info("Wrong version of package %s, %s is installed; %s expected" %
                                 (package_type, self._packages[package_type], package))
        else:
            self.logger.info("Package %s doesn't exist" % package)
        return found

    def check_successful_install(self, filepath, patch_num):
        """ make sure that the ramstat file shows success """
        self.logger.info("Checking for successful patch install")
        installed = False
        full_path = "%s/ramstat.%s" % (filepath, patch_num)
        if os.path.exists(full_path):
            vfile = open(full_path, "r")
            for line in vfile:
                line = line.rstrip()
                self.logger.debug("ramstat line: %s" % line)
                if line.find("INSTALL COMPLETED SUCCESSFULLY") != -1:
                    installed = True
                    break
            vfile.close()
        return installed

    def check_patch(self, patch_num):
        """ Check if a given patch is installed... """
        self.logger.info("Checking for patch %s" % patch_num)
        found = False
        found = self.check_successful_install("/usr/ramresults", patch_num)
        if not found:
            found = self.check_successful_install("/adp/3party/Ramit/ramresults", patch_num)
        return found

    def grep_check(self, pattern, filename):
        """ check for the pattern in file... """
        self.logger.info("Checking for patch: %s in file %s" % (pattern, filename))
        found = False
        tmp_file = "/adp/tmp/patch.txt"
        cmd = "grep -in '%s' %s" % (pattern, filename)
        #print("cmd: '%s'" % cmd)
        os.system("%s > %s" % (cmd, tmp_file))
        vfile = open(tmp_file, "r")
        for line in vfile:
            line = line.rstrip()
            if len(line) > 0:
                found = True
        os.remove(tmp_file)
        return found

    def check_for_packages(self, config_file):
        """ check for all packages in config file """
        #pylint: disable-msg=too-many-branches
        all_found = True
        ret_val = ""
        csv_file = open(config_file, "r")
        lcount = 0
        for line in csv_file:
            # skip header line
            if lcount > 0:
                line = line.rstrip()
                if line[0] == '#':
                    # ignore comment line
                    pass
                else:
                    fields = line.split(",")
                    idfield = fields[0]
                    if len(fields) > 2:
                        # special handling for patch info...
                        self.logger.debug("Fields: %s=>%s (%s)" % (fields[0], fields[1], fields[2]))
                        installed = self.grep_check(fields[2], fields[1])
                    elif self.is_numeric(fields[0]):
                        installed = self.check_patch(fields[0])
                    elif len(fields) == 2:
                        self.logger.debug("Fields: %s=>%s" % (fields[0], fields[1]))
                        installed = self.check_package(fields[1], fields[0])
                        idfield = fields[1]
                    else:
                        self.logger.debug("Error -- invalid format, line: %s" % line)
                        idfield = "'Error: %s'" % line
                        installed = 0
                    if installed:
                        ret_val += "%s=found " % idfield
                    else:
                        all_found = False
                        ret_val += "%s=notfound " % idfield
            lcount = lcount + 1
        csv_file.close()
        if all_found:
            ret_val = "ALL=1 " + ret_val
        else:
            ret_val = "ALL=0 " + ret_val
        print(ret_val)

def main():
    """ main """
    logger = Logger("/adp/logs/secureDms/sd_checkconfig.log")
    #logger.set_level(logging.DEBUG)
    logger.set_level(logging.INFO)
    try:
        parser = PackageChecker(logger)
        parser.check_for_packages("/adp/bin/secureDms/sd_spec.csv")
    except IOError:
        err = sys.exc_info()[1]
        logger.exception("Error: %s" % err)
        traceback.print_exc(file=sys.stdout)

if __name__ == "__main__":
    main()
