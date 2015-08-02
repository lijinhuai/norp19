#!/usr/bin/python
# -*- coding: utf-8 -*-
# filename: download.py
# from www.biuman.com

import threading
import time
import urllib2
import re
import string
import sys
import os

class Mydown(threading.Thread):
    """docstring for Download"""
    def __init__(self, threadname,url,ranges,filename):
        super(Mydown, self).__init__()
        self.threadname = threadname
        self.url = url
        self.ranges = ranges
        self.filename = filename
        self.downloadsize = 0
    def run(self):
        try:
            self.downloadsize = os.path.getsize( self.filename )
        except OSError:
            self.downloadsize = 0

        self.startpoint = self.ranges[0] +self.downloadsize
        print 'thread_%s downloading from %d to %d' %(self.threadname,self.startpoint,self.ranges[1])

        try:
            request = urllib2.Request(self.url)
            request.add_header("Range", "bytes=%d-%d" % (self.startpoint, self.ranges[1]))            
            response = urllib2.urlopen(request)
            self.oneTimeSize = 16384 #16kByte/time
            data = response.read(self.oneTimeSize)
            while data:
                handle = open(self.filename,'ab+')
                handle.write(data)
                handle.close()

                self.downloadsize += len(data) 
                data = response.read(self.oneTimeSize)            
        except Exception, e:
            print 'download error:',e
            return False
        return True




def getUrlFileSize(url):
    res = urllib2.urlopen(url)
    headers =res.info().headers #heaer info array
    for v in headers:
        #whether support accept-ranges
        # if v.find('Ranges') > 0:
        #     print 'done'
        if v.find('Length') > 0:
            size = v.split(':')[1].strip()
            size = int(size)
    return size

def splitBlock(totalsize,blocks):
    blocksize = totalsize/blocks
    ranges = []
    for x in xrange(0,blocks-1):
        ranges.append([x*blocksize,x*blocksize+blocksize-1])
    ranges.append([blocksize*(blocks-1),totalsize]) #deal with last block 

    return ranges
def islive(tasks):
    for task in tasks:
        if task.isAlive():
            return True
    return False

def startDown(url,output,blocks):
    
    size = getUrlFileSize(url)
    ranges = splitBlock(size,blocks)
    file_name = output.split(".")[0]
    filename = [ file_name+"tmpfile_%d" % i for i in xrange(0, blocks) ]
    tasks = []
    for x in xrange(0,blocks):
        t = Mydown(x,url,ranges[x],filename[x])
        t.setDaemon( True )
        t.start()        
        tasks.append( t )

    time.sleep( 2 )
    while islive(tasks):
        downloaded = sum( [task.downloadsize for task in tasks] )
        process = downloaded/float(size)*100
        show = u'\rFilesize:%d Downloaded:%d Completed:%.2f%%' % (size, downloaded, process)
        sys.stdout.write(show)
        sys.stdout.flush()
        time.sleep( 0.5 )
            
    filehandle = open( output, 'wb+' )
    for i in filename:
        f = open( i, 'rb' )
        filehandle.write( f.read() )
        f.close()
        try:
            os.remove(i)
            pass
        except:
            pass

    filehandle.close()

if __name__ == '__main__':
    url = 'http://50.7.73.90//dl//94e94a1d86cc2fa030b8b2dfee318976/558caefe//91porn/mp43/120814.mp4'
    output = 'test.mp4'
    startDown( url, output, blocks=5)    
