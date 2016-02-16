# Klimplot
# Convert Script
# (c) 2015 Mohammad Fadli
# Geo Enviro Omega, PT
# Funded by BMKG - Indonesia
# KlimPlot digunakan untuk memvisualisasikan dan mempublikasikan data Iklim menjadi bentuk Map Services.
# Script ini digunakan untuk mengkonversikan file csv keluaran PIKAM menjadi file tiff hasil dari interpolasi dan sudah dipotong dengan shapefile Indonesia.

#HOWTO
# Jalankan di background: python klimplot_convert.py &
# Taruh di cron, atau jalankan sebagai services berkala
# Struktur folder hasil akan menyesuaikan 

import os.path
import subprocess
import sys
from os import walk
from os import listdir
from os.path import isfile, join
import sqlite3
from osgeo import gdal
import shutil


#---LIST OF VARIABLE

#nama folder direktori
klimplotdir="/home/klimplot/"
datadir="data/"
tiffdir="tiff/"
supportdir="support/"
inafile="indonesia.shp"
inapath=klimplotdir+supportdir+inafile
vrtdir="vrt/"

#path di mana folder data yg difetch akan di simpan
datapath=klimplotdir+datadir
tiffpath=klimplotdir+tiffdir
vrtpath=klimplotdir+vrtdir

dbname='scan'
uploadir='/var/www/geonode/geonode/uploaded/uploads/'
logfile=uploadir+'duplicatedir.txt'

#---LIST OF FUNCTION

def log(content):
	print content
	flog = open(logfile, 'a')
	flog.writelines(content)
	flog.close()
	
#Function Checking Folder
def checkFolder(str):
	if not os.path.exists(str):
		#os.makedirs(str)
		log( "\r Directory "+str+" is not exist. Please create one.")
		log( "\n Program Terminated. \n")
		sys.exit()
	else:
		log( "\r Directory "+str+" already exist.")

#--BEGIN
flog = open(logfile, 'w')
conn = sqlite3.connect(dbname+".db")
c = conn.cursor()

#DUPLICATE DIRECTORY STRUCTURE
with conn:
	c.execute('SELECT DISTINCT csvpath FROM '+dbname+' WHERE (csvpath IS NOT NULL OR csvpath <> "")' )
	while True:
		row = c.fetchone()
		if row == None:
			break
		strcsvpath=row[0]
		strtiffpath=strcsvpath.replace("data","tiff")
		log( "\n"+strtiffpath)
		if not os.path.exists(strtiffpath):
			os.makedirs(strtiffpath)
			print "Directory "+strtiffpath+" successfully created!"
conn.commit()

#COPY TIFF FILES TO NEW STRUCTURE
with conn:
	c.execute('SELECT csvpath,tiffile FROM '+dbname+' WHERE (tiffile IS NOT NULL OR tiffile <> "")' )
	while True:
		row = c.fetchone()
		if row == None:
			break
		strcsvpath=row[0]
		tiffile=row[1]
		strtiffpath=strcsvpath.replace("data","tiff")
		log( "\n"+strtiffpath)
		shutil.copyfile(strcsvpath+tiffile, strtiffpath+tiffile)
		
conn.commit()
conn.close()

print "Ahoy!"

