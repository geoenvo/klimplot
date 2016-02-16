# Klimplot
# Fetch Script
# (c) 2015 Mohammad Fadli
# Geo Enviro Omega, PT
# KlimPlot digunakan untuk memvisualisasikan dan mempublikasikan data Iklim menjadi bentuk Map Services.
# Script ini digunakan untuk me

#HOWTO
# Jalankan di background: python klimplot.py &
# Taruh di cron, atau jalankan sebagai services berkala
# Struktur folder hasil akan menyesuaikan 

import os.path
import wget
import subprocess

#define variable

#Sumber Data (Server PIKAM via http)
spath="http://202.90.199.147/ec_prob/results_mat/"

#sfolder="2015.01.01/"
#sfile="control.2015.02_ver_2015.01.01.csv"
#surl=spath+sfolder+sfile
#cpath=os.getcwd()+"/"

#nama folder direktori
datadir="data/"

#path di mana folder data yg difetch akan di simpan
datapath="/home/klimplot/"+datadir

#datapath=cpath+datadir
#filepath=datapath+sfile


#Check Folder data

if not os.path.exists(datapath):
    os.makedirs(datapath)
else:
        print "\n Directory already exist."
"""
#Check File
if not os.path.exists(filepath):
        #Get File
        wget.download(surl,datapath)
else:
        print "\n File already exist. Download Aborted."
"""
subprocess.call("wget -r -np -nc --cut-dirs=2 -A '*.csv' --ignore-case -nH -P "+datapath+" "+spath, shell=True)

"""
-r recursive download folder
-np no parents directory, tidak mendownload isi dari parent directory
-nH would download all files to the directory d in the current directory
-P you will save to specific directory
-nc, --no-clobber: skip downloads that would download to existing files.
--cut-dirs tidak melihat struktur direktori yang ada di sub folder sebelumnya.
-A '*.csv' hanya download csv file
"""

print "\n Alhamdulillah."
