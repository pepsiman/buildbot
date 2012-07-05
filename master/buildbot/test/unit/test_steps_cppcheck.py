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

import textwrap
from buildbot.status.results import FAILURE, SUCCESS, WARNINGS
from buildbot.steps import cppcheck
from buildbot.test.fake.remotecommand import ExpectShell
from buildbot.test.util import steps
from twisted.trial import unittest

xml_no_errors = '''\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
  <cppcheck version="1.54"/>
  <errors>
  </errors>
</results>'''

xml_one_error = '''\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
  <cppcheck version="1.54"/>
  <errors>
  <error id="returnReference" severity="error" msg="Returning reference to auto variable" verbose="Returning reference to auto variable">
    <location file="test.cpp" line="13"/>
  </error>
  </errors>
</results>'''

xml_error_no_location = '''\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
  <cppcheck version="1.54"/>
  <errors>
  <error id="missingInclude" severity="information" msg="Cppcheck cannot find all the include files (use --check-config for details)" verbose="Cppcheck cannot find all the include files. Cppcheck can check the code without the include files found. But the results will probably be more accurate if all the include files are found. Please check your project's include directories and add all of them as include directories for Cppcheck. To see what files Cppcheck cannot find use --check-config.">
  </error>
  </errors>
</results>'''

xml_multiple_errors = '''\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
  <cppcheck version="1.54"/>
  <errors>
  <error id="returnReference" severity="error" msg="Returning reference to auto variable" verbose="Returning reference to auto variable">
    <location file="test.cpp" line="14"/>
  </error>
  <error id="unreadVariable" severity="style" msg="Variable 'i' is assigned a value that is never used" verbose="Variable 'i' is assigned a value that is never used">
    <location file="test.cpp" line="27"/>
  </error>
  <error id="stlcstr" severity="error" msg="Dangerous usage of c_str(). The returned value by c_str() is invalid after this call." verbose="Dangerous usage of c_str(). The c_str() return value is only valid until its string is deleted.">
    <location file="test.cpp" line="21"/>
  </error>
  <error id="unusedFunction" severity="style" msg="The function 'dsfsdf' is never used" verbose="The function 'dsfsdf' is never used">
    <location file="test.cpp" line="24"/>
  </error>
  <error id="unusedFunction" severity="style" msg="The function 'foo' is never used" verbose="The function 'foo' is never used">
    <location file="test.cpp" line="11"/>
  </error>
  <error id="missingInclude" severity="information" msg="Cppcheck cannot find all the include files (use --check-config for details)" verbose="Cppcheck cannot find all the include files. Cppcheck can check the code without the include files found. But the results will probably be more accurate if all the include files are found. Please check your project's include directories and add all of them as include directories for Cppcheck. To see what files Cppcheck cannot find use --check-config.">
  </error>
  </errors>
</results>'''

xml_bad = '''\
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
'''


class TestCppCheck(steps.BuildStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpBuildStep()

    def tearDown(self):
        return self.tearDownBuildStep()

    def test_success(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_no_errors)
            + 0)
        self.expectOutcome(result=SUCCESS, status_text=['CppCheck'])
        self.expectLogfile("cppcheck.xml", xml_no_errors)
        self.expectProperty("warnings-count", 0)
        return self.runStep()

    def test_one_error(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_one_error)
            + 0)
        self.expectOutcome(result=WARNINGS, status_text=['CppCheck', 'warnings'])
        self.expectLogfile("cppcheck.xml", xml_one_error)
        self.expectLogfile("warnings (1)", "test.cpp:13 returnReference error Returning reference to auto variable\n")
        self.expectProperty("warnings-count", 1)
        return self.runStep()

    def test_one_error_no_location(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_error_no_location)
            + 0)
        self.expectOutcome(result=WARNINGS, status_text=['CppCheck', 'warnings'])
        self.expectLogfile("cppcheck.xml", xml_error_no_location)
        self.expectLogfile("warnings (1)", " missingInclude information Cppcheck cannot find all the include files (use --check-config for details)\n")
        self.expectProperty("warnings-count", 1)
        return self.runStep()
    
    def test_one_error_verbose(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.'], verbose=True))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_error_no_location)
            + 0)
        self.expectOutcome(result=WARNINGS, status_text=['CppCheck', 'warnings'])
        self.expectLogfile("cppcheck.xml", xml_error_no_location)
        self.expectLogfile("warnings (1)", " missingInclude information Cppcheck cannot find all the include files. Cppcheck can check the code without the include files found. But the results will probably be more accurate if all the include files are found. Please check your project's include directories and add all of them as include directories for Cppcheck. To see what files Cppcheck cannot find use --check-config.\n")
        self.expectProperty("warnings-count", 1)
        return self.runStep()

    def test_multiple_errors(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_multiple_errors)
            + 0)
        self.expectOutcome(result=WARNINGS, status_text=['CppCheck', 'warnings'])
        self.expectLogfile("cppcheck.xml", xml_multiple_errors)
        self.expectLogfile("warnings (6)", textwrap.dedent("""\
                test.cpp:14 returnReference error Returning reference to auto variable
                test.cpp:27 unreadVariable style Variable 'i' is assigned a value that is never used
                test.cpp:21 stlcstr error Dangerous usage of c_str(). The returned value by c_str() is invalid after this call.
                test.cpp:24 unusedFunction style The function 'dsfsdf' is never used
                test.cpp:11 unusedFunction style The function 'foo' is never used
                 missingInclude information Cppcheck cannot find all the include files (use --check-config for details)
                """))
        self.expectProperty("warnings-count", 6)
        return self.runStep()

    def test_failure(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_no_errors)
            + 1)
        self.expectOutcome(result=FAILURE, status_text=['CppCheck', 'failed'])
        return self.runStep()

    def test_bad_xml(self):
        self.setupStep(cppcheck.CppCheck(args=['--enable=all', '.']))
        self.expectCommands(
            ExpectShell(workdir='wkdir', command=['cppcheck', '--xml-version=2', '--enable=all', '.'])
            + ExpectShell.log('stdio',
                stdout='Checking main.cpp...\n',
                stderr=xml_bad)
            + 0)
        self.expectOutcome(result=FAILURE, status_text=['CppChecking'])
        return self.runStep()

