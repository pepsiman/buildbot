# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import xml.dom.minidom
import xml.parsers.expat
from twisted.python import log
from buildbot.process import buildstep
from buildbot.status.results import SUCCESS, WARNINGS, FAILURE
from buildbot.status.logfile import STDOUT, STDERR
from buildbot.steps.shell import ShellCommand

class CppCheck(ShellCommand):
    warnCount = 0

    def __init__(self, args, verbose=False, **kwargs) :
        self.verbose = verbose

        ShellCommand.__init__(self,
                name = "CppCheck",
                description = "CppChecking",
                descriptionDone = "CppCheck",
                warnOnWarnings = True,
                command=["cppcheck", "--xml-version=2"] + args,
                **kwargs)

    def createSummary(self, stdio):
        stderr = "".join(stdio.getChunks([STDERR], onlyText=True))
        self.addCompleteLog("cppcheck.xml", stderr)

        try:
            result_xml = xml.dom.minidom.parseString(stderr)
        except xml.parsers.expat.ExpatError:
            log.err("Corrupted xml, aborting step")
            raise buildstep.BuildStepFailed()

        warnings = []
        for error in result_xml.getElementsByTagName('error'):
            id = error.getAttribute('id')
            severity = error.getAttribute('severity')
            if self.verbose:
                message = error.getAttribute('verbose')
            else:
                message = error.getAttribute('msg')

            locations = error.getElementsByTagName('location')
            if locations:
                location = locations[0]
                file = location.getAttribute('file')
                lineNo = location.getAttribute('line')
                warnings.append("[%s:%s]: (%s) %s" % (file, lineNo, severity, message))
            else:
                warnings.append("(%s) %s" % (severity, message))

            self.warnCount += 1

        if self.warnCount:
            self.addCompleteLog("warnings (%d)" % self.warnCount,
                    "\n".join(warnings) + "\n")

        warnings_stat = self.step_status.getStatistic('warnings', 0)
        self.step_status.setStatistic('warnings', warnings_stat + self.warnCount)

        old_count = self.getProperty("warnings-count", 0)
        self.setProperty("warnings-count", old_count + self.warnCount, "CppCheck")

    def evaluateCommand(self, cmd):
        if cmd.didFail():
            return FAILURE
        if self.warnCount:
            return WARNINGS
        return SUCCESS
