import zmq
import time
import json

PORT = 3001
topics = ["LEADER","TERMINATE"]

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://127.0.0.1:{PORT}")

    counter = 1

    while True:
        message = f"{topics[counter%2]}:{PORT}"

        print(f"Sending message: {message} on PORT: {PORT}")
        socket.send_string(message)

        counter += 1
        time.sleep(1)

if __name__ == "__main__":
    main()