import os

datadir = array[]

for dirname, dirnames, filenames in os.walk('/home/klimplot/data/'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        print(os.path.join( subdirname))
        datadir[] = os.path.join( subdirname)

    # print path to all filenames.
#    for filename in filenames:
#        print(os.path.join(dirname, filename))

print datadir
