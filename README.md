noserunner 0.0.2
==========

runner based on python nose testing framework



### Dependency
    sudo pip install nose
    
### Help
    $ cd noserunner
    $ python runtests.py -h
  
### Command-line
    usage:
	python runtests.py [-h|--help] [--cycle CYCLE] [--duration DURATION_TIME] [--plan-file PLAN_FILE] [--livereport] [--livereport-config LIVE_REPORT_CONFIG] [--device-config DEVICE_CONFIG] [--verbosity VERBOSITY] [,[argv]]


    Process the paramters of runtests
    optional arguments:
	    -h, --help            Show this help message and exit

	    --cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle. Default is 1
	    
	    --plan-file PLAN      Set the absolute path or relative path of test plan file. If not provide this option. The "plan" file in current directory will be used as default

	    --duration DURATION   The maxumum test duration before ending the test.
					          Here format must follow next format: xxDxxHxxMxxS.
					          e.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds

	    --livereport          Enable the live report server feature. Default is disable
	    
        --livereport-config       Specify the path of the lieve report server configuration file.
                              If not provide this option. The "livereport.config" file in current directory will be used as default
                              
        --device-config       Specify the path of device configuration file.
                              If not provide this option. The "device.config" file in current directory will be used as default
                              
	    --verbosity           Default is 2. set the level(1~5) of verbosity to get the help string of every test and the result
	    
	    argv                  Additional arguments accepted by nose
	    
    e.g:
        run test with 10 cycles:
        $ python runtests.py --cycle 10
        
        run test with 2 days:
        $ python runtests.py --duration 2d
        
        run test with 10 cycles and expect to finish within 4 hours:
        $ python runtests.py --cycle 2 --duration 4h
        
        specify the location of test plan file:
        $ python runtests.py --cycle 10 --plan-file path_of_plan_file
        
        upload result to report server:
        $ python runtests.py --cycle 10 --livereport
        
        specify the config file location of the live report server and device: 
        $ python runtests.py --plan-file plan --cycle 10 --device-config device.config --livereport-config livereport.config --livereport
        
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

### Demo

    ├── client.py                                       #nose plugin module
    ├── planloader.py                                   #nose plugin module
    ├── reporter.py                                     #nose plugin module
    ├── makelog.py                                      #make an entire log file based on report folder
    ├── runtests.py                                     #launch script
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
    └── server.config                                   #config file (server, account, device...)
    ├── plan                                            #test case plan

