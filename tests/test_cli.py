import csv
import json
import sys
import tests

from collections import OrderedDict
from cStringIO import StringIO
from elex.cli.app import ElexApp

DATA_FILE = 'tests/data/20151103_national.json'
ELECTIONS_DATA_FILE = 'tests/data/00000000_elections.json'

TEST_COMMANDS = [
    'races',
    'candidates',
    'reporting-units',
    'candidate-reporting-units',
    'results',
]


class ElexCLICSVTestMeta(type):
    def __new__(mcs, name, bases, dict):
        def gen_test(command):
            """
            Dynamically generate a test function, like test_init_races
            """
            def test(self):
                cli_fields, cli_data = self._test_command(command=command)
                api_data = getattr(self, command.replace('-', '_'))
                api_fields = api_data[0].serialize().keys()
                self.assertEqual(cli_fields, api_fields)
                self.assertEqual(len(cli_data), len(api_data))
                for i, row in enumerate(cli_data):
                    for k, v in api_data[i].serialize().items():
                        if v is None:
                            v = ''
                        self.assertEqual(row[k], str(v))

            return test

        for command in TEST_COMMANDS:
            test_name = 'test_{0}'.format(command.replace('-', '_'))
            dict[test_name] = gen_test(command)

        return type.__new__(mcs, name, bases, dict)


class ElexCLICSVTestCase(tests.ElectionResultsTestCase):
    """
    This testing class is mostly dynamically generated by its metaclass.

    The goal of the CLI tests is to the make sure the CLI output matches the
    Python API. The API tests guarantee the validity of the data, while these
    tests guarantee the CLI provides the same data in CSV format.
    """
    __metaclass__ = ElexCLICSVTestMeta

    def test_elections_fields(self):
        fields, data = self._test_command(command='elections', datafile=ELECTIONS_DATA_FILE)
        self.assertEqual(fields, ['electiondate', 'liveresults', 'testresults'])

    def test_elections_length(self):
        fields, data = self._test_command(command='elections', datafile=ELECTIONS_DATA_FILE)
        self.assertEqual(len(data), 11)

    def test_elections_date(self):
        fields, data = self._test_command(command='elections', datafile=ELECTIONS_DATA_FILE)
        self.assertEqual(data[4]['electiondate'], '2015-08-04')

    def test_elections_liveresults(self):
        fields, data = self._test_command(command='elections', datafile=ELECTIONS_DATA_FILE)
        self.assertEqual(data[4]['liveresults'], 'False')

    def test_elections_testresults(self):
        fields, data = self._test_command(command='elections', datafile=ELECTIONS_DATA_FILE)
        self.assertEqual(data[4]['testresults'], 'True')

    def _test_command(self, command, datafile=DATA_FILE):
        """
        Execute an `elex` sub-command; returns fieldnames and rows
        """
        stdout_backup = sys.stdout
        sys.stdout = StringIO()

        app = ElexApp(argv=[command, '--data-file', datafile])

        app.setup()
        app.log.set_level('FATAL')
        app.run()

        lines = sys.stdout.getvalue().split('\n')
        reader = csv.DictReader(lines)

        sys.stdout.close()
        sys.stdout = stdout_backup

        return reader.fieldnames, list(reader)


class ElexCLIJSONTestMeta(type):
    def __new__(mcs, name, bases, dict):
        def gen_test(command):
            """
            Dynamically generate a test function, like test_init_races
            """
            def test(self):
                cli_fields, cli_data = self._test_command(command=command)
                api_data = getattr(self, command.replace('-', '_'))
                api_fields = api_data[0].serialize().keys()
                self.assertEqual(cli_fields, api_fields)
                self.assertEqual(len(cli_data), len(api_data))
                for i, row in enumerate(cli_data):
                    for k, v in api_data[i].serialize().items():
                        self.assertEqual(row[k], v)

            return test

        for command in TEST_COMMANDS:
            test_name = 'test_{0}'.format(command.replace('-', '_'))
            dict[test_name] = gen_test(command)

        return type.__new__(mcs, name, bases, dict)


class ElexCLIJSONTestCase(tests.ElectionResultsTestCase):
    """
    This testing class is mostly dynamically generated by its metaclass.

    The goal of the CLI tests is to the make sure the CLI output matches the
    Python API. The API tests guarantee the validity of the data, while these
    tests guarantee the CLI provides the same data in JSON format.
    """
    __metaclass__ = ElexCLIJSONTestMeta

    def _test_command(self, command, datafile=DATA_FILE):
        """
        Execute an `elex` sub-command; returns fieldnames and rows
        """
        stdout_backup = sys.stdout
        sys.stdout = StringIO()

        app = ElexApp(argv=[command, '--data-file', datafile, '-o', 'json'])

        app.setup()
        app.log.set_level('FATAL')
        app.run()

        json_data = sys.stdout.getvalue()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        sys.stdout.close()
        sys.stdout = stdout_backup

        return data[0].keys(), data
