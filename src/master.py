

import requests
import json
from flask import Flask, request, abort
from flask_restful import Api, Resource
import config as cf
from datetime import datetime
import uuid
import sys

app = Flask(__name__)
api = Api(app)

#Map of commits to their complexity, 0 if they havent been handled yet
COMMITS_MAP = {}

#Map of client ids to the commit they're working on and when they started the commit
CLIENTS = {}

COMMITS_FINISHED = False

OVERALL_COMPLEXITY = 0

def get_commit():
    for commit in COMMITS_MAP:
        if COMMITS_MAP[commit] == None:
            return commit
    return None

class node_init_API(Resource):
    def get(self):
        id = str(uuid.uuid4())
        CLIENTS[id] = {}
        repo = cf.ARGON_URL
        resp = {
            'client_id': id,
            'repo_url': repo
        }
        return json.dumps(resp)

class distributor_API(Resource):
    def __init__(self):
        self.OVERALL_COMPLEXITY =  0
    def get(self, client_id):
        if not client_id in CLIENTS:
            print('Client unauthorised as worker')
            abort(403)
        commit = get_commit()
        if commit == None:
            COMMITS_FINISHED = True

        response = {
            'sha': commit
        }
        CLIENTS[client_id]['commit'] = commit
        CLIENTS[client_id]['start_time'] = datetime.now()
        return json.dumps(response)


    def post(self, client_id):
        #Received post with body 
        #Commit:  Complexity: 
        if not request.is_json:
            print('Request not in json format')
            abort(400)
        data = request.json
        commit = data['commit']
        complexity = data['complexity']
        if not (commit in COMMITS_MAP):
            print('Commit doesnt exist')
            abort(404)
        COMMITS_MAP[commit] = complexity
        print('Complexity Received: ', complexity)
        CLIENTS[client_id] = {}
        self.OVERALL_COMPLEXITY += complexity
        print('Overall complexity: ', self.OVERALL_COMPLEXITY)


api.add_resource(node_init_API, '/api/init')
api.add_resource(distributor_API, '/api/clients/<string:client_id>')

if __name__ == '__main__':
    OVERALL_COMPLEXITY = 0
    commit_list = []
    commit_count = 0

    next_url = cf.ARGON_API_URL + '/commits'
    params = cf.PARAMS
    
    while next_url:
        response = requests.get(next_url, params = params)
        decoded_r = response.content.decode()
        response_j = json.loads(decoded_r)
        
        for commit in response_j:
            COMMITS_MAP[commit['sha']] = None
        
        if 'next' in response.links:
            next_url = response.links['next']['url']
        else:
            next_url = ''
    
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
