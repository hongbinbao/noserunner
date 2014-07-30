noserunner 1.0
==========

a test runner based on python nose testing framework. Used to load, parse, control test case sequence and generate test report.
support to specify test case execute order  in a good-readable plan file. support to define test case timeout value for each test method. support to fetch logcat/kmsg/snapshot from Android device  in real-time. Support to send the test result  to a remote HTTP server.


### Dependency

    sudo pip install nose

### Installation

    1: download the latest release from `[releases](https://github.com/hongbinbao/noserunner/releases/latest)`
    2: unzip it into an avaiable path of HOST
    
### Help

    $ cd noserunner
    $ python runtests.py -h
  
### Command-line
    usage:
	python runtests.py [-h|--help]
	                   [--cycle CYCLE]
	                   [--duration DURATION_TIME]
                           [--timeout TIMEOUT_VALUE_SECONDS]
	                   [--plan-file PLAN_FILE]
	                   [--livereport]
	                   [--server-config SERVER_CONFIG]
	                   [--client-config CLIENT_CONFIG]
	                   [--verbosity VERBOSITY]
	                   [,[argv]]


    Process the paramters of runtests
    optional arguments:
	    -h, --help            Show this help message and exit

	    --cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle Default is 1
	    
	    --plan-file PLAN      Set the absolute path or relative path of test plan file. If not provide this option. The "plan" file in current directory will be used as default

	    --duration DURATION   The maxumum test duration before ending the test.
					          Here format must follow next format: xxDxxHxxMxxS
					          e.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds

        --timeout SECONDS     The timeout specified in seconds to limit the maximum
                              period of test case method execution. The result of test method will be failure if the timeout exceeded. Default is 180 seconds 
                              
	    --livereport          Enable the live report server feature. Default is disable
	    
        --server-config       Specify the path of the lieve report server configuration file
                              If not provide this option. The "server.config" file in current directory will be used as default
                              
        --client-config       Specify the path of device configuration file
                              If not provide this option. The "client.config" file in current directory will be used as default
                              
	    --verbosity           Default is 2. set the level(1~5) of verbosity to get the help string of every test and the result
	    
	    argv                  Additional arguments accepted by nose
	    
    e.g:
        run test with 10 cycles:
        $ python runtests.py --cycle 10
        
        run test with 2 days and set each test method timeout value to be 360 seconds:
        $ python runtests.py --duration 2d --timeout 360
        
        run test with 10 cycles and expect to finish within 4 hours:
        $ python runtests.py --cycle 2 --duration 4h
        
        specify the location of test plan file:
        $ python runtests.py --cycle 10 --plan-file path_of_plan_file
        
        upload result to report server:
        $ python runtests.py --cycle 10 --livereport
        
        specify the config file location of the live report server and device: 
        $ python runtests.py --plan-file plan --cycle 10 --client-config device.config --server-config livereport.config --livereport
        
### TestCaseContext instance provided by nose plugin

    test case extends from unittest.TestCase is able to get TestCaseContext obj during nose run time.
     
    """
    def testMethod(self):
        ctx = self.contexts 
        user_log_dir_path = ctx.user_log_dir
        device_id = ctx.device_config['deviceid']
        
    """
    function test case is able to get TestCaseContext obj during nose run time.
     
    """
    def testMethod():
        ctx = contexts 
        user_log_dir_path = ctx.user_log_dir
        device_id = ctx.device_config['deviceid']
        
    """

### Make entire logcat log
    how to:
        python makelog.py --help

    e.g:
        python makelog.py -d path_of_report/2014-04-02_23:38:32 -f entire.log

### Make device config file
    '--device-config' option is enable as default. an available device config file MUST be required. device config file can be generated automatically by script.
    how to:
        python makeconfig.py --help
        
    e.g:
        python makeconfig.py -s serial_number -f server.config

### Demo

    ├── client.py                                       #nose plugin module
    ├── planloader.py                                   #nose plugin module
    ├── reporter.py                                     #nose plugin module
    ├── makelog.py                                      #make an entire log file based on report folder
    ├── makeconfig.py                                   #generate device config file
    ├── runtests.py                                     #launch script
    ├── tools.py                                        #unit library
    ├── scripts                                         #test case package
    │   ├── __init__.py
    │   ├── pics                                        #test case related sources
    │   │   ├── browser.BrowserTest.testOpenBrowser
    │   │   │   ├── baidu_logo.png
    │   │   │   └── baidu_logo.(x267y267w554h206).png
    │   │   └── phone.PhoneTest.testCall
    │   └── testcases                                   #unittest test case package
    │       ├── __init__.py 
    │       ├── browser.py                              #test case for browser
    │       ├── phone.py                                #test case for phone
    └── server.config                                   #server config file (server, account, device...)
    └── client.config                                   #device config file (serial number, product name, revision number...)
    ├── plan                                            #test case plan file
    ├── buildtest                                       #unit test package
    │   ├── planloader_test.py
    │   ├── reporter_test.py
    │   ├── resource
    │   │   ├── device.config
    │   │   ├── livereport.config
    │   │   ├── plan
    │   │   └── repeatplan
    │   └── ut.py


### unit test
    $ cd noserunner
    $ python buildtest/ut.py
