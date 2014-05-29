#!/usr/bin/python
# -*- coding:utf-8 -*- 
import os, time, sys, copy
from tools import AdbCommand
import ConfigParser
'''
script to generate device config file which need by report server
'''

CONFIG_BASIC = {'product': None, 'revision': None, 'deviceid': None, 'screen_width': None, 'screen_height': None}
DEFAULT_CONFIG_NAME = 'devconfig'
def show_usage():
    print 'usage:'
    print '\tpython makeconfig.py [-h|--help] <-s DEVICE_SERIAL_NUMBER> [-f CONFIG_FILE_NAME]\n\n'
    print 'Process the paramters of makeconfig'

    print 'optional arguments:'
    print '\t-h, --help                    Show this help message and exit\n'
    print '\t-s DEVICE_SERIAL_NUMBER       Set the device serial number list by adb devices\n'
    print '\t-f CONFIG_FILE_NAME           Set the name of config file which to be created\n'
    exit(1)

def getDevices():
    devices = {}
    ret = AdbCommand('adb devices', retry=2, timeout=5).run()
    if ret.find('List of devices attached') == -1:
        raise Exception('adb error: %s' % ret)
    _ = [i.strip() for i in ret.strip().split('\n')]
    _.remove('List of devices attached')
    if not _:
        return devices
    devices = dict([i.strip().split('\t') for i in _])
    return devices


def getDeviceProps(serial):
    #global CONFIG
    CONFIG = copy.copy(CONFIG_BASIC)
    CONFIG['deviceid'] = serial
    product = AdbCommand('adb -s %s shell getprop ro.product.device' % serial, retry=2, timeout=5).run()
    CONFIG['product'] = product.strip() if product else 'unknown'
    revision = AdbCommand('adb -s %s shell getprop ro.build.version.incremental' % serial, retry=2, timeout=5).run()
    CONFIG['revision'] = revision.strip() if revision else 'unknown'
    screen_size = AdbCommand('adb -s %s shell dumpsys display' % serial, retry=2, timeout=5).run()
    if not screen_size:
        CONFIG['screen_width'] = 'unknown'
        CONFIG['screen_height'] = 'unknown'
    else:
        display = screen_size.strip().split('\n')
        for i in display:
            if i.find('mBaseDisplayInfo') != -1:
                _ = i.strip().split(',')
                for __ in _:
                    if __.find('real') != -1:
                        ___ = __.strip().split()
                        ___.remove('real')
                        ___.remove('x')
                        CONFIG['screen_width'] , CONFIG['screen_height'] = ___
                        break
    return CONFIG


def createFile(config, target_file):
    p = ConfigParser.RawConfigParser()
    p.add_section('device')
    print 'device info:'
    for k, v in config.items():
        p.set('device', k, v)
        print '\t%s = %s' % (k, v)
    with open(target_file, 'w') as localfile:
        p.write(localfile)
    print 'device config file \'%s\' created successfully' % target_file

def createConfig(serial=None, target_file=None):
    devices = getDevices()
    if not devices:
        raise Exception('no device connected')
    if not serial:
        if len(devices) >= 2:
            raise Exception('multi devices connected. please specify serial number by \'-s\'')
        else:
            serial = devices.keys()[0]
            config_dict = getDeviceProps(serial)
            if not target_file:
                target_file = '%s.%s' % (serial, DEFAULT_CONFIG_NAME)
            createFile(config_dict, target_file)
    else:           
        if serial in devices.keys():
            if devices[serial] != 'device':
                raise Exception('device status error: %s' % devices[serial])
        else:
            raise Exception('device %s not connected' % serial)
        config_dict = getDeviceProps(serial)
        if not target_file:
            target_file = '%s.%s' % (serial, DEFAULT_CONFIG_NAME)
        createFile(config_dict, target_file)


if __name__ == '__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        show_usage()
    serial_no = None
    file_name = None
    if '-f' in sys.argv:
        index = sys.argv.index('-f')
        file_name = sys.argv[int(index)+1]

    if '-s' in sys.argv:
        index = sys.argv.index('-s')
        serial_no = sys.argv[int(index)+1]

    createConfig(serial=serial_no, target_file=file_name)
