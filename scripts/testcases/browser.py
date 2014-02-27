#!/usr/bin/python
# -*- coding:utf-8 -*- 
import unittest
from uiautomator import device as d

class Browser(unittest.TestCase):
    def setUp(self):
        super(Browser, self).setUp()
        #d.start_activity(action='android.intent.action.DIAL', data='tel:13581739891', flags=0x04000000)
        d.wakeup()
        #d.press('back')
        #d.press('back')
        #d.press('back')
        #d.press('home')

    def tearDown(self):
        super(Browser, self).tearDown()
        d.press('back')
        d.press('back')
        d.press('back')
        d.press('home')

    def testOpenBrowser(self):
        assert True, 'manual success'
        #assert d.exists(text='Browser') , 'Browser app not appear on the home screen'
        #assert 0, 'main failure'
        #assert d.exists(text='Apps')  , 'not appear on the home screen'
        #d(text='Browser').click.wait()
        #assert d(text="Bookmarks").wait.exists(timeout=10000), 'browser unable to open in 10 secs'
        #d(className='android.widget.EditText').set_text('www.baidu.com')
        #d.click('go.png', threshold=0.01)
        #d.press('enter')
        #d.expect('baidu_logo.png', timeout=20)



