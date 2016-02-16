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

resolution="672 1840"

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
def updatedirfile():
	print "\n UPDATE DIR STARTED \n"
	#read folder structure data/
	#keep as an array _datadir[]

	#Create SQL Lite table (inf not exist)
	conn = sqlite3.connect('datadir.db')
	c = conn.cursor()

	# Create table if not exist
	c.execute('''DROP TABLE IF EXISTS datadir''')
	c.execute('''CREATE TABLE IF NOT EXISTS datadir
				(csvpath text, csvfile text, tiffile text, UNIQUE (csvpath, csvfile))''')
	c.execute('''DELETE FROM datadir''')
	
	for dirname, dirnames, filenames in os.walk(datapath):
		for filename in filenames:
			file_name_only = os.path.splitext(filename)[0]
			file_extension = os.path.splitext(filename)[1]
			#read file_extension
			if	file_extension == ".csv":
				sql = "INSERT OR IGNORE INTO datadir VALUES ('"+dirname+"/','"+filename+"','')"
				c.execute(sql)
			elif file_extension == ".tiff":
				#print "\nADA TIFF FILE"
				sql = "UPDATE datadir SET tiffile = '"+filename+"' WHERE (csvfile = '"+file_name_only+".csv' AND csvpath='"+dirname+"/' AND (tiffile IS NULL OR tiffile = ''))"
				#print sql
				c.execute(sql)
	conn.commit()
	conn.close()
	print "\n UPDATE DIR FINISHED \n"	
		
#Function create_tiff_file
def create_tiff_file(filename,fpath):
	#Create VRT File
	file_name_only=os.path.splitext(filename)[0]
	print "\ngenerate "+file_name_only+".vrt"
	fvrt = open(fpath+file_name_only+'.vrt', 'w')
	fvrt.writelines('<OGRVRTDataSource>\n')
	fvrt.writelines('<OGRVRTLayer name="'+file_name_only+'">\n')
	fvrt.writelines('	<SrcDataSource>'+fpath+filename+'</SrcDataSource>\n')
	fvrt.writelines('	<GeometryType>wkbPoint</GeometryType>\n')
	fvrt.writelines('	<GeometryField encoding="PointFromColumns" x="field_1" y="field_2" z="field_3"/>\n')
	fvrt.writelines('	<LayerSRS>EPSG:4326</LayerSRS>\n')
	fvrt.writelines('</OGRVRTLayer>\n')
	fvrt.writelines('</OGRVRTDataSource>\n')
	fvrt.close()
	
	#Create Tiff File
	print "\nCREATE TIFF FILE\n"
	#gdal_grid_cmd='gdal_grid -a invdist:power=2.0:smoothing=1.0 -txe 95.05 141.0 -tye 5.85 -10.9 -outsize 336 920 -of GTiff -ot Float64 -l '+file_name_only+' "'+fpath+file_name_only+'.vrt" "'+fpath+file_name_only+'_full.tiff"'
	gdal_grid_cmd='gdal_grid -a invdist:power=2.0:smoothing=1.0 -txe 95.05 141.0 -tye 5.85 -10.9 -outsize '+resolution+' -of GTiff -ot Float64 -l '+file_name_only+' "'+fpath+file_name_only+'.vrt" "'+fpath+file_name_only+'_full.tiff"'
	print "\n command: "+gdal_grid_cmd+"\n"
	subprocess.call(gdal_grid_cmd, shell=True)
	print "Done.\n"
	
	#CLIP tiff file
	print "\nCLIP TIFF FILE\n"
	gdal_wrap_cmd='gdalwarp -of GTiff -cutline "'+inapath+'" -cl indonesia -crop_to_cutline "'+fpath+file_name_only+'_full.tiff" "'+fpath+file_name_only+'.tiff"'
	print "\n command: "+gdal_wrap_cmd+"\n"
	subprocess.call(gdal_wrap_cmd, shell=True)
	print "Done.\n"
	




checkFolder(datapath)
checkFolder(inapath)
checkFolder(tiffpath)
checkFolder(vrtpath)
#subprocess.call("", shell=True)

print "\n Ready to go.."

#Update Dir File
print "\n UPDATE DIR #1 \n"
updatedirfile()

#CHECK TIFF FILE
print "\n CHECK TIFF FILE \n"
conn = sqlite3.connect('datadir.db')
c = conn.cursor()
with conn:
	c.execute("SELECT * FROM datadir WHERE tiffile IS NULL OR tiffile = ''")
	while True:
		row = c.fetchone()
		if row == None:
			break
		print "\nFollowiing files doesn't have tiff files:\n"
		print row[0], "  |  ", row[1]
		#create tiff file
		create_tiff_file(row[1],row[0])
conn.commit()
conn.close()

#Update Dir File
print "\n UPDATE DIR #2 \n"
updatedirfile()
#check layer file

#Apakah ada yang baru?

#create structure folder vrt/ sesuai dengan structure pada data/

#looping for each folder
#	read file list, keep in array _datadir_filename[]
#		looping for each filename[]
#			create vrt file di vrt dir masing-masing
#			jalankan gdal_grid lalu taruh ke folder tiff
#			clip file tiff tersebut menggunakan shapefile indonesia, taruh di folder yg sama (tiff)
#end loop

#bikin/update json
#curl XPOST import

#update layers
#ganti style



print "\n Alhamdulillah."

