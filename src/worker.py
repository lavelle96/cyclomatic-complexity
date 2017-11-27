import pygit2
import config as cf
import os
import subprocess
import json
import requests
from format import format_node_init, format_commit_call

if __name__ == '__main__':
    

    #Get client id and url from server
    url = format_node_init(cf.MASTER_PORT)
    response = requests.get(url)
    response_d = response.content.decode()
    response_j = json.loads(json.loads(response_d))
    client_id = response_j['client_id']
    repo_url = response_j['repo_url']

    
    
    path = client_id
    if not os.path.exists(path):
        os.makedirs(path)
    repo = pygit2.clone_repository(repo_url, path)

    finished = False

    url = format_commit_call(cf.MASTER_PORT, client_id)
    headers =  {'content-type': 'application/json'}

    while(not finished):

        
        response = requests.get(url)
        response_j = json.loads(json.loads(response.content.decode()))
        sha = response_j['sha']
        p = subprocess.Popen(['git', 'checkout', sha], cwd=client_id)
        p.wait()
        response = subprocess.check_output(['argon', '--json', '--min', '2', client_id])
        j_response = json.loads(response.decode())
        total_complexity = 0

        for b in j_response:
            if 'blocks' in b:
                block = b['blocks']
                for element in block:
                    total_complexity += element['complexity']
        print('About to send total complexity: ', total_complexity)
        response = {
            'commit': sha,
            'complexity': total_complexity
        }
        requests.post(url, data=json.dumps(response), headers=headers)
    
    
    

