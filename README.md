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
	python runtests.py [-h|--help] [--cycle CYCLE] [--reportserver]


    Process the paramters of runtests
    optional arguments:
	    -h, --help            Show this help message and exit

	    --cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle. Default is 1

	    --duration DURATION   The minumum test duration before ending the test.

					          Here format must follow next format: xxDxxHxxMxxS.

					          e.g. --duration=2D09H30M12S, which means 2 days, 09 hours, 30 minutes and 12 seconds

	    --reportserver        Enable the report server feature. Default is disable

	    --verbosity           Default is 2. set the level(1~5) of verbosity to get the help string of every test and the result

### TestCaseContext instance provided by nose plugin

    test case extends from unittest.TestCase is able to get TestCaseContext obj during nose run time.
     
    """
    def testMethod(self):
        ctx = self.contexts 
        user_log_dir_path = ctx.user_log_dir
        
    """
    function test case is able to get TestCaseContext obj during nose run time.
     
    """
    def testMethod():
        ctx = contexts 
        user_log_dir_path = ctx.user_log_dir
        
    """
    
### Demo

    ├── client.py                                       #nose plugin module
    ├── planloader.py                                   #nose plugin module
    ├── reporter.py                                     #nose plugin module
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

