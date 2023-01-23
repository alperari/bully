import zmq
import time

PORT = 5552
TIMEOUT = 10000


def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://127.0.0.1:{PORT}")

       
    socket.subscribe("LEADER")
    socket.subscribe("TERMINATE")

    print("started listening on port:", PORT)
    
    # Register to poller
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        events = dict(poller.poll(timeout=TIMEOUT))

        if (socket in events) and (events[socket] == zmq.POLLIN):

            message = socket.recv_string()
            print("Received message:", message)

        else:
            print(f"Timeout {TIMEOUT}ms!")
            break
            

if __name__ == "__main__":
    main()