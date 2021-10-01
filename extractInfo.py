#!/usr/bin/python3
import re
import os
import sys
import argparse
import requests

fuzzDir = ['/web-inf/web.xml',
'/docs/index.html',
'/.git',
'/monitor',
'/actuator',
'/cookie',
'/debug',
'/admin',
'/manager/html',
'/console',
'/resin-admin',
'/webadmin'

]

urlList = []
urlAlive = []
parser = argparse.ArgumentParser()

parser.add_argument("-l", type=str, required=False, help="Contain this string at urL",metavar='[contain this string at urL]')
parser.add_argument("-i", type=str, required=False, help="Contain this string at uri",metavar='[contain this string at uri]')
args = parser.parse_args()

urlContainWord = args.l
uriContainWord = args.i

patternURL = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
searchedList = []
urlList = []

def findURL(content):
    global searchedList
    global urlList

    patternURL = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    regexURL = re.compile(patternURL)
    mo = regexURL.search(content)
    if mo!=None:
        url = mo.group()
        if url not in searchedList:
            if urlContainWord==None:
                searchedList.append(url)
                domain = url[:url.find('/',8)]

                if domain not in urlList:
                    urlList.append(domain)

                print('[+] urL : ',url)
            else:
                if urlContainWord in url:
                    searchedList.append(url)
                    domain = url[:url.find('/',8)]

                    if domain not in urlList:
                        urlList.append(domain)
                    print('[+] urL : ',url)

def findURI(content):
    global searchedList
    patternURI = r"\/([A-z0-9?#\/=]){0,100}"
    regexURI = re.compile(patternURI)
    mo = regexURI.search(content)

    if mo!=None:
        uri = mo.group()
        if uri not in searchedList:
            if uriContainWord == None:
                searchedList.append(uri)
                print('[+] uri : ',uri)
            else:
                if uriContainWord in uri:
                    searchedList.append(uri)
                    print('[+] uri : ',uri)


def searchPattern(path):
    try:
        fileList = os.listdir(path)
        
        for fileName in fileList:
            if fileName=='.' or fileName=='..':
                pass
            if os.path.isdir(path+'/'+fileName):
                searchPattern(path+'/'+fileName)
            else:
                f = open(path+'/'+fileName,'r')
                c = f.read()
                f.close()

                findURL(c)
                #findURI(c)
    except Exception as e:
       # print(e)
        pass

def urlFuzzing(urlList, fuzzDir):
    result = ''
    global urlAlive

    
    for url in urlList:
        try:
            requests.get(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'},timeout=2)
            urlAlive.append(url)
    
            for fuzz in fuzzDir:
                req = requests.get(url+fuzz,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'})
                if req.status_code!=404:
                    urlAndCode = url+fuzz+'-----'+str(req.status_code)+'\r\n'
                    result+=urlAndCode
        except Exception as e:
            #print(e)
            pass
    
    return result


searchPattern('.')

result = ''
for r in searchedList:
    result+=(r+'\r\n')

result+=('\r\n\r\n')

fuzzResult = urlFuzzing(urlList,fuzzDir)
result+= ('url alive List : \r\n')
for aUrl in urlAlive:
    result +=(aUrl+'\r\n')

result+='\r\n'
result+=('fuzz result : \r\n')
result +=(fuzzResult)

f = open('result.txt','w')
f.write(result)
f.close()

