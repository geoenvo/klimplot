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


#---LIST OF VARIABLE
#nama folder direktori
klimplotdir="/home/klimplot/"
datadir="data/"
tiffdir="tiff/"
supportdir="support/"
inafile="indonesia.shp"
inapath=klimplotdir+supportdir+inafile
vrtdir="vrt/"

#resolution="672 1840"

#path di mana folder data yg difetch akan di simpan
datapath=klimplotdir+datadir
tiffpath=klimplotdir+tiffdir
vrtpath=klimplotdir+vrtdir


#Check Variable
print "\n Checking Variable"
print "\r datapath ="+datapath
print "\r inapath ="+inapath
print "\r tiffpath (result) ="+tiffpath

print "\n Checking Folder:"

#---LIST OF FUNCTION
#Function Checking Folder
def checkFolder(str):
	if not os.path.exists(str):
		#os.makedirs(str)
		print "\r Directory "+str+" is not exist. Please create one."
		print "\n Program Terminated. \n"
		sys.exit()
	else:
		print "\r Directory "+str+" already exist."

#UPDATING CSV FILE
#check csv file
# masukan pada postgresql table:
# [directory][csvname][tiffname][vrtname]
def updatedirfile(dbname):
	print "\n UPDATE DIR STARTED \n"
	#read folder structure data/
	#keep as an array _datadir[]

	#Create SQL Lite table (inf not exist)
	conn = sqlite3.connect(dbname+".db")
	c = conn.cursor()

	# Create table if not exist
	c.execute('DROP TABLE IF EXISTS '+dbname)
	c.execute('CREATE TABLE IF NOT EXISTS '+dbname+'(csvpath text, csvfile text, tiffile text, UNIQUE (csvpath, csvfile))')
	c.execute('DELETE FROM '+dbname)
	
	for dirname, dirnames, filenames in os.walk(datapath):
		for filename in filenames:
			file_name_only = os.path.splitext(filename)[0]
			file_extension = os.path.splitext(filename)[1]
			#read file_extension
			if	file_extension == ".csv":
				sql = "INSERT OR IGNORE INTO "+dbname+" VALUES ('"+dirname+"/','"+filename+"','')"
				c.execute(sql)
			elif file_extension == ".tiff":
				#print "\nADA TIFF FILE"
				sql = "UPDATE "+dbname+" SET tiffile = '"+filename+"' WHERE (csvfile = '"+file_name_only+".csv' AND csvpath='"+dirname+"/' AND (tiffile IS NULL OR tiffile = ''))"
				#print sql
				c.execute(sql)
	conn.commit()
	conn.close()
	print "\n UPDATE DIR FINISHED \n"	

	
#BEGIN	
	
checkFolder(datapath)
checkFolder(inapath)
checkFolder(tiffpath)
checkFolder(vrtpath)
#subprocess.call("", shell=True)

print "\n Ready to go.."

#Update Dir File
print "\n UPDATE DIR \n"
updatedirfile("scan")


print "\n Alhamdulillah."

