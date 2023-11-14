import os
import socket
import time
current_ip = socket.gethostbyname(socket.gethostname())
print("Current IP Address: "+current_ip)
print("Start Runing Server...")
files = [f for f in os.listdir('.') if os.path.isfile(f)]
if('manage.py' in files):
    os.system("python manage.py runserver "+current_ip+":8080")
else:
    print("Could not locate manage.py file")
    time.sleep(2)
    print("Exiting...")
    time.sleep(2)
time.sleep(2)
