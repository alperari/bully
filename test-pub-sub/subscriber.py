import zmq
import time

PORT = 3000
TIMEOUT = 2000
topics = ["0","1","2","3","4"]


def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://127.0.0.1:{PORT}")

    for topic in topics:
        socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    # Register to poller
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    while True:
        events = dict(poller.poll(timeout=TIMEOUT))

        if socket in events:
            message = socket.recv_string()
            print("Received message:", message)
        else:
            print(f"Timeout {TIMEOUT}ms!")
            break

if __name__ == "__main__":
    main()