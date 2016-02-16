import os.path
import subprocess
import sys
import sqlite3
import lxml
import pycurl
import shutil

#---LIST OF VARIABLE
#nama folder direktori
klimplotdir="/home/klimplot/"
datadir="data/"
tiffdir="tiff/"
tmpdir="tmp/"
supportdir="support/"
inafile="indonesia.shp"
inapath=klimplotdir+supportdir+inafile

#path di mana folder data yg difetch akan di simpan
datapath=klimplotdir+datadir
tiffpath=klimplotdir+tiffdir
tmppath=klimplotdir+tmpdir

workspace="geonode:"
dbname='scan'

#--BEGIN
conn = sqlite3.connect(dbname+".db")
c = conn.cursor()

with conn:
	c.execute('SELECT DISTINCT csvpath,tiffile FROM '+dbname+' WHERE (layername IS NULL OR layername = "")' )
	while True:
		row = c.fetchone()
		if row == None:
			break
		print row[1]
		src=row[0].replace(datadir,tiffdir)+row[1]
		dst=tmppath+row[1]
		#print "\n",src
		#print dst
		shutil.copy2(src, dst)
		
		
conn.commit()
conn.close()