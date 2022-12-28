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
def responder(nodeId, ids_alive, pubsocket):
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

    print("NodeId:", nodeId, "listening on ports:", ports)

    # Start receiving messages
    while True:
        evts = dict(poller.poll(timeout=TIMEOUT))
        if socket in evts:
            message = socket.recv_string()


            message_parsed = message.split(":")

            received_body = message_parsed[0]
            received_port = int(message_parsed[1])
            sender_id = int(message_parsed[2])

            print("nodeId:", nodeId, "received:", message)
            
            if received_body == "TERMINATE":
                # Leader is already selected
                # Notify main and finish myself
                return "END"
                break
            
            elif received_body == "LEADER":
                # If sender_id < myid, then send "RESP" to sender
                if sender_id < nodeId:                    
                    # TODO: send "RESP" to sender
                    
                    # pubsocket.bind(f"tcp://127.0.0.1:{5550+nodeId}")
                    time.sleep(2)        

                    resp_message = f"RESP:{5550+nodeId}:{nodeId}"
                    
                    print("nodeId:", nodeId, "sending RESP to the sender nodeId:", sender_id, "on its own port:", 5550+nodeId)
                    pubsocket.send_string(resp_message)
                    
                    # pubsocket.disconnect(f"tcp://127.0.0.1:{received_port}")


                    # after that, notify main to broadcast "LEADER"
                    # return "BROADCAST_LEADER"
                    pass

        else:
            # If no message is received for TIMEOUT amount of time
            # Then this means i am leader
            # Notify main
            print("Timeout!", nodeId)
            return "BROADCAST_TERMINATE"


    time.sleep(2)
    print("End of a processor.")
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

    # Start listener thread listening on other ports (nodes)
    listener_thread = threading.Thread(target=responder, args=(nodeId, ids_alive, socket,))
    listener_thread.start()

    
    if isStarter:
        # Broadcast 'LEADER'

        message = f"LEADER:{port}:{nodeId}"

        # Make sure others started listening before i send LEADER
        time.sleep(2) 

        print("NodeId:", nodeId, "sending message:", message)
        socket.send_string(message)



    responder_message = listener_thread.join()

    if responder_message == "END":
        # Game is over
        time.sleep(1)

        return

    elif responder_message == "BROADCAST_LEADER":
        time.sleep(1)

        # TODO: broadcast "LEADER"
        return

    elif responder_message == "BROADCAST_TERMINATE":
        # Game is over, i am the leader
        time.sleep(1)

        # TODO: broadcast "TERMINATE"
        return 


    if isStarter:
        pass
    else:
        pass
    
    time.sleep(1)
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

    ids = [0,1,2,3,4,5]
    ids_alive = [1,2,3,4]
    ids_starter = [2]

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