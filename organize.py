import mistune
import os.path
import re
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request, urlretrieve
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode,urlretrieve
    from urllib2 import urlopen, Request, HTTPError


try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv

class CSVRenderer(mistune.Renderer):
    def table(self,header,body):
       return header+body
    def table_cell(self,content,**flags):
       return content+','
    def table_row(self,content):
       return content+'\n'


def parseLinks(string):
  # format is something like: 
  # <a href="https://github.com/MiSTer-devel/Menu_MiSTer/blob/master/releases/menu_20171229.rbf">menu_20171229.rbf</a>
  # or
  # <a href="https://github.com/MiSTer-devel/ao486_MiSTer/blob/master/releases/bios/boot0.rom">boot0.rom</a> <a href="https://github.com/MiSTer-devel/ao486_MiSTer/blob/master/releases/bios/boot1.rom">boot1.rom</a>
  pattern="<a href=\"(?P<link>.*?)\"[^>]*?>(?P<name>.*?)</a>"
  #result = re.match(pattern, string)
  result = re.findall(pattern, string)
  #print(result)
  return result

def checkgithublinks(link):
   path = os.path.normpath(link)
   parts=path.split(os.sep)
   print(parts)
   if (parts[4]=='blob'):
     print(link)
     link=link.replace('blob','raw')
     print(link)
   return link

#
#  download the newest markdown from:
#    https://raw.githubusercontent.com/wiki/alanswx/InstallerMister/Home.md
#
urlretrieve ("https://raw.githubusercontent.com/wiki/alanswx/InstallerMister/Home.md","misterinstaller.md")


mytable=[]
renderer = CSVRenderer()
markdown = mistune.Markdown(renderer=renderer)

with open ("misterinstaller.md", "r") as myfile:
    data=myfile.read()

scsv=markdown(data)
print(scsv)

table = []

f = StringIO(scsv)
reader = csv.reader(f, delimiter=',')
for row in reader:
    table.append(row)
    print('\t'.join(row))

print(table)

# 
# switch table into a better structure
#


keys=[]
newtable = []
i=0
for row in table:
  if i==0:
     print(row)
     keys = row
  else:
     j=0
     newrow = {}
     for col in row:
        newrow[keys[j]]=col
        if (keys[j]=='rom list' or keys[j]=='Latest Version' or keys[j]=='Core'):
           links=parseLinks(col)
           newrow[keys[j]+'_links']=links
        j=j+1
     newtable.append(newrow)
  i=i+1 

print("newtable\n=====\n")
print(newtable)

#
#  should we write out json?
#

# walk our table, and check to see if we have each core installed

misterpath="misterinst"


def checkAndDownloadFile(path,filebundles):
  for file in filebundles:
    print(file)
    filelink=file[0]
    filename=file[1]
    print(filename)
    print(filelink)
    fullpath = path+ "/" + filename
    if (os.path.isfile(fullpath)):
       print("* already exists: "+ fullpath)
    else:
       print("download: "+filelink+" to: "+fullpath)
       filelink=checkgithublinks(filelink)
       urlretrieve (filelink,fullpath)

def checkAndCreateFolder(path,directoryname):
  if directoryname!='-':
     print("****")
     fulldirpath = path + "/" + directoryname
     if not os.path.isdir(fulldirpath):
        print("make directory:"+fulldirpath)
        os.mkdir(fulldirpath)

for row in newtable:
  print("handling:")
  print(row)

  corel = row['Core_links'][0]
  if (len(corel)>1):
    corename=corel[1]
  else:
    corename="N/A"
  print(corename)
  print("=======")
  lvl = row['Latest Version_links']
  checkAndDownloadFile(misterpath,lvl)
  try:
    ldir = row['folder name']
    checkAndCreateFolder(misterpath,ldir)
  except KeyError:
     print("no directory name: "+corename)
  try:
     roml = row['rom list_links']
     checkAndDownloadFile(misterpath+'/'+ldir,roml)
  except KeyError:
     print("no roms "+corename)
