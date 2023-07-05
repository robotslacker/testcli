# -*- coding: UTF-8 -*-
from collections import defaultdict
import xml.etree.ElementTree as xmlEt
from six import iteritems


class TestSuite(object):
    """
    Suite of test cases.
    Can handle unicode strings or binary strings if their encoding is provided.
    """

    def __init__(
        self,
        name,
        testcases=None,
        hostname=None,
        suiteId=None,
        package=None,
        timestamp=None,
        properties=None,
        file=None,
        log=None,
        url=None,
        stdout=None,
        stderr=None,
    ):
        self.name = name
        if not testcases:
            testcases = []
        try:
            iter(testcases)
        except TypeError:
            raise TypeError("test_cases must be a list of test cases")
        self.test_cases = testcases
        self.timestamp = timestamp
        self.hostname = hostname
        self.id = suiteId
        self.package = package
        self.file = file
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr
        self.properties = properties

    def build_xml_doc(self):
        """
        Builds the XML document for the JUnit test suite.
        Produces clean unicode strings and decodes non-unicode with the help of encoding.
        @return: XML document with unicode string elements
        """

        # build the test suite element
        test_suite_attributes = dict()
        if any(c.assertions for c in self.test_cases):
            test_suite_attributes["assertions"] = str(sum([int(c.assertions) for c in self.test_cases if c.assertions]))
        test_suite_attributes["disabled"] = str(len([c for c in self.test_cases if not c.is_enabled]))
        test_suite_attributes["errors"] = str(len([c for c in self.test_cases if c.is_error()]))
        test_suite_attributes["failures"] = str(len([c for c in self.test_cases if c.is_failure()]))
        test_suite_attributes["name"] = self.name
        test_suite_attributes["skipped"] = str(len([c for c in self.test_cases if c.is_skipped()]))
        test_suite_attributes["tests"] = str(len(self.test_cases))
        test_suite_attributes["time"] = str(sum(c.elapsed_sec for c in self.test_cases if c.elapsed_sec))

        if self.hostname:
            test_suite_attributes["hostname"] = self.hostname
        if self.id:
            test_suite_attributes["id"] = self.id
        if self.package:
            test_suite_attributes["package"] = self.package
        if self.timestamp:
            test_suite_attributes["timestamp"] = self.timestamp
        if self.file:
            test_suite_attributes["file"] = self.file
        if self.log:
            test_suite_attributes["log"] = self.log
        if self.url:
            test_suite_attributes["url"] = self.url

        xml_element = xmlEt.Element("testsuite", test_suite_attributes)

        # add any properties
        if self.properties:
            props_element = xmlEt.SubElement(xml_element, "properties")
            for k, v in self.properties.items():
                attrs = {"name": k, "value": v, }
                xmlEt.SubElement(props_element, "property", attrs)

        # add test suite stdout
        if self.stdout:
            stdout_element = xmlEt.SubElement(xml_element, "system-out")
            stdout_element.text = self.stdout

        # add test suite stderr
        if self.stderr:
            stderr_element = xmlEt.SubElement(xml_element, "system-err")
            stderr_element.text = self.stderr

        # test cases
        for case in self.test_cases:
            test_case_attributes = dict()
            test_case_attributes["name"] = case.name
            if case.assertions:
                # Number of assertions in the test case
                test_case_attributes["assertions"] = "%d" % case.assertions
            if case.elapsed_sec:
                test_case_attributes["time"] = "%f" % case.elapsed_sec
            if case.timestamp:
                test_case_attributes["timestamp"] = case.timestamp
            if case.classname:
                test_case_attributes["classname"] = case.classname
            if case.status:
                test_case_attributes["status"] = case.status
            if case.category:
                test_case_attributes["class"] = case.category
            if case.file:
                test_case_attributes["file"] = case.file
            if case.line:
                test_case_attributes["line"] = case.line
            if case.log:
                test_case_attributes["log"] = case.log
            if case.url:
                test_case_attributes["url"] = case.url

            test_case_element = xmlEt.SubElement(xml_element, "testcase", test_case_attributes)

            # failures
            for failure in case.failures:
                if failure["output"] or failure["message"]:
                    attrs = {"type": "failure"}
                    if failure["message"]:
                        attrs["message"] = failure["message"]
                    if failure["type"]:
                        attrs["type"] = failure["type"]
                    failure_element = xmlEt.Element("failure", attrs)
                    if failure["output"]:
                        failure_element.text = failure["output"]
                    test_case_element.append(failure_element)

            # errors
            for error in case.errors:
                if error["message"] or error["output"]:
                    attrs = {"type": "error"}
                    if error["message"]:
                        attrs["message"] = error["message"]
                    if error["type"]:
                        attrs["type"] = error["type"]
                    error_element = xmlEt.Element("error", attrs)
                    if error["output"]:
                        error_element.text = error["output"]
                    test_case_element.append(error_element)

            # skippeds
            for skipped in case.skipped:
                attrs = {"type": "skipped"}
                if skipped["message"]:
                    attrs["message"] = skipped["message"]
                skipped_element = xmlEt.Element("skipped", attrs)
                if skipped["output"]:
                    skipped_element.text = skipped["output"]
                test_case_element.append(skipped_element)

            # test stdout
            if case.stdout:
                stdout_element = xmlEt.Element("system-out")
                stdout_element.text = case.stdout
                test_case_element.append(stdout_element)

            # test stderr
            if case.stderr:
                stderr_element = xmlEt.Element("system-err")
                stderr_element.text = case.stderr
                test_case_element.append(stderr_element)

        return xml_element

    @staticmethod
    def to_xml_string(test_suites):
        try:
            iter(test_suites)
        except TypeError:
            raise TypeError("test_suites must be a list of test suites")

        xml_element = xmlEt.Element("testsuites")
        attributes = defaultdict(int)
        for test_suite in test_suites:
            ts_xml = test_suite.build_xml_doc()
            for key in ["disabled", "errors", "failures", "tests"]:
                attributes[key] += int(ts_xml.get(key, 0))
            for key in ["time"]:
                attributes[key] += float(ts_xml.get(key, 0))
            xml_element.append(ts_xml)
        for key, value in iteritems(attributes):
            xml_element.set(key, str(value))
        xml_string = str(xmlEt.tostring(xml_element, encoding="utf-8").decode("utf-8"))

        return xml_string


class TestCase(object):
    """A JUnit test case with a result and possibly some stdout or stderr"""

    def __init__(
        self,
        name,
        classname=None,
        elapsed_sec=None,
        stdout=None,
        stderr=None,
        assertions=None,
        timestamp=None,
        status=None,
        category=None,
        file=None,
        line=None,
        log=None,
        url=None,
        allow_multiple_subelements=False,
    ):
        self.name = name
        self.assertions = assertions
        self.elapsed_sec = elapsed_sec
        self.timestamp = timestamp
        self.classname = classname
        self.status = status
        self.category = category
        self.file = file
        self.line = line
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr

        self.is_enabled = True
        self.errors = []
        self.failures = []
        self.skipped = []
        self.allow_multiple_subalements = allow_multiple_subelements

    def add_error_info(self, message=None, output=None, error_type=None):
        """Adds an error message, output, or both to the test case"""
        error = {"message": message, "output": output, "type": error_type}
        if self.allow_multiple_subalements:
            if message or output:
                self.errors.append(error)
        elif not len(self.errors):
            self.errors.append(error)
        else:
            if message:
                self.errors[0]["message"] = message
            if output:
                self.errors[0]["output"] = output
            if error_type:
                self.errors[0]["type"] = error_type

    def add_failure_info(self, message=None, output=None, failure_type=None):
        """Adds a failure message, output, or both to the test case"""
        failure = {"message": message, "output": output, "type": failure_type}
        if self.allow_multiple_subalements:
            if message or output:
                self.failures.append(failure)
        elif not len(self.failures):
            self.failures.append(failure)
        else:
            if message:
                self.failures[0]["message"] = message
            if output:
                self.failures[0]["output"] = output
            if failure_type:
                self.failures[0]["type"] = failure_type

    def add_skipped_info(self, message=None, output=None):
        """Adds a skipped message, output, or both to the test case"""
        skipped = {"message": message, "output": output}
        if self.allow_multiple_subalements:
            if message or output:
                self.skipped.append(skipped)
        elif not len(self.skipped):
            self.skipped.append(skipped)
        else:
            if message:
                self.skipped[0]["message"] = message
            if output:
                self.skipped[0]["output"] = output

    def is_failure(self):
        """returns true if this test case is a failure"""
        return sum(1 for f in self.failures if f["message"] or f["output"]) > 0

    def is_error(self):
        """returns true if this test case is an error"""
        return sum(1 for e in self.errors if e["message"] or e["output"]) > 0

    def is_skipped(self):
        """returns true if this test case has been skipped"""
        return len(self.skipped) > 0


if __name__ == '__main__':
    xx = TestCase(
        name='Test1',
        classname='some.class.name',
        elapsed_sec=0,
        stdout='I am stdout!',
        stderr='I am stderr!')
    xx.add_failure_info(message="abcd\r\ndexfg中国人民解放军")
    test_cases = [xx]
    ts = TestSuite("my test suite", test_cases)
    # pretty printing is on by default but can be disabled using prettyprint=False
    print(TestSuite.to_xml_string([ts]))