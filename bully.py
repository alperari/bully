import sys
import os
import random
import threading
from multiprocessing import Process, Value, Array
import zmq
import time

lock = threading.Lock()

has_received_leader_buffer = []

ids = []
ids_alive = []
ids_starter =  []

# "responder" method is assigned to each process' listener_thread
def responder(nodeId):
    global has_received_leader_buffer

    print("RESPONDER STARTS", nodeId)

    # Listen to other processes
    # port = 5550+nodeId
    # context = zmq.Context()
    # socket_receive = context.socket(zmq.PULL)
    # socket_receive.bind(f"tcp://localhost:{port}")
        
        

    # incoming_message = []

    # for i in range(self.num_worker):
    #     incomingData = socket_receive.recv_json()
    #     # print ('ResultCollector process id:', os.getpid(), " Retrieved data:", incomingData )
    #     incoming_partial_results.append(incomingData)

    lock.acquire()
    has_received_leader_buffer[nodeId] = 1
    lock.release()

    pass


# "leader" method is assigned to every node alive
def leader(nodeId, isStarter):
    pid = os.getpid()
    print("PROCESS STARTS ", pid, nodeId, isStarter)

    # Create listener thread
    listener_thread = threading.Thread(target=responder, args=(nodeId,))
    listener_thread.start()



    listener_thread.join()

    # If no node has responded with "OK"
    #   then it means this node is the leader, i.e. highest id in the network
    #   and it will broadcast "TERMINATE"

    if isStarter:
        pass
    else:
        pass
    
    time.sleep(2)
    pass


def main(args):  
    global ids, ids_alive, ids_starter, has_received_leader_buffer

    numProc =  3
    numAlive = 2
    numStarter = 2

    has_received_leader_buffer = [0 for i in range(numProc)]

    # numProc = int(args[1])
    # numAlive = int(args[2])
    # numStarter = int(args[3])

    # ids = [i for i in range(numProc)]
    # ids_alive = random.sample(ids, numAlive)
    # ids_starter = random.sample(ids_alive, numStarter)

    ids = [0,1,2]
    ids_alive = [1,2]
    ids_starter = [1]

    print("Alives:", ids_alive, sep="\n")
    print("Starters:", ids_starter, sep="\n")


    # Create processes
    # Each process represents a node
    processes = []
    
    for i in ids_alive:
        isStarter = (i in ids_starter)
        process = Process(target=leader, args=(i, isStarter,))
        processes.append(process)

    for process in processes:
        process.start()
    
    for process in processes:
        process.join()

    pass

