# Introduction

- The [Bully Leader Election Algorithm (BLE)](https://en.wikipedia.org/wiki/Bully_algorithm) is a distributed algorithm that is used to select a leader (or coordinator) among a group of processes (or nodes) in a computer network.

- It is called the bully algorithm because it allows the processes to "bully" or challenge each other for leadership by sending special messages called election messages.

### How it works?

1. Coordinator multicasts "LEADER" message to nodes with higher IDs.
2. If any node with higher ID is available at the moment, they will respond with "RESP". Then they will behave as a coordinator and multicast "LEADER" to higher nodes.
3. If a coordinator doesn't receive any "RESP", then it will declare itself as the leader and broadcasts "TERMINATE" to network.

### With Visuals

![1](https://user-images.githubusercontent.com/68128434/214062750-75cb7a89-9a37-47be-a3ac-03f6346cc6e3.JPG)

![2](https://user-images.githubusercontent.com/68128434/214062754-a672b9e3-0cec-401f-be08-df031e962091.JPG)

## Specs

- This implementation is using python's multiprocessing library to simulate a network of nodes as processes.
- Processes communicates using [ZMQ](https://zeromq.org/languages/python/) sockets (PUB-SUB)

### How To Run?

Command line arguments will be:

```bash
python bully.py <numProc> <numAlive> <numStarter>
```

`numProc`: Number of nodes in the network
`numAlive`: Number of alive nodes in the network
`numStarter`: Number of coordinators in the beginning of algorithm

### Example Run

```
python bully.py 10 4 2
```

```
Alives :
[ 8 , 9 , 0 , 3 ]
Starters :
[ 9 , 3 ]
PROCESS STARTS: 42004 8 False
RESPONDER STARTS: 8
PROCESS STARTS: 49092 9 True
RESPONDER STARTS: 9
PROCESS STARTS: 42836 3 True
RESPONDER STARTS: 3
PROCESS STARTS: 40496 0 False
RESPONDER STARTS: 0
PROCESS MULTICASTS LEADER MSG: 9
PROCESS MULTICASTS LEADER MSG: 3
RESPONDER RESPONDS 9 3
RESPONDER RESPONDS 8 3
PROCESS MULTICASTS LEADER MSG: 8
RESPONDER RESPONDS 9 8
PROCESS BROADCASTS TERMINATE MSG: 9
```
