

import requests
import json
from flask import Flask, request
from flask_restful import Api, Resource
import config as cf



if __name__ == '__main__':
    commit_list = []
    commit_count = 0

    next_url = cf.ARGON_URL + '/commits'
    params = {'access_token': cf.GIT_TOKEN}
    while next_url:
        response = requests.get(next_url, params = params)
        decoded_r = response.content.decode()
        response_j = json.loads(decoded_r)
        for commit in response_j:
            commit_count+=1
            commit_list.append(commit['sha'])
        
        if 'next' in response.links:
            next_url = response.links['next']['url']
            print('next url: ', next_url)
        else:
            next_url = ''

    print(commit_count, ' commits found: ', commit_list)


    url = cf.ARGON_URL + '/commits/' + commit_list.pop
    response = requests.get(url, params=params)
    decoded_r = response.content.decode()
    response_j = json.loads(decoded_r)
    print(response_j)


