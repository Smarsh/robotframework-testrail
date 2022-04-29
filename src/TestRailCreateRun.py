# -*- coding: utf-8 -*-

from concurrent.futures import TimeoutError
from requests.exceptions import RequestException
from robot.api import SuiteVisitor, TestSuite
from robot.output import LOGGER
from robot.run import RobotFramework
import sys
from TestRailAPIClient import TestRailAPIClient
from VariableFileParser import VariableFileParser
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONNECTION_TIMEOUT = 60  # Value in seconds of timeout connection with testrail for one request


class TestRailCreateRun(SuiteVisitor):
    """ This module can be used in as a --prerunmodifier option when executing the robot command to create a test run
    in test rail based on tests that run according to tests which are set to be included or excluded by tagging
    in the robot command.

    Configuration for this module can be specified as positional arguments in the robot command
    e.g robot --prerunmodifier TestRailCreateRun:myserver.com:user@email.com:password:https:1:robot_ robot_tests_dir/*

    or configuration can be done in a variable file
    e.g robot --prerunmodifier TestRailCreateRun --variableFile myVars.py

    Where myVars.py looks like:
    TESTRAIL_CLIENT_PROTOCOL = 'https'
    TESTRAIL_CLIENT_SERVER = 'myServer.com'
    TESTRAIL_CLIENT_USER = 'user@email.com'
    TESTRAIL_CLIENT_PASSWORD = 'password'
    TESTRAIL_PROJECT_ID = 1
    TESTRAIL_RUN_TITLE_PREFIX = 'robot_'

    The TestRail run title prefix is optional and defaults to robot_.
    The Testrail Client password should be a users API key.
    """

    def __init__(self, server: str = None, user: str = None, password: str = None, protocol: str = None,
                 projectId: str = None, testRunTitlePrefix: str = 'robot_') -> None:
        """Pre-run modifier initialization.

        *Args:*\n
            All module args are optional as they can be set as a var in a --variablefile\n.
            _server_ - name of TestRail server (set in --variablefile as TESTRAIL_CLIENT_SERVER);\n
            _user_ - name of TestRail user (set in --variablefile as TESTRAIL_CLIENT_USER);\n
            _password_ - password of TestRail user (set in --variablefile as TESTRAIL_CLIENT_PASSWORD);\n
            _protocol_ - connecting protocol to TestRail server (set in --variablefile as TESTRAIL_CLIENT_PROTOCOL): http or https;\n
            project_id_ - ID of project in testrail to create Test Run in (set in --variablefile as TESTRAIL_PROJECT_ID);\n
            run_title_prefix_ - (Optional)
        """
        # Get the command line options passed to the robot command
        options, arguments = RobotFramework().parse_arguments(sys.argv[1:])

        # if the command line arguments are provided
        if server is not None:
            self._protocol = protocol
            self._server = server
            self._user = user
            self._password = password
            self.project_id = projectId
            self.run_title_prefix = testRunTitlePrefix
        # if the command line arguments are not provided look for them in the variablefile(s)
        else:
            variable_file_settings = VariableFileParser(options)
            self._protocol = variable_file_settings.protocol
            self._server = variable_file_settings.server
            self._user = variable_file_settings.user
            self._password = variable_file_settings.password
            self.project_id = variable_file_settings.projectId
            self.run_title_prefix = variable_file_settings.runTitlePrefix

        # raise errors if the necessary variable cannot be found
        if self._protocol is None: raise NameError('variable not defined as arg or in variablefile --> TESTRAIL_CLIENT_PROTOCOL')
        if self._server is None: raise NameError('variable not defined as arg or in variablefile --> TESTRAIL_CLIENT_SERVER')
        if self._user is None: raise NameError('variable not defined as arg or in variablefile --> TESTRAIL_CLIENT_USER')
        if self._password is None: raise NameError('variable not defined as arg or in variablefile --> TESTRAIL_CLIENT_PASSWORD')
        if self.project_id is None: raise NameError('variable not defined as arg or in variablefile --> TESTRAIL_PROJECT_ID')

        # get the included and excluded tags from the robot command options
        self.robot_option_included_tags, self.robot_options_excluded_tags = self.get_robot_option_tags(options)

        # instantiate the test rail api client
        self.tr_client = TestRailAPIClient(self._server, self._user, self._password, 0, self._protocol)
        LOGGER.register_syslog()

        test_run_title = self.run_title_prefix + "_" + datetime.now().strftime("%d-%m-%YT%H:%M:%S")

        self.run_id = str(self.tr_client.add_test_run(self.project_id, test_run_title)['id'])

        # store the run ID in a configuration file
        with open('testRail.yml', 'w') as filetowrite:
            filetowrite.write('[DEFAULT]')
            filetowrite.write('\nTESTRAIL_RUN_ID = '+self.run_id)

    def get_robot_option_tags(self, options: dict):
        included_tags = []
        excluded_tags = []
        if 'include' in options: included_tags = options['include']
        if 'exclude' in options: excluded_tags = options['exclude']
        return included_tags, excluded_tags

    def get_test_rail_ids(self, testcase):
        test_rail_ids = []
        for tag in testcase.tags:
            if 'testrailid=' in str(tag).lower():
                tr_id = str(tag).lower().split('=')[1]
                if tr_id.isdigit():
                    test_rail_ids.append(int(tr_id))
                else:
                    raise TypeError(tr_id+" cannot be converted to int type")
        if len(test_rail_ids) > 0:
            return test_rail_ids
        return None

    def does_testcase_contain_tag(self, testcase, tag):
        for testcase_tag in testcase.tags:
            if str(tag).lower() in str(testcase_tag).lower():
                return True
        return False

    def _log_to_parent_suite(self, suite: TestSuite, message: str) -> None:
        """Log message to the parent suite.

        *Args:*\n
            _suite_ - Robot Framework test suite object.
            _message_ - message.
        """
        if suite.parent is None:
            LOGGER.error("{suite}: {message}".format(suite=suite, message=message))

    def get_list_of_test_ids_in_testrail_run(self, run_id : str):
        response = self.tr_client.get_tests_from_test_run(run_id)
        test_ids = []
        for test in response['tests']:
            test_ids.append(test['case_id'])
        return test_ids


    def end_suite(self, suite: TestSuite) -> None:
        """This function overrides the default behaviour of the end_suite function allowing us to access test suite
        information before to execution of tests.

        This function iterates over each test in each suite and identifies which tests contain tags which should be
        included in test execution.

        - tests must contain a testrailid to be considered for inclusion in TestRail run creation
        - if a test contains tags matching an --include tag and a testrail id the tag will be added to a list of test
        cases to add to a TestRail run.
        - if a test contains tags matching an --exclude tag it will be removed from the list of test cases to add to a
        TestRail run.
        - if no --include tags exist then all test cases with a testrail id will be added to the list but removed if
        test case tags match an --exclude tag.

        Once tags are processed we then add thm to the testrail run.

        *Args:*\n
             _suite_ - Robot Framework test suite object.
        """
        LOGGER.debug("Starting to end suite")
        case_id_list = []
        # loop through test cases in tests
        for testcase in suite.tests:
            # get case Ids associated with a test
            cases_ids = self.get_test_rail_ids(testcase)

            # if the there are case Ids in the robot test
            if cases_ids:
                # if there are --included tags in the robot command
                if len(self.robot_option_included_tags) > 0:
                    # then loop through the --included tags
                    for tag in self.robot_option_included_tags:
                        # if there is a match for a testcase tag and --included tag
                        if self.does_testcase_contain_tag(testcase, tag):
                            # add the case ids to the list of testcase ids
                            case_id_list.extend(cases_ids)
                            # no need to continue looping through the --included tags
                            break
                # if there are no --included tags then just add all the case IDs
                else:
                    case_id_list.extend(cases_ids)
                # loop through --excluded tags in the robot command
                if len(self.robot_options_excluded_tags) > 0:
                    for excl_tag in self.robot_options_excluded_tags:
                        # if the test case contains an excluded tag
                        if self.does_testcase_contain_tag(testcase, excl_tag):
                            # loop through the test case testrail IDs
                            for case_id in cases_ids:
                                # if the case Id is in the list then remove
                                while case_id in case_id_list: case_id_list.remove(case_id)
                        # no need to do any if the test case doesn't contain excluded tag
            # if there are no cases IDs then no need to add or exclude any test cases

        try:
            # if there is any case ID's to add to testrail from this suite
            if len(case_id_list) > 0:
                # get existing test ids in testrail run
                existing_case_ids = self.get_list_of_test_ids_in_testrail_run(self.run_id)

                changedList = False
                for listed_case_id in case_id_list:
                    if listed_case_id not in existing_case_ids:
                        existing_case_ids.append(listed_case_id)
                        changedList = True

                if changedList:
                    self.tr_client.add_test_case_to_run(self.run_id, existing_case_ids)

        except (RequestException, TimeoutError) as error:
            self._log_to_parent_suite(suite, str(error))
