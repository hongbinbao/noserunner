import requests
import StringIO
import zipfile
import logging
from uuid import uuid1
from ConfigParser import ConfigParser
import json, hashlib, math, time, threading, sys, os
from os.path import dirname, abspath, join, exists, splitext, split
from threading import Thread
REPORT_TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
AUTH_REQ_TIMEOUT = 3
REQ_TIMEOUT = 3

logging.getLogger("requests").setLevel(logging.WARNING)
###authentication###
#method: POST
#request URI      : http://ats.borqs.com/smartapi/account/login
#request header   : Content-Type: 'application/json', 'Accept': 'application/json'
#request payload  : {'subc': 'login',
#                   'data': {appid': 01, 'username': username, 'password': pwd}

#response payload : {'result': ok|error, 'data': {'token': token}, 'msg': log_error}





###test session create###
#method: POST
#request URI      : http://ats.borqs.com/smartapi/group/<group_id>/test/<session_id>/create
#request header   : Content-Type: 'application/json', 'Accept': 'application/json'
#request payload  : { 'subc': 'create',
#                     'data':{ 'token': token,
#                              'planname': plan_name,
#                              'starttime': session_start_time,
#                              'deviceinfo':{'product': product_name,
#                                            'revision': product_revision,
#                                            'deviceid': device_serial_number
#                                           }
#                            }
#                    }

#response payload : {'result': ok|error, msg': log_error}

###create test case###
#method: POST
#request URI      : http://ats.borqs.com/smartapi/group/<group_id>/test/<session_sid>/case/<tid>/create
#request header   : Content-Type: 'application/json', 'Accept': 'application/json'
#request payload  : {'tid':tid, 'sid':session_id, 'casename': domain.case_name), 'starttime': case_start_time}}
#response payload : {'result': ok|error, msg': log_error}

###update test case###
#method: POST
#request URI      : http://ats.borqs.com/smartapi/group/<group_id>/test/<session_id>/case/<tid>/update
#request header   : Content-Type: 'application/json', 'Accept': 'application/json'
#request payload  : {'tid':tid, 'result': pass|fail|error|timeout, 'time': case_end_time, 'traceinfo': trace_stack_output}
#response payload : {'result': ok|error, msg': log_error}

###upload file###
#method: PUT
#request URI      : http://ats.borqs.com/smartapi/group/<group_id>/test/<session_id>/case/<tid>/fileupload
#request header   : Content-Type: 'image/png' | Content-Type: 'application/zip', 'Accept': 'application/json'
#request payload  : {'file': file_data }
#response payload : {'result': ok|error, msg': log_error}

def reporttime():
    '''
    return time stamp format with REPORT_TIME_STAMP_FORMAT
    '''
    return time.strftime(REPORT_TIME_STAMP_FORMAT, time.localtime(time.time()))

def getServerConfiguration(config):
    ret = {}
    cf = ConfigParser()
    cf.read(config)
    ret.update({'username': cf.get('account', 'username'),\
                'password': cf.get('account', 'password'),\
                'auth': cf.get('server', 'auth'),\
                'session_create': cf.get('server', 'session_create'),\
                'session_update': cf.get('server', 'session_update'),\
                'case_update': cf.get('server', 'case_update'),\
                'file_upload': cf.get('server', 'file_upload'),\
                'product': cf.get('device', 'product'),
                'revision': cf.get('device', 'revision'),
                'deviceid': cf.get('device', 'deviceid'),
                'planname': cf.get('device', 'planname'),
                'screen_width': cf.get('device', 'screen_width'),
                'screen_height': cf.get('device', 'screen_height')               
               })
    return ret


def getContentType(filename):
    '''
    lists and converts supported file extensions to MIME type
    '''
    ext = filename.split('.')[-1].lower()
    if ext == 'png': return 'image/png'
    if ext == 'gif': return 'image/gif'
    if ext == 'svg': return 'image/svg+xml'
    if ext == 'jpg' or ext == 'jpeg': return 'image/jpeg'
    if ext == 'zip': return 'application/zip'
    return None

def fbuffer(f, chunk_size=1024):
    '''
    read source file. default chunk size is 1024b.
    '''
    while True:
        chunk = f.read(chunk_size)
        if not chunk: break
        yield chunk

class MemoryZip(object):
 
    def __init__(self):
        # Create the a memory file-like object
        self.memory_zip = StringIO.StringIO()
 
    def appendFile(self, file_path, file_name=None):
        '''
        read local source file and add into memory
        '''
        if file_name is None:
            p, fn = os.path.split(file_path)
        else:
            fn = file_name
        c = open(file_path, "rb").read()
        self.append(fn, c)
        return self
 
    def append(self, filename_in_zip, file_contents):
        '''
        Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip
        '''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)
        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0
        return self
 
    def read(self):
        '''
        Returns a string with the contents of the in-memory zip
        '''
        self.memory_zip.seek(0)
        return self.memory_zip.read()
 
    def writetofile(self, filename):
        '''
        Writes the in-memory zip to a file.
        '''
        f = file(filename, "wb")
        f.write(self.read())
        f.close()
 
class Authentication(object):

    @staticmethod
    def regist(url, session_info, **kwargs):
        '''
        regist session on server
        ##session_id, token, session_info
        session info        { 'subc':'create',
                              'data':{'planname':'test.plan',
                                      'starttime':reporttime(),
                                      'deviceinfo':{'product':kwargs['product'],
                                                    'revision':kwargs['revision'],
                                                    'deviceid':kwargs['deviceid']
                                                   }
                                     }
                            }
        '''
        values = json.dumps(session_info)
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = request(method='post', url=url, data=values, headers=headers, timeout=AUTH_REQ_TIMEOUT)
        return r

    @staticmethod
    def getToken(url, username, password, appid='01', **kwargs):
        '''
        Get the session token from server.
        '''
        ret = None
        m = hashlib.md5()
        m.update(password)
        pwd = m.hexdigest()
        values = json.dumps({'appid':'01', 'username':username, 'password':pwd})
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        r = request(method='post', url=url, data=values, headers=headers, timeout=AUTH_REQ_TIMEOUT)
        return r and r['data']['token'] or None


def retry(tries, delay=1, backoff=2):
    '''
    retries a function or method until it returns True.
    delay sets the initial delay, and backoff sets how much the delay should
    lengthen after each failure. backoff must be greater than 1, or else it
    isn't really a backoff. tries must be at least 0, and delay greater than 0.
    @type tries: int
    @param tries: the retry times
    @type delay: int
    @param delay: the retry duration from last request to next request
    @type backoff: int
    @param backoff: used to make the retry duration wait longer
    @rtype: boolean
    @return: True if the function return True. else return False
    '''

    if backoff <= 1: 
        raise ValueError("backoff must be greater than 1")
    tries = math.floor(tries)
    if tries < 0: 
        raise ValueError("tries must be 0 or greater")
    if delay <= 0: 
        raise ValueError("delay must be greater than 0")
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay # make mutable
            rv = f(*args, **kwargs) # first attempt
            while mtries > 0:
                if rv != None or type(rv) == str or type(rv) == dict: # Done on success ..
                    return rv
                mtries -= 1      # consume an attempt
                time.sleep(mdelay) # wait...
                mdelay *= backoff  # make future wait longer
                rv = f(*args, **kwargs) # Try again
            print 'retry %d times all failed. plese check server status' % tries
            sys.exit(1)
            return False # Ran out of tries
        return f_retry # true decorator -> decorated function
    return deco_retry  # @retry(arg[, ...]) -> true decorator

@retry(3)
def request(method, url, data=None, **kwargs):
    '''
    Sends a request.
    :param url: URL for the request.    
    :param method: the request type of http method(get, post, put, delete)
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of http protocol
    :param \*\*kwargs: Optional arguments that request takes
    :return: dict or None 
    '''
    ret = None
    m = method.lower()
    if m in ('get', 'post', 'put', 'delete'):
        req = getattr(requests, m, None)
    try:
        r = req(url=url, data=data, **kwargs)
        if r:
            ret = r.json()
    except requests.exceptions.Timeout, e:
        #sys.stderr.write(str(e))
        pass
    except requests.exceptions.TooManyRedirects , e:
        #sys.stderr.write(str(e))
        pass
    except requests.exceptions.RequestException , e:
        #sys.stderr.write(str(e))
        pass
    except Exception, e:
        #sys.stderr.write(str(e))
        pass
    return ret

REQ_TIMEOUT = 3
class ReportClient(object):
    '''
    client to communicate with server
    '''
    def __init__(self, config=None, **kwargs):
        '''
        init with server.config
        '''
        if kwargs:
            self.__dict__.update(kwargs)
        if config:
            self.__dict__.update(getServerConfiguration(config))
        self.token = None
        self.session_id = None
        self.created = False

    def task(self):
        pass

    def _get_retry_count(self):
        pass

    def with_retries(self, q, fn):
        pass

    def regist(self, **kwargs):
        '''
        get token from server by server.config or user-input
        '''
        m = hashlib.md5()
        m.update(self.__dict__['password'])
        pwd = m.hexdigest()
        values = json.dumps({'subc': 'login', 'data':{'appid':'01', 'username':self.__dict__['username'], 'password':pwd}})
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        auth_url = self.__dict__['auth']
        ret = request(method='post', url=auth_url, data=values, headers=headers, timeout=AUTH_REQ_TIMEOUT)
        #OLD{u'results': {u'token': u'bdfbadaca1c514c3eafca6f2c4cb5c81', u'uid': u'51b8672e1ba1ee14235b03515c52c015'}}
        #NEW{u'msg': u'', u'data': {u'token': u'306fddbabe37011903e8f103829afc68', u'uid': 2}, u'result': u'ok|error'}
        try:
            self.token = ret['data']['token']
        except:
            pass
        return self.token

    def createSession(self, **kwargs):
        '''
        session_properties = {    'sid': self.session_id,\
                                  'product': 'p',\
                                  'revision': 'r',\
                                  'deviceid': 'devid',\
                                  'planname': 'test.plan',\
                                  'starttime': self.conf.test_start_time
                                 }
        '''
        self.session_id =  kwargs.pop('sid')
        url = self.__dict__['session_create'] % self.session_id
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        #new style API
        #values = { 'token': self.token,\
        #           'subc':'create',\
        #           'data':{'planname':kwargs.pop('planname'),\
        #                   'starttime':kwargs.pop('starttime'),\
        #                   'deviceinfo':{'product':kwargs.pop('product'),\
        #                   'revision':kwargs.pop('revision'),\
        #                   'deviceid':kwargs.pop('deviceid')\
        #                                }\
        #                  }\
        #          }
        deviceinfo = {'product':self.__dict__['product'], 'deviceid':self.__dict__['deviceid'], 'revision':self.__dict__['revision'], 'width':self.__dict__['screen_width'], 'height':self.__dict__['screen_height']}
        values = json.dumps({'subc': 'create',
                             'token':self.token ,
                             'data':{'planname':self.__dict__['planname'], 'starttime':kwargs.pop('starttime'), 'deviceinfo':deviceinfo}})
        ret = request(method='post', url=url, data=values, headers=headers, timeout=REQ_TIMEOUT)
        #{u'msg': u'', u'data': {}, u'result': u'ok'}
        try:

            if ret['result'] == 'ok':
                self.created = True
        except:
            pass
        return self.created

    def updateTestCase(self, **kwargs):
        result_url = self.__dict__['case_update'] % self.session_id
        file_url = self.__dict__['file_upload'] % (self.session_id, kwargs['payload']['tid'])
        kwargs.update({'token':self.token, 'result_url': result_url, 'file_url': file_url})
        UploadThread(**kwargs).start()

    def updateSession(self, **kwargs):
        '''
        session_properties = {    'sid': self.session_id,\
                                  'product': 'p',\
                                  'revision': 'r',\
                                  'deviceid': 'devid',\
                                  'planname': 'test.plan',\
                                  'starttime': self.conf.test_start_time
                                 }
        '''
        self.session_id =  kwargs.pop('sid')
        url = self.__dict__['session_update'] % self.session_id
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        #new style API
        #values = { 'token': self.token,\
        #           'subc':'create',\
        #           'data':{'planname':kwargs.pop('planname'),\
        #                   'starttime':kwargs.pop('starttime'),\
        #                   'deviceinfo':{'product':kwargs.pop('product'),\
        #                   'revision':kwargs.pop('revision'),\
        #                   'deviceid':kwargs.pop('deviceid')\
        #                                }\
        #                  }\
        #          }
        #sys.stderr.write(str(kwargs)+'\n')
        values = json.dumps({'subc': 'update',
                             'token':self.token ,
                             'data' : kwargs})
        ret = request(method='post', url=url, data=values, headers=headers, timeout=REQ_TIMEOUT)
        #{u'msg': u'', u'data': {}, u'result': u'ok'}
        try:

            if ret['result'] == 'ok':
                pass
        except:
            pass


class UploadThread(threading.Thread):
    '''
    Thread for uploading result.
    '''
    def __init__(self, callback=None, **kwargs):
        '''
        Init the instance of Sender.
        '''
        super(UploadThread, self).__init__()
        self.kwargs = kwargs
        self.callback = callback
        self.is_stop = False
        #self.daemon = True

    def run(self):
        '''
        The work method.
        '''
        try:
            if self.kwargs['payload']['result'] == 'pass':
                self.basicPayloadRequest(**self.kwargs)
            elif self.kwargs['payload']['result'] == 'fail':
                if self.basicPayloadRequest(**self.kwargs):
                    self.extrasRequest(**self.kwargs)
            elif self.kwargs['payload']['result'] == 'error':       
                if self.basicPayloadRequest(**self.kwargs):
                    self.extrasRequest(**self.kwargs)
        except Exception, e:
            pass
        finally:
            if self.callback: self.callback()

    def log(self, output):
        with open('mylog.txt', 'a') as f:
            f.write('%s%s' % (str(output), os.linesep))

    def basicPayloadRequest(self, **kwargs):
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        result_url = kwargs.pop('result_url')
        token = kwargs.pop('token')
        values = json.dumps({'subc':'update','token':token, 'data': kwargs['payload']})
        ret = request(method='post', url=result_url, data=values, headers=headers, timeout=REQ_TIMEOUT)
        #{u'msg': u'', u'data': {}, u'result': u'ok'}
        try:
            if ret['result'] == 'ok':
                return True
        except Exception, e:
            return False

    def extrasRequest(self, **kwargs):
        file_url = kwargs.pop('file_url')
        token = kwargs.pop('token')
        log = kwargs['extras']['log']
        snapshot = kwargs['extras']['screenshot_at_failure']
        files = {'file': open(snapshot, 'rb')}
        headers = {'content-type': 'image/png','Ext-Type':'%s%s%s' % ('expect', ':', 'step'), 'accept': 'application/json'}     
        try:
            ret = request(method='put', url=file_url, headers=headers, data=files['file'], timeout=10)
        except Exception, e:
            pass
        headers = {'content-type': 'application/zip',  'accept': 'application/json'}
        files = {'file': open(log, 'rb')}
        try:
            ret = request(method='put', url=file_url, headers=headers, data=files['file'], timeout=10)
        except Exception, e:
            #ret{u'msg': u'', u'data': {u'fileid': u'/file/3be61a9aef2940fc84f01278b9d6336f'}, u'result': u'ok'}
            pass
    def stop(self):
        '''
        Stop the thread.
        '''
        self.is_stop = True
