# RobotFramework Testrail

This repo has been forked from https://travis-ci.org/peterservice-rnd/robotframework-testrail
Refactoring had to be made to allow this plugin to work with TestRail version **v7.5.1.7004**. Additional features added include begin able to pass variables through via a robot framework--variable file and also a module which allows us to create test runs automatically.

Short Description
---  

[Robot Framework](http://www.robotframework.org) library, listener and pre-run modifiers for working with TestRail.

Installation
---  
Add to your project's requirements file:


    git+https://github.com/Smarsh/robotframework-testrail@master

Run

    pip install -r {path_to_requirements_file}

## Configuring Robot Test Cases
This plugin links tests in your Robot Framework suites to TestRail test cases by tags. Each TestRail Test Case has a unique ID which we tag in a corresponding Robot Framework test cases using the following format in a Robot tag:

    testcaseid={test_case_id_value}
E.g a test case exists in TestRail with the ID = 83920
The corresponding automated test representing this test case in Robot Framework should be tagged as follows

    ***Tests***
    Example Test
      [Tags]	testcaseid=83920

JIRA defect(s)/bug(s) in our Robot Tests can also be added as tags. Defects will be added in the Defects field in TestRail when TestRail test case results are added follow a Robot test run. One or more defects can be tagged as follows:

    defects={defect id(s)}

E.g test case exists in TestRail

    ***Tests***
    Example Test
      [Tags]	testcaseid=83920	defects=EG-123,EG-321


Modules
---

**TestRailCreateRun**

- Used as a robot --prerunmodifier
- Creates a test run in testrail which includes cases for tests which will be executed for a given robot command
- Tests can be filtered using the --include/-i tagging option in the robot command
- Tests can be filtered using the --exclude/-i tagging option in the robot command

**TestRailExecuteTestRun**

- Used as robot --prerunmodifier
- Runs robot suites/test cases based on cases present in a testrail run

**TestRailListener**

- Used as a robot --listener
- Updates a TestRail test run with results from a robot test run


# Configuration


Each module can be configured in the command line or in a python variable file passed to robot.


## TestRailCreateRun


Once the test run has been created the TestRail test run ID will be written to the `testRail.yml` file


***Arguments***:
- *server*: name of TestRail server (string) *required
- *protocol*: http/https (string) *required
- *user*: TestRail username (string) *required
- *password*: TestRail API Key (string) *required
- *projectId*: ID of the Testrail project to create the test run in (int) *required
- *testRunTitlePrefix*: Prefix to add to the title/name of the test run (string) *optional

***Set Variables in the command line***

    robot --prerunmodifier TestRailCreateRun:{server}:{user}:{password}:{protocol}:{projectId}:{testRunTitlePrefix} -i includedTags -e excludedTags path/to/tests/*

***Set Variables in a variable file***

variable file named `testRailConfig.py`:

    TESTRAIL_CLIENT_PROTOCOL = '{protocol}'  
    TESTRAIL_CLIENT_SERVER = '{server}'  
    TESTRAIL_CLIENT_USER = '{user}'  
    TESTRAIL_CLIENT_PASSWORD = '{password}'  
    TESTRAIL_PROJECT_ID = {projectId}  
    TESTRAIL_RUN_TITLE_PREFIX = 'robot_'  

Insert testRailConfig into robot command:

    robot --prerunmodifier TestRailCreateRun --variableFile testRailConfig.py -i includedTags -e excludedTags path/to/tests*

***Command Examples***

    robot --prerunmodifier TestRailCreateRun --variableFile testRailConfig.py -i includedTags -e excludedTags path/to/tests*

Will create a test run in the provided TestRail project which contains tests from robot suites in the path/to/tests* directories which have a testrailid tag, have a tag matching the includedTag but don't have the tag excluded tag.

    robot --prerunmodifier TestRailCreateRun --variableFile testRailConfig.py  path/to/tests*

Will create a test run in the provided TestRail project which contains all tests from robot suites in the path/to/tests* directories which have a testrailid tag

## TestRailExecuteTestRun

***Arguments***:

- *server*: name of TestRail server (string) *required
- *protocol*: http/ https (string) *required
- *user*: TestRail username (string) *required
- *password*: TestRail API Key (string) *required
- *run_id*: testRail run id (int) *optional
- *results_depth*: analysis depth of run results *optional
- *status_names*: name of test statuses in TestRail *optional



***Set Variables in the command line***

    robot --prerunmodifier TestRailExecuteTestRun:{server}:{user}:{password}:{protocol}:{results_depth}:{status1}:{status2} path/to/tests/*

***Set Variables in a variable file***

variable file named `testRailConfig.py`:

    TESTRAIL_CLIENT_PROTOCOL = '{protocol}'  
    TESTRAIL_CLIENT_SERVER = '{server}'  
    TESTRAIL_CLIENT_USER = '{user}'  
    TESTRAIL_CLIENT_PASSWORD = '{password}'  
    TESTRAIL_RUN_ID = {run_id}  
    RESULTS_DEPTH = '{results_depth}'
    CASE_STATUSES_TO_RUN = 'status1, status2'


Insert testRailConfig into robot command:

    robot --prerunmodifier TestRailExecuteTestRun --variableFile testRailConfig.py -i includedTags -e excludedTags path/to/tests*

***Command Examples***

    robot --prerunmodifier TestRailExecuteTestRun --variableFile testRailConfig.py path/to/tests*

Assuming we have test the TESTRAIL_RUN_ID variables in the testRailConfig.py file the tests from this run will be executed if the have a status which matches a status in the CASE_STATUSES_TO_RUN variable.

    robot --prerunmodifier TestRailCreateRun --prerunmodifier TestRailExecuteTestRun --variableFile testRailConfig.py path/to/tests*

Assuming we have **not** set a TESTRAIL_RUN_ID variable in the testRailConfig.py file. The TestRailCreateRun prerunmodifier will create a test run from all suites/tests in the path/to/tests* directories which have a testrailid tag. The run_id of this test run will be written to the `testRail.yml` file. The testRailExecuteTestRun will read the testRail.yml and pick up the run_id and then only run tests from this run.

## TestRailListener

***Arguments***
- *server*: name of TestRail server (string) *required
- *protocol*: http/ https (string) *required
- *user*: TestRail username (string) *required
- *password*: TestRail API Key (string) *required
- *run_id*: Testrail run Id (int) *optional
- *juggler_disable*: indicator to disable juggler logic; if exists, then juggler logic will be disabled (str) *optional - defaults to off
- *update*: indicator to update test case in TestRail; if exist, then test will be updated (str) *optional - defaults to off

***Set Variables in the command line***

    robot --listener TestRailListener:{server}:{user}:{password}:{protocol}:{run_id}:{juggler_disable}:{update} path/to/tests/*

***Set Variables in a variable file***

variable file named `testRailConfig.py`:

    TESTRAIL_CLIENT_PROTOCOL = '{protocol}'  
    TESTRAIL_CLIENT_SERVER = '{server}'  
    TESTRAIL_CLIENT_USER = '{user}'  
    TESTRAIL_CLIENT_PASSWORD = '{password}'  
    TESTRAIL_RUN_ID = {run_id}
    JUGGLER_DISABLE = '{juggler_disable}'
    UPDATE_TEST_CASES = '{update}'


Insert testRailConfig into robot command:

       robot --listener TestRailListener --variableFile testRailConfig.py path/to/tests/*
***Command Examples***


    robot --prerunmodifier TestRailCreateRun --prerunmodifier TestRailExecuteTestRun --listener TestRailListener --variableFile testRailConfig.py path/to/tests*

Assuming we have **not** set a TESTRAIL_RUN_ID variable in the testRailConfig.py file. The TestRailCreateRun prerunmodifier will create a test run from all suites/tests in the path/to/tests* directories which have a testrailid tag. The run_id of this test run will be written to the `testRail.yml` file. The testRailExecuteTestRun will read the testRail.yml and pick up the run_id and then only run tests from this run. The TestRailListener module will then update the test cases in TestRail with the results from the tests.

Original Readme Docs
[![Build Status](https://travis-ci.org/peterservice-rnd/robotframework-testrail.svg?branch=master)](https://travis-ci.org/peterservice-rnd/robotframework-testrail)

Short Description
---  

[Robot Framework](http://www.robotframework.org) library, listener and pre-run modifiers for working with TestRail.

Usage
---  

[How to enable TestRail API](http://docs.gurock.com/testrail-api2/introduction)



### TestRail Listener

Fixing of testing results and updating test cases.

#### Example

1. Create custom field "case_description" with type "text", which corresponds to the Robot Framework's test case documentation.

2. Create Robot test:

    ```robot  
*** Test Cases *** Autotest name [Documentation]    Autotest documentation [Tags]    testrailid=10    defects=BUG-1, BUG-2    references=REF-3, REF-4 Fail    Test fail message
 ```  
3. Run Robot Framework with listener:  
  
    ```  
 pybot --listener TestRailListener.py:testrail_server_name:tester_user_name:tester_user_password:run_id:https:update  robot_suite.robot ```  
  Test with case_id=10 will be marked as failed in TestRail with message "Test fail message" and defects "BUG-1, BUG-2".  
      
    Also title, description and references of this test will be updated in TestRail. Parameter "update" is optional.  
  
### TestRail Pre-run Modifier  
  
Pre-run modifier for starting test cases from a certain test run.  
  
#### Example  
  
1. Create Robot test:  
    ```robot  
 *** Test Cases *** Autotest name 1 [Documentation]    Autotest 1 documentation [Tags]    testrailid=10 Fail    Test fail message Autotest name 2 [Documentation]    Autotest 2 documentation [Tags]    testrailid=11 Fail    Test fail message  
 ```  
2. Run Robot Framework with pre-run modifier:

    ```  
pybot --prerunmodifier TestRailPreRunModifier:testrail_server_name:tester_user_name:tester_user_password:run_id:http:results_depth robot_suite.robot ```  
Only test cases that are included in the test run _run_id_ will be executed.

3. To execute tests from TestRail test run only with a certain status, for example "failed" and "blocked":

    ```  
pybot --prerunmodifier TestRailPreRunModifier:testrail_server_name:tester_user_name:tester_user_password:run_ind:http:results_depth:failed:blocked robot_suite.robot ```  
License
---  

Apache License 2.0