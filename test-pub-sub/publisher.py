import zmq
import time

PORT = 3000

def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://127.0.0.1:{PORT}")

    message = 0
    while True:
        print(f"Sending message: '{message}' on PORT: {PORT}")
        socket.send_string(str(message))

        message =  (message+ 1) % 5
        time.sleep(0.25)

if __name__ == "__main__":
    main()