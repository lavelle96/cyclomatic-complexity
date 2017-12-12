import config as cf
import os
import subprocess
import json
import requests
import time
import sys
from format import format_node_init, format_commit_call

if __name__ == '__main__':
    
    print('Client running')
    #Get client id and url from server
    url = format_node_init(cf.MASTER_PORT)
    server_running = False
    print('sending get to : ', url)
    while(not server_running):
        try:
            response = requests.get(url)
            server_running = True
        except:
            print('Waiting for server')
            time.sleep(0.5)
    response_d = response.content.decode()
    response_j = json.loads(response_d)
    client_id = response_j['client_id']
    repo_url = response_j['repo_url']

    
    
    path = client_id
    if not os.path.exists(path):
        os.makedirs(path)
    
    p1 = subprocess.Popen(['git', 'clone', repo_url, path])
    p1.wait()

    url = format_commit_call(cf.MASTER_PORT, client_id)
    headers =  {'content-type': 'application/json'}

    while(1):

        
        try:
            response = requests.get(url)
        except:
            print('Closing client')
            break
        
        response_j = json.loads(response.content.decode())
        sha = response_j['sha']
        if sha == None:
            print('Closing client')
            break
        p = subprocess.Popen(['git', 'checkout', sha], cwd=client_id)
        p.wait()
        response = subprocess.check_output(['argon', '--json', '--min', '2', client_id]) #+ '/src'])
        j_response = json.loads(response.decode())
        total_complexity = 0

        for b in j_response:
            if 'blocks' in b:
                block = b['blocks']
                for element in block:
                    total_complexity += element['complexity']
        response = {
            'commit': sha,
            'complexity': total_complexity
        }
        try:
            requests.post(url, data=json.dumps(response), headers=headers)
        except:
            print('Closing Client')
            break
            
    
    
    

