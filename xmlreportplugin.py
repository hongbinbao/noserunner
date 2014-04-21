#!/usr/bin/python
# -*- coding:utf-8 -*- 
import nose
import xml.etree.ElementTree as ET
import sys


class XmlReporterPlugin(nose.plugins.Plugin):
    """
    Convert test result into xml format
    """
    name = 'xml-reporter'

    def __init__(self):
        super(XmlReporterPlugin, self).__init__()
        
    def options(self, parser, env):
        """ 
        Register commandline options.
        Called to allow plugin to register command line options with the parser. DO NOT return a value from this method unless you want to stop all other plugins from setting their options.        
        """
        super(XmlReporterPlugin, self).options(parser, env)

        parser.add_option("--xml-report-file", action="store", 
                          default="nose_report.xml", dest="file_name", help="File to output XML report to")
        
        parser.add_option("--xml-accumulate", action="store_true", 
                          dest="accumulate", default=True, help="Accumulate reults into report file, or start new")

    def configure(self, options, conf):
        """
        Called after the command  line has been parsed, with the parsed options and the config container. Here, implement any config storage or changes to state or operation that are set by command line options. DO NOT return a value from this method unless you want to stop all other plugins from being configured.
        """
        super(XmlReporterPlugin, self).configure(options, conf)
        if not self.enabled: return

        self.conf = conf
        self.opt = options
        
        self.reportFile = options.file_name
        self.accumulate = options.accumulate

    def _new_tree(self):
        """ Initialise a new tree """
        #sys.stderr.write('new-----\n')
        self.root = ET.Element("sets")
        self.tree = ET.ElementTree(self.root)
        
    def begin(self):
        """ If a file already exists and --xml-accumulate is set, we add into that, otherwise, create a new one """
        if self.accumulate:
            try:
                self.tree = ET.parse(self.reportFile)
                self.root = self.tree.getroot()
            except IOError:
                self._new_tree()
        else:
            self._new_tree()

    #Case fail
    def addFailure(self, test, err, capt=None, tbinfo=None):
        sys.stderr.write('Add Failure ..........\n')
        m, c, n = test.id().split('.')[-3:]
        e = ET.SubElement(self.root, "set")
        e.set("feature",m)
        e = ET.SubElement(e, "case")
        e.set("name", n)
        e.set("description", test.shortDescription())
        e.set("result","Fail")
        
    #Case error
    def addError(self, test, err, capt=None):
        m, c, n = test.id().split('.')[-3:]
        e = ET.SubElement(self.root, "set")
        e.set("feature",m)
        e = ET.SubElement(e, "case")
        e.set("name", n)
        #e.set("description", test.shortDescription())
        e.set("result","Error")

    #Case success
    def addSuccess(self, test, capt=None):
        m, c, n = test.id().split('.')[-3:]
        e = ET.SubElement(self.root, "set")
        e.set("feature",m)
        e = ET.SubElement(e, "case")
        e.set("name", n)
        e.set("description", test.shortDescription())
        e.set("result","Success")

    def finalize(self, result):
        """
        Write out report as serialized XML 
        """
        self.tree.write(self.reportFile)
