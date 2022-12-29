import sys
import os
import random
import threading
from multiprocessing import Process, Value, Array
import zmq
import time

lock = threading.Lock()

has_received_leader_buffer = []

# Set timeout to be 10 sec
TIMEOUT = 5000



# "responder" method is assigned to each process' listener_thread
def responder(nodeId, ids_alive, pubsocket, responder_return):
    print("RESPONDER STARTS", nodeId)
    
    time.sleep(1)

    # Connect and subscribe to all alive ports
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.subscribe("LEADER")
    socket.subscribe("TERMINATE")
    socket.subscribe("RESP")


    ports = [5550 + int(i) for i in ids_alive]

    for port in ports:
        socket.connect(f"tcp://127.0.0.1:{port}")

    # Register subscribe socket to poller
    # So we could avoid infinite receive() blocks
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    # Start receiving messages
    while True:
        evts = dict(poller.poll(timeout=TIMEOUT))
        if socket in evts:
            message = socket.recv_string()


            message_parsed = message.split(":")

            received_body = message_parsed[0]
            received_port = int(message_parsed[1])
            sender_id = int(message_parsed[2])
            to_id = int(message_parsed[3])
            
            if received_body == "RESP":
                # There is another node with higher,
                # Become passive listener
                if to_id == nodeId:
                    responder_return["RECEIVED_RESP"] = 1

                if to_id > nodeId:
                    # Eliminate smaller passive nodes as well
                    responder_return["RECEIVED_RESP"] = 1


            if received_body == "TERMINATE":
                # Leader is already selected
                # Notify main and finish myself
                return
            

            elif received_body == "LEADER":
                # If sender_id < myid, then send "RESP" to sender
                if sender_id < nodeId:                                        
                    time.sleep(1)        

                    resp_message = f"RESP:{5550+nodeId}:{nodeId}:{sender_id}"
                    
                    print("RESPONDER RESPONDS", nodeId, sender_id)
                    pubsocket.send_string(resp_message)
                    
                    # after that, notify main to broadcast "LEADER"
                    responder_return["BROADCAST_LEADER"] = 1
                    pass

        else:
            # If no message is received for TIMEOUT amount of time
            # Then this means i am leader
            # Notify main
            if not responder_return["RECEIVED_RESP"]:
                responder_return["BROADCAST_TERMINATE"] = 1
    # End of listener_thread
    pass





# "leader" method is assigned to every node alive
def leader(nodeId, isStarter, ids_alive):
    
    pid = os.getpid()
    print("PROCESS STARTS ", pid, nodeId, isStarter, ids_alive)

    # Open my publisher socket 
    # (also share this pub socket with listener thread)
    port = 5550 + nodeId
    
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://127.0.0.1:{port}")

    # Shared variable among 2 threads (main & listener)
    responder_return = {"BROADCAST_LEADER": 0, "RECEIVED_RESP": 0, "BROADCAST_TERMINATE": 0}

    # Start listener thread listening on other ports (nodes)
    listener_thread = threading.Thread(target=responder, args=(nodeId, ids_alive, socket, responder_return,))
    listener_thread.start()

    # Make sure others started listening before i send LEADER
    time.sleep(2) 


    if isStarter:
        # Broadcast 'LEADER'
        responder_return["BROADCAST_LEADER"] = 1
        pass


    while not responder_return["BROADCAST_LEADER"]:
        # Wait until i need to broadcast "LEADER"
        if responder_return["RECEIVED_RESP"]:
            break
        pass
    

    if not responder_return["RECEIVED_RESP"] and responder_return["BROADCAST_LEADER"]:
        time.sleep(2)

        message = f"LEADER:{port}:{nodeId}:-1"

        print("PROCESS MULTICASTS LEADER MSG:", nodeId)
        socket.send_string(message)

        time.sleep(3)


    if not responder_return["RECEIVED_RESP"]:
        while not responder_return["BROADCAST_TERMINATE"]:
            pass
        
        message = f"TERMINATE:{port}:{nodeId}:-1"

        print("PROCESS BROADCASTS TERMINATE MSG:", nodeId)
        socket.send_string(message)

    listener_thread.join()
    pass


    
def main(args):  
    global ids, ids_alive, ids_starter, has_received_leader_buffer

    numProc =  6
    numAlive = 4
    numStarter = 1

    has_received_leader_buffer = [0 for i in range(numProc)]
    # numProc = int(args[1])
    # numAlive = int(args[2])
    # numStarter = int(args[3])

    # ids = [i for i in range(numProc)]
    # ids_alive = random.sample(ids, numAlive)
    # ids_starter = random.sample(ids_alive, numStarter)

    ids = [0,1,2,3,4,5,6,7,8,9]
    ids_alive = [9,8,0,3]
    ids_starter = [9,3]

    print("Alives:", ids_alive, sep="\n")
    print("Starters:", ids_starter, sep="\n")


    # Create processes
    # Each process represents a node
    processes = []
    
    for i in ids_alive:
        isStarter = (i in ids_starter)
        # ids_alive = list(filter(lambda id: i!=id, ids_alive))
        
        process = Process(target=leader, args=(i, isStarter, ids_alive,))
        processes.append(process)

    for process in processes:
        process.start()
    
    for process in processes:
        process.join()

    pass


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Invalid command line arguments!")
    else:
        main(args=sys.argv)