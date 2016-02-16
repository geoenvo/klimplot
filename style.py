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
#Arguments
try:
	arg1=str(sys.argv[1])
except:
	print "try: style.py updatedir or updatestyle"
	sys.exit()

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

dbname='scan'
stylename='Peluang_Curah_Hujan'
updatelayersgeonode='python /var/www/geonode/manage.py updatelayers'
uploadir='/var/www/geonode/geonode/uploaded/uploads/'
logfile=uploadir+'log.txt'
layerslistfile=uploadir+'layers.xml'

#---LIST OF FUNCTION

def log(content):
	print content
	flog = open(logfile, 'a')
	flog.writelines(content)
	flog.close()

def writef(pathfile,content):
	#print content
	flog = open(pathfile, 'a')
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

#UPDATING CSV FILE
#check csv file
# masukan pada postgresql table:
# [directory][csvname][tiffname][vrtname]
def updatedirfile(dbname):
	log("\n UPDATE DIR STARTED \n")
	#read folder structure data/
	#keep as an array _datadir[]

	#Create SQL Lite table (inf not exist)
	conn = sqlite3.connect(dbname+".db")
	c = conn.cursor()

	# Create table if not exist
	c.execute('DROP TABLE IF EXISTS '+dbname)
	c.execute('CREATE TABLE IF NOT EXISTS '+dbname+'(csvpath text, csvfile text, tiffile text, layername text, UNIQUE (csvpath, csvfile))')
	c.execute('DELETE FROM '+dbname)
	
	for dirname, dirnames, filenames in os.walk(datapath):
		for filename in filenames:
			file_name_only = os.path.splitext(filename)[0]
			file_extension = os.path.splitext(filename)[1]
			#read file_extension
			if	file_extension == ".csv":
				sql = "INSERT OR IGNORE INTO "+dbname+" VALUES ('"+dirname+"/','"+filename+"','','')"
				c.execute(sql)
				
	for dirname, dirnames, filenames in os.walk(datapath):
		for filename in filenames:
			file_name_only = os.path.splitext(filename)[0]
			file_extension = os.path.splitext(filename)[1]
			#read file_extension
			if file_extension == ".tiff":
				#print "\nADA TIFF FILE"
				sql = "UPDATE "+dbname+" SET tiffile = '"+filename+"' WHERE (csvfile = '"+file_name_only+".csv' AND csvpath='"+dirname+"/' AND (tiffile IS NULL OR tiffile = ''))"
				#print sql
				c.execute(sql)
	
	conn.commit()
	
	log( "\nSummary:")
	log( "\nList of Tiff File(s):")
	
	
	
	with conn:
		c.execute("select count(distinct tiffile) from "+dbname)
		while True:
			row = c.fetchone()
			if row == None:
				break
			log("\nTotal Tiff file generated: "+str(row[0]))
	conn.commit()
	
	with conn:
		c.execute("SELECT count(distinct csvfile) FROM "+dbname)
		while True:
			row = c.fetchone()
			if row == None:
				break
			log( "\nTotal csv file(s): "+str(row[0])+" row(s)")
	conn.commit()
	
	conn.close()
	log( "\n UPDATE DIR FINISHED \n")

def updatestyle(tiffile):
	cmd = 'curl -v -u admin:geoserver -XPUT -H "Content-type: text/xml" -d "<layer><defaultStyle><name>'+stylename+'</name><workspace>geonode</workspace></defaultStyle></layer>" http://45.118.135.27/geoserver/rest/layers/geonode:'+tiffile
	log( '\n'+cmd+'\n')
	subprocess.call(cmd, shell=True)
	
#--- BEGIN	
#Check Variable
ff = open(layerslistfile, 'w')
flog = open(logfile, 'w')

log( "\n Checking Variable")
log( "\r datapath ="+datapath)
log( "\r inapath ="+inapath)
log( "\r tiffpath (result) ="+tiffpath)

log( "\n Checking Folder:")

checkFolder(datapath)
checkFolder(inapath)
checkFolder(tiffpath)
checkFolder(vrtpath)
#subprocess.call("", shell=True)

log( "\n Ready to go..")


#Update Dir File
if arg1 == "updatedir" or arg1 == "updatestyle":
	log( "\n UPDATE DIR \n")
	updatedirfile(dbname)
	
if arg1 == "updatestyle":

	# MAIN LOOP
	# UPDATE LAYERS!
	log( "\n CHECK TIFF FILE \n")
	conn = sqlite3.connect(dbname+'.db')
	c = conn.cursor()
	with conn:
		c.execute("SELECT distinct tiffile FROM "+dbname)
		while True:
			row = c.fetchone()
			if row == None:
				break
			#print "\n Update Style "+row[0]+"\n"
			#create tiff file
			tiffilecount=row[0]
			tiffilecount=tiffilecount.replace(".tiff","")
			tiffilecount=tiffilecount.replace(".","_")
			writef(uploadir+"listlayer.txt",tiffilecount)
			log( "\n Update Style "+tiffilecount+"\n")
			updatestyle(tiffilecount)
	conn.commit()
	conn.close()

	subprocess.call(updatelayersgeonode, shell=True)

copydb='cp '+klimplotdir+dbname+'.db '+uploadir+dbname+'.db'
subprocess.call(copydb, shell=True)
	
log( "\n Alhamdulillah.")
