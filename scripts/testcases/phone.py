#!/usr/bin/python
# -*- coding:utf-8 -*- 
import unittest
from uiautomator import device as d

class Phone(unittest.TestCase):
    def setUp(self):
        super(Phone, self).setUp()
        d.wakeup()

    def tearDown(self):
        super(Phone, self).tearDown()

    
    def testCall(self):
        import time
        #d.sleep(9)
        assert 0, 'phone failure'
        assert d.exists(text='Phone') , 'Phone app not appear on home screen'
        d(text='Phone').click.wait()
        d(description='one').click()
        d(description='zero').click()
        d(description='zero').click()
        d(description='eight').click()
        d(description='six').click()
        assert d.exists(text="10086")
        if d.exists(description='dial'):
            d(description='dial').click.wait()
        assert d(text="Dialing").wait.exists(timeout=5000), 'call not connected in 10 secs'
        assert d(text="0:10").wait.exists(timeout=20000), 'call duration should be 10 secs'
        d(className='android.widget.Button', index=1).click.wait()
        assert d(description='dial').wait.exists(timeout=3000)



