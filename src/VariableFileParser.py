import configparser


class VariableFileParser(object):

    def __init__(self, cliOptions: dict) -> None:
        self.sectionName = 'DEFAULT'
        self.password = None
        self.user = None
        self.server = None
        self.protocol = None
        self.projectId = None
        self.runId = None
        self.runTitlePrefix = None
        self.testPlanId = None

        if 'variablefile' in cliOptions:
            variableFiles = cliOptions['variablefile']
            for varFilePath in variableFiles:
                parser = configparser.ConfigParser()
                with open(varFilePath) as stream:
                    parser.read_string('['+self.sectionName+"]\n" + stream.read())
                    self.password = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_CLIENT_PASSWORD')
                    self.user = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_CLIENT_USER')
                    self.server = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_CLIENT_SERVER')
                    self.protocol = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_CLIENT_PROTOCOL')
                    self.projectId = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_PROJECT_ID')
                    self.runId = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_RUN_ID')
                    self.runTitlePrefix = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_RUN_TITLE_PREFIX')
                    self.testPlanId = self.getVariableFromConfig(parser, self.sectionName, 'TESTRAIL_TEST_PLAN_ID')
                    self.resultsDepth = self.getResultsDepthFromConfig(parser, self.sectionName)
                    self.statuses = self.getTupleFromConfig(parser, self.sectionName, 'CASE_STATUSES_TO_RUN')
                    self.suiteId = self.getVariableFromConfig(parser,self.sectionName, 'TESTRAIL_SUITE_ID')
                    self.updateTestCases = self.getVariableFromConfig(parser, self.sectionName, 'UPDATE_TEST_CASES')
                    self.jugglerDisable = self.getVariableFromConfig(parser, self.sectionName, 'JUGGLER_DISABLE')

    def getVariableFromConfig(self, parser, sectionName: str, variableName: str):
        if parser.has_option(sectionName, variableName):
            return str(parser.get(sectionName, variableName)).replace('"', '').replace("'", "")
        else:
            return None

    def getResultsDepthFromConfig(self, parser, sectionName: str):
        if parser.has_option(sectionName, 'RESULTS_DEPTH'):
            results_depth = str(self.getVariableFromConfig(parser, sectionName, 'RESULTS_DEPTH'))
            return int(results_depth) if results_depth.isdigit() else None
        return 0

    def getTupleFromConfig(self,parser, sectionName: str, variableName: str):
        if parser.has_option(sectionName, variableName):
            return tuple(parser.get(sectionName, variableName).replace(" ","").split(","))
        else:
            return None
