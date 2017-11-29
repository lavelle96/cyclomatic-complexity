

import threading
import requests
import json
from flask import Flask, request, abort
from flask_restful import Api, Resource
from common_resources import Common_resources
import config as cf
from datetime import datetime
import uuid
import sys
import time
import os


#TODO: Implement lock structure on all resources
#TODO: Thread that checks whether or not the clients are taking too long on a commit and resetting the commits variable to None if they are allowing
        #it to be operated on by another client


app = Flask(__name__)
api = Api(app)

#Map of commits to their complexity, 0 if they havent been handled yet

#Map of client ids to the commit they're working on and when they started the commi


def get_commit(COMMITS_MAP):
    for commit in COMMITS_MAP:
        if COMMITS_MAP[commit] == None:
            return commit
    return None

def end_check():
    """
    Thread that checks every second whether or not all commits have been completed
    Also gives total complexity and time taken
    """
    global resources
    global resource_lock
    start = time.time()
    while(1):
        
        time.sleep(1)
        resource_lock.acquire()
        print('Commits completed: ', resources.COMPLETED_COMMITS)
        if resources.COMMIT_COUNT <= resources.COMPLETED_COMMITS:
            print('Closing server')
            end = time.time()
            time_taken = end-start #Recorded in seconds
            no_clients = len(resources.CLIENTS)
            try:
                with open("results.txt", "a") as myfile:
                    result = 'number of clients: ' + str(no_clients) + '  time_taken: ' + str(time_taken) + '\n'
                    myfile.write(result)
            except:
                print('problem writing to file')
            resource_lock.release()
            os.system("killall -KILL python")
           
            return
        resource_lock.release()
    
def node_check():
    global resources
    global resource_lock

    while(1):
        resource_lock.acquire()
        now = datetime.now()
        for client in resources.CLIENTS:
            #CHeck the time stamp diff with now
            if len(resources.CLIENTS[client]) > 0:
                time_diff = (now-resources.CLIENTS[client]['start_time']).total_seconds()
                if time_diff > cf.ALLOWED_TIME_DIFF:
                    commit = resources.CLIENTS[client]['commit']
                    resources.COMMITS_MAP[commit] = None

        resource_lock.release()
        time.sleep(2)



class node_init_API(Resource):
    def __init__(self):
        global resources
        self.resources = resources
        global resource_lock
        self.resource_lock = resource_lock
        

    def get(self):
        id = str(uuid.uuid4())
        self.resource_lock.acquire()
        self.resources.CLIENTS[id] = {}
        self.resource_lock.release()
        repo = cf.ARGON_URL
        resp = {
            'client_id': id,
            'repo_url': repo
        }
        return resp

class distributor_API(Resource):
    def __init__(self):
        global resources
        self.resources = resources
        global resource_lock
        self.resource_lock = resource_lock

    def get(self, client_id):
        self.resource_lock.acquire()
        if not client_id in self.resources.CLIENTS:
            print('Client unauthorised as worker')
            abort(403)
        commit = get_commit(self.resources.COMMITS_MAP)
        if commit == None:
            self.resources.COMMITS_FINISHED = True
        
        response = {
            'sha': commit
        }
        self.resources.CLIENTS[client_id]['commit'] = commit
        self.resources.CLIENTS[client_id]['start_time'] = datetime.now()
        self.resources.COMMITS_MAP[commit] = 0
        self.resource_lock.release()
        return response


    def post(self, client_id):
        #Received post with body 
        #Commit:  Complexity: 
       
        if not request.is_json:
            print('Request not in json format')
            abort(400)
        data = request.json
        commit = data['commit']
        complexity = int(data['complexity'])
        self.resource_lock.acquire()
        if not (commit in self.resources.COMMITS_MAP):
            print('Commit doesnt exist')
            abort(404)
        
        self.resources.CLIENTS[client_id] = {}
        
        if self.resources.COMMITS_MAP[commit] == None or self.resources.COMMITS_MAP[commit] == 0:
            self.resources.COMMITS_MAP[commit] = complexity
            self.resources.OVERALL_COMPLEXITY += complexity 
            self.resources.COMPLETED_COMMITS += 1

        self.resource_lock.release()
        


api.add_resource(node_init_API, '/api/init')
api.add_resource(distributor_API, '/api/clients/<string:client_id>')

if __name__ == '__main__':
    
    global resources
    resources = Common_resources()

    global resource_lock 
    resource_lock = threading.Lock()

    next_url = cf.ARGON_API_URL + '/commits'
    params = cf.PARAMS
    
    while next_url:
        response = requests.get(next_url, params = params)
        decoded_r = response.content.decode()
        response_j = json.loads(decoded_r)
        
        for commit in response_j:
            resources.COMMITS_MAP[commit['sha']] = None
            resources.COMMIT_COUNT += 1
        
        if 'next' in response.links:
            next_url = response.links['next']['url']
        else:
            next_url = ''
    

    end_check_thread = threading.Thread(target=end_check)
    end_check_thread.start()

    node_check_thread = threading.Thread(target=node_check)
    node_check_thread.start()

    server_port = cf.MASTER_PORT
    app.run('0.0.0.0', server_port)
    '''

    response = requests.get('https://github.com/rubik/argon/archive/37e1c85cedb3485473fa4506aaf4d1fada43e606.zip', params = params)
    response_d = response.content
    print(response_d)

    date_raw = commit['commit']['author']['date'] 
            #"2016-06-22T06:54:51Z"
            date = datetime.strptime(date_raw, "%Y-%m-%dT%H:%M:%SZ")
            if date < earliest_date:
                earliest_date = date
                earliest_commit = commit['sha']
            commit_count+=1
            commit_list.append(commit['sha'])

'''
