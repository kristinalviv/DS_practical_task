# DS_practical_task
 Distributed Systems replicated logs task


Following components are needed:
- Client-server app
- code for Master node
- code for Secondary node
- Concurrency programming
- Client interaction
- Communication channel  
- Docker


To run the apps in the docker containers, follow these steps:

import the project

cd to server dir

1. Create new network: docker network create -d bridge test_new

2. To build docker image run: docker build -f Dockerfile -t docker22de/devops:DS_server .

3. To run docker container execute: docker run -it --name server --network test_new -p 4040:4040 docker22de/devops:DS_server

Server is up and running in container

4. Open another cmd and cd to client dir

5. To build docker image run:docker build -f Dockerfile -t docker22de/devops:DS_client .

6. To run docker containers execute: 

docker run -it --name client1 --network test_new docker22de/devops:DS_client

docker run -it --name client2 --network test_new docker22de/devops:DS_client

docker run -it --name client3 --network test_new docker22de/devops:DS_client

7. To test write concern feature (write concern is 3) - enter the following command into new terminal 

docker network disconnect NETWORK_NAME CONTAINER_NAME
e.g.(docker network disconnect test_new 37634569c10a)

After that send any message to the server, message won't be saved due to timeout. (Neither on server, nor on any client)

To restore connection with client node enter command (docker network connect NETWORK_NAME CONTAINER_NAME)

Following message will be saved.



*Connection successfully established and messages can be written to the server.*

*'exit', 'end', 'quit', 'q' will stop app execution and all messages with id (from both server and client) will be shown*
*client can list all messages if user will enter 'List()' input within 5 seconds timeouts*
