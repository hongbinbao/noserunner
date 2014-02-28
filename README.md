noserunner
==========

runner based on python nose testing framework



### Dependency
    sudo pip install nose
    
### Help
    $ cd noserunner
    $ python runtests.py -h
  
### Command-line
    python runtests.py [-h|--help] [--cycle CYCLE] [--reportserver]

    Process the paramters of runtests
    optional arguments:
	  -h, --help            Show this help message and exit

	  --cycle CYCLE         Set the number(int) of cycle. Execute test with a specified number of cycle. Default is 1

	  --reportserver        Enable the report server feature. Default is disable


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

