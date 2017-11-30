import config as cf

#remote deployment
def format_node_init(port):
    url = 'http://' + cf.MASTER_IP + ':' + str(port) + '/api/init'
    return url

def format_commit_call(port, client_id):
    url = 'http://' + cf.MASTER_IP + ':' + str(port) + '/api/clients/' + str(client_id)
    return url
'''

def format_node_init(port):
    url = 'http://localhost:' + str(port) + '/api/init'
    return url

def format_commit_call(port, client_id):
    url = 'http://localhost:' + str(port) + '/api/clients/' + str(client_id)
    return url
'''
