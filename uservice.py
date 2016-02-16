import os.path
import subprocess
import sys
from os import walk
from os import listdir
from os.path import isfile, join
import sqlite3
import lxml
import pycurl
import cStringIO
from lxml import etree
import xml.etree.ElementTree as ET

#nama folder direktori
klimplotdir="/home/klimplot/"
datadir="data/"
tiffdir="tiff/"
supportdir="support/"
inafile="indonesia.shp"
inapath=klimplotdir+supportdir+inafile

#resolution="672 1840"

#path di mana folder data yg difetch akan di simpan
datapath=klimplotdir+datadir
tiffpath=klimplotdir+tiffdir

dbname='scan'
uploadir='/var/www/geonode/geonode/uploaded/uploads/'
logfile=uploadir+'log.txt'
layerslistfile=uploadir+'layers.xml'
workspace="geonode:"

response = cStringIO.StringIO()

c = pycurl.Curl()
c.setopt(pycurl.URL, "http://localhost:8080/geoserver/gwc/rest/layers")
c.setopt(pycurl.USERPWD, 'admin:geoserver')
c.setopt(c.WRITEFUNCTION, response.write)
c.perform()
c.close()

root = ET.fromstring(response.getvalue())
conn = sqlite3.connect(dbname+".db")
c = conn.cursor()

def log(content):
	print content
	flog = open(logfile, 'a')
	flog.writelines(content)
	flog.close()

#put to array
i=0
_tiffiles={}
with conn:
	c.execute('SELECT DISTINCT tiffile FROM '+dbname+' WHERE (csvfile IS NOT NULL OR csvfile <> "")' )
	while True:
		row = c.fetchone()
		if row == None:
			break
		_tiffiles[i]=str(row[0])
		i=i+1
conn.commit()

for name in root.iter('name'):
	layername= name.text.replace(workspace,"")
	for i in range(len(_tiffiles)):
		strtiff=str(_tiffiles[i]).replace(".tiff","")
		strtiff=str(strtiff).replace(".","_")
		if layername == strtiff:
			sql = "UPDATE "+dbname+" SET layername = '"+layername+"' WHERE (tiffile='"+_tiffiles[i]+"')"
			#print sql
			print layername
			c.execute(sql)
			conn.commit()

print "\nLIST SERVICES:\n"
for name in root.iter('name'):
	layername= name.text.replace(workspace,"")
	print layername
	
#Create XML
	ff = open(layerslistfile, 'w')
	ff.writelines("<services>\n")
	ff.close()
	with conn:
		c.execute("SELECT distinct csvpath,layername FROM "+dbname)
		while True:
			row = c.fetchone()
			if row == None:
				break
			pathcut=row[0].replace(datapath,"")
			pathcut=pathcut.replace("/","")
			strtiff=row[1]
	
			log( "\n"+strtiff)
			strtiff=strtiff.replace(".tiff","")
			strtiff=strtiff.replace(".","_")
			ff = open(layerslistfile, 'a')
			if strtiff <> '':
				print pathcut
				print strtiff
				ff.writelines(" <layer>\n")
				ff.writelines("	<group>"+pathcut+"</group><name>"+strtiff+"</name>\n")
				ff.writelines(" </layer>\n")
			ff.close()
	conn.commit()
	
	# Delete last character ";"
	"""
	with open(layerslistfile, 'rb+') as ff:
		ff.seek(-2, os.SEEK_END)
		ff.truncate()
	ff.close()
"""
	ff = open(layerslistfile, 'a')
	ff.writelines("</services>")
	ff.close()	
	
conn.close()
