#!/usr/bin/env python

'''Post a message to twitter'''

#__author__ = 'dewitt@google.com'

from __future__ import print_function

try:
    import configparser
except ImportError as _:
    import ConfigParser as configparser

import getopt
import os
import sys
import twitter

USAGE = '''
    Usage: tweet [options] message

    This script posts a message to Twitter.

    Options:

    -h --help : print this help
    --encoding : the character set encoding used e.g. "utf-8". [optional]

    Documentation:

    The tweetrc file is used to set the user credentials.
    The file should contain the following five lines, replacing 
    each *value* with the proper respective one from 
    https://developer.twitter.com.

    [Tweet]
    consumer_key: *consumer_key*
    consumer_secret: *consumer_password*
    access_key: *access_key*
    access_secret: *access_password*
'''

def PrintUsageAndExit(errcode):
    print("Error: " + str(errcode))
    if(errcode == 0):
        print(USAGE)
        sys.exit(2)
    elif(errcode == 1):
        print("Missing or invalid file tweetrc.")
        print(USAGE)
        sys.exit(2)
    elif(errcode == 2):
        print("Invalid arguments passed.")
        print(USAGE)
        sys.exit(2)
    elif(errcode == 3):
        print("No message passed.")
        print(USAGE)
        sys.exit(2)
    elif(errcode == 4):
        print("Missing credentials.")
        print(USAGE)
        sys.exit(2)
    elif(errcode == 5):
        print("Your message could not be encoded.  Perhaps it contains non-ASCII characters?")
        print("Try explicitly specifying the encoding with the --encoding flag.")
        sys.exit(2)
    elif(errcode == 6):
        print("Warning: Invalid media file.")
    elif(errcode == 7):
        print("Twitter error.")
        sys.exit(2)
    
class TweetRc(object):
    def __init__(self):
        self._config = None

    def GetConsumerKey(self):
        return self._GetOption('consumer_key')

    def GetConsumerSecret(self):
        return self._GetOption('consumer_secret')

    def GetAccessKey(self):
        return self._GetOption('access_key')

    def GetAccessSecret(self):
        return self._GetOption('access_secret')

    def _GetOption(self, option):
        try:
            return self._GetConfig().get('Tweet', option)
        except:
            return None

    def _GetConfig(self):
        if not self._config:
            self._config = configparser.ConfigParser()
            self._config.read(os.getcwd() + "/tweetrc")
        return self._config

def main():
    try:
        shortflags = 'h'
        longflags = ['help', 'encoding=']
        opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
    except getopt.GetoptError:
        PrintUsageAndExit(2)
    
    encoding = None
    message = None
    media = None
    
    for o, a in opts:
        if o in ("-h", "--help"):
            PrintUsageAndExit(0)
        if o in ("--encoding"):
            encoding = a

    message = args[0]
    if(len(args)==2):
        if(("/" in args[1]) or ("\\" in args[1])):
            if(os.path.isfile(args[1])):
                media = args[1]
            else:
                PrintUsageAndExit(6)
        else:
            if(os.path.isfile(os.getcwd() + "\\" + args[1])):
                media = args[1]
            else:
                PrintUsageAndExit(6)
    
    if not message:
        PrintUsageAndExit(3)
    
    if(os.path.isfile(os.getcwd() + "/tweetrc")):
        rc = TweetRc()
    else:
        PrintUsageAndExit(1)
        
    consumer_key = rc.GetConsumerKey()
    consumer_secret = rc.GetConsumerSecret()
    access_key = rc.GetAccessKey()
    access_secret =  rc.GetAccessSecret()
    
    if not consumer_key or not consumer_secret or not access_key or not access_secret:
        PrintUsageAndExit(4)
        
    status = None
    
    try:
        api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                      access_token_key=access_key, access_token_secret=access_secret,
                      input_encoding=encoding)
                      
        status = api.PostUpdate(message, media)
        
    except UnicodeDecodeError:
        PrintUsageAndExit(5)
    except twitter.error.TwitterError as err:
        PrintUsageAndExit(7)

    if(status):
        print("{0} just posted: {1}".format(status.user.name, status.text))

if __name__ == "__main__":
    main()