import paramiko
import os

#paramiko.util.log_to_file('/tmp/paramiko.log')

#Open a transport

host = '149.28.95.222'
port = 2222
transport = paramiko.Transport((host, port))

#Auth

password = '7Po,Ef@+RpQNjvNN'
username = 'root'
print ("Connecting...")
transport.connect(username = username, password = password)

#Go!

sftp = paramiko.SFTPClient.from_transport(transport)

print ("Connected.")

#Upload
#print (sftp.listdir())
cwd = os.getcwd()
#print(cwd)
inputdir = cwd + ('/images/series/')
print(os.listdir(inputdir))
for file in os.listdir(inputdir):
    namefile = file[:-4]
    extfile = file[-4:]
    #print(namefile)
    #print(extfile)
    localpath = cwd + '/images/' + file
    print(localpath)
    largefile = '/home/comiconlinefree.com/public_html/images/series/large/' + file
    smallfile = '/home/comiconlinefree.com/public_html/images/series/small/' + file
    sftp.put(localpath, largefile)
    sftp.put(localpath, smallfile)
    os.remove(localpath)

#Download
# filepath = '/etc/passwd'
# localpath = '/home/remotepasswd'
# sftp.get(filepath, localpath)






sftp.close()
transport.close()
print ("Closed connection.")
