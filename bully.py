import sys
import os
import random
import threading
from multiprocessing import Process, Value, Array
import zmq
import time

lock = threading.Lock()

has_received_leader_buffer = []

# Set timeout to be 2 sec
TIMEOUT = 2000

# "responder" method is assigned to each process' listener_thread
def responder(nodeId, ids_alive_filtered):
    print("RESPONDER STARTS", nodeId)

    # Connect and subscribe to all alive ports
    sockets = []
    for id_alive in ids_alive_filtered:
        port = 5550+id_alive
        context = zmq.Context()
        socket_subscribe = context.socket(zmq.SUB)
        socket_subscribe.connect(f"tcp://127.0.0.1:{port}")
        
        socket_subscribe.subscribe("LEADER")
        socket_subscribe.subscribe("TERMINATE")
        
        sockets.append(socket_subscribe)


    for i in range(len(sockets)):
        socket_subscribe = sockets[i]
        # Register subscribe socket to poller
        # So we could avoid infinite receive() blocks
        poller = zmq.Poller()
        poller.register(socket_subscribe, zmq.POLLIN)


    # Receive messages
    for socket in sockets:
        evts = dict(poller.poll(timeout=TIMEOUT))
        if socket in evts:
            message = socket.recv_json()

            # Parse received message
            senderId = message["senderId"]
            data = message["data"]

            if data == "TERMINATE":
                # Leader is already selected
                # Notify main and finish myself
                return "END"
                break
            
            elif data == "LEADER":
                # If senderId < myid, then send "RESP" to sender
                if senderId < nodeId:
                    # TODO: send "RESP" to sender
                    send_port = port = 5550+int(senderId)
                    send_context = zmq.Context()
                    socket_send = send_context.socket(zmq.PUB)
                    socket_send.connect(f"tcp://127.0.0.1:{send_port}")

                    message = {
                        "senderId": nodeId,
                        "data": "RESP"
                    }

                    # after that, notify main to broadcast "LEADER"
                    return "BROADCAST_LEADER"
                    pass

               
        else:
            # No response means i am the leader
            # Notify main to  broadcast "TERMINATE"
            print("Timeout!")
            return "BROADCAST_TERMINATE"


    # incoming_message = []

    # for i in range(self.num_worker):
    #     incomingData = socket_receive.recv_json()
    #     # print ('ResultCollector process id:', os.getpid(), " Retrieved data:", incomingData )
    #     incoming_partial_results.append(incomingData)

    # lock.acquire()
    # has_received_leader_buffer[nodeId] = 1
    # lock.release()

    time.sleep(2)
    print("End of a processor.")
    pass


# "leader" method is assigned to every node alive
def leader(nodeId, isStarter, ids_alive_filtered):
    
    pid = os.getpid()
    print("PROCESS STARTS ", pid, nodeId, isStarter, ids_alive_filtered)

    # Create listener thread
    listener_thread = threading.Thread(target=responder, args=(nodeId, ids_alive_filtered,))
    listener_thread.start()

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
        ids_alive_filtered = list(filter(lambda id: i!=id, ids_alive))
        
        process = Process(target=leader, args=(i, isStarter, ids_alive_filtered,))
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