#!/usr/bin/env python
# coding: utf-8

# In[1]:


import docker
import math
import numpy as np
import json
import requests
from collections import defaultdict
import random
client = docker.from_env()


# In[ ]:


def initialize_swarm(n):
    client.swarm.init(advertise_addr='eth0')


# In[ ]:


def create_services(n):
    for i in range(n):
        client.services.create('polinux/stress', 'stress --cpu 1 --io 1 --vm 1 --vm-bytes 128M --timeout 600s')


# In[ ]:


def remove_services():
    services = client.services.list()
    for service in services:
        service.remove()    


# In[ ]:


def get_stats():
    response = requests.get('http://localhost:8080/api/v2.0/summary?type=docker&recursive=true')
    return json.loads(response.content)


# In[ ]:


def get_service_container():
    services = client.services.list()
    service_containers = defaultdict(list)
    for service in services:
        tasks = service.tasks()
        for task in tasks:
            if(task['DesiredState'] == 'running'):
                service_containers[service.id].append(task['Status']['ContainerStatus']['ContainerID'])
    return service_containers


# In[ ]:


def get_priority_compute():
    compute = []
    priority = []
    total_consumed = 0
    data = get_stats()
    service_containers = get_service_container()
    for service_id in service_containers:
        memory_used = 0
        for container_id in service_containers[service_id]:
            if('/docker/' + container_id in data):
                memory_used += data['/docker/' + container_id]['latest_usage']['memory']/1000000
            else:
                data = get_stats()
                memory_used += data['/docker/' + container_id]['latest_usage']['memory']/1000000
        priority.append(random.randint(1, 3))
        total_consumed += int(math.ceil(memory_used))
        compute.append(int(math.ceil(memory_used)))
    return priority, compute, total_consumed


# In[ ]:


priority, compute, total_consumed = get_priority_compute()


# In[ ]:


def knapsack_dp(values,weights,n_items,capacity,return_all=False):
    check_inputs(values,weights,n_items,capacity)

    table = np.zeros((n_items+1,capacity+1),dtype=np.float32)
    keep = np.zeros((n_items+1,capacity+1),dtype=np.float32)

    for i in range(1,n_items+1):
        for w in range(0,capacity+1):
            wi = weights[i-1] # weight of current item
            vi = values[i-1] # value of current item
            if (wi <= w) and (vi + table[i-1,w-wi] > table[i-1,w]):
                table[i,w] = vi + table[i-1,w-wi]
                keep[i,w] = 1
            else:
                table[i,w] = table[i-1,w]

    picks = []
    K = capacity

    for i in range(n_items,0,-1):
        if keep[i,K] == 1:
            picks.append(i)
            K -= weights[i-1]

    picks.sort()
    picks = [x-1 for x in picks] # change to 0-index

    if return_all:
        max_val = table[n_items,capacity]
        return picks,max_val
    return picks


def check_inputs(values,weights,n_items,capacity):
    # check variable type
    assert(isinstance(values,list))
    assert(isinstance(weights,list))
    assert(isinstance(n_items,int))
    assert(isinstance(capacity,int))
    # check value type
    assert(all(isinstance(val,int) or isinstance(val,float) for val in values))
    assert(all(isinstance(val,int) for val in weights))
    # check validity of value
    assert(all(val >= 0 for val in weights))
    assert(n_items > 0)
    assert(capacity > 0)


# In[ ]:


n_items = len(compute)
capacity = 400
picks = knapsack_dp(priority, compute, n_items, capacity)
print(picks)


# In[ ]:


services = client.services.list()
for i in range(len(compute)):
    if i not in picks:
        print(services[i].name)
    #services[i].update()


# In[ ]:


import subprocess


# In[ ]:


subprocess.call(["docker", "service","update", "--constraint-rm", "node.hostname==docker-desktop","busy_kowalevski"])
subprocess.call(["docker", "service","update", "--constraint-add", "node.hostname==muhammad-Inspiron-3542","busy_kowalevski"])
subprocess.call(["docker", "service","update", "--constraint-add", "node.hostname==docker-desktop","busy_kowalevski"])


# In[4]:


services = client.services.list()
services


# In[ ]:




