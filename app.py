from flask import Flask, render_template,request
from subprocess import run,PIPE,STDOUT
import sys
import subprocess

# import requests
import os
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

app = Flask(__name__)
pid = ""

def upload_file():
   if request.method == 'POST':
      f = request.files['keys']
      f.save("keywords.txt")
    #   return 'file uploaded successfully'

def writeFile(variables):
    with open('variables.txt','w') as search:
        search.write(variables)

@app.route('/update', methods=['GET'])
def update():
    with open('updates.txt','r') as fl:
        return fl.read().replace("\n"," ").strip() 
@app.route("/",methods = ['POST','GET'])
def posts():
    intro=""
    end=''
    limit=''
    actn =''
    if request.method == 'POST':
        
        actn = request.form['action']
        if(actn =="start"):
            intro = request.form['intro']
            end = request.form['end']
            limit = request.form['limit']
            url =request.form['url']
            username = request.form['username']
            password = request.form['password']
            with open('updates.txt','w') as fl:
              fl.write('Loading..') 
            
            variables = intro+"|"+end+"|"+limit+"|"+url+"|"+username+"|"+password
            writeFile(variables)
            upload_file()

            global pid
            pid = subprocess.Popen([sys.executable, "scraper.py"],stdin=PIPE,shell=True)

        print(pid)
        if(actn == "killprocess"):
            subprocess.Popen("TASKKILL /F /PID {pidd} /T".format(pidd=pid.pid))
            print("Process killed")
        # proc = subprocess.Popen(["rm","-r","scraper.py"])
        # proc.terminate()
        # os.spawnl(os.P_DETACH, run([sys.executable,'scraper.py'],shell=False,stdout=PIPE))
        # run([sys.executable,'scraper.py'],shell=False,stdout=PIPE)

         
    return render_template('index.html')

@app.route("/terminate",methods = ['POST','GET'])
def killprocess():
    global pid
    subprocess.Popen("TASKKILL /F /PID {pidd} /T".format(pidd=pid.pid))
    print(pid.pid)
    # return("Process Killed +++++++++++++++++++++++++++++++++++++++")


if __name__ == '__main__':
   app.run(debug = True)