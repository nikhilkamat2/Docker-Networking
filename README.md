Requirements:
Docker
brctl
iproute2

The script uses topology.csv to run
please modify topology.csv according to input
use del.sh to remove the creaated containers, and networking devices

To run:
sudo python a.py <numleaf> <numspine> <imagefile> <csvfile>
eg.
sudo python a.py 2 2 assignmentimage topology.csv

numleaf = number of leaf containers
numspine = number of spine containers
imagefile = image file used for docker containers
csvfile = contains data of containers and their networks

Overview:
Python Program creates container leaf-spine topology,
accepts input from csv file specifying containers and networks ( L2, L3, Vxlan, GRE ) used to connect them to each other,
creates containers and networks,
connects them to leaf-spine topology
and configures routes for achieving end-to-end connectivity.

Working:
The code uses Container and Network class to keep a track
of the Containers and Networks created.
The containers and networks are appended to their respective lists.
The container object has reference to networks it is connected to and
the network has references to containers that use it.

IP addresses are assigned incrementally for every newly created network type

#Creating Leaf and Spine
We create Leaf containers named leaf0,leaf1...
We create Spine containers named spine0,spine1...
Each leaf container is connected to each spine container by veth pairs
Appropriate routes are added to achieve end to end connectivity

#Creating Bridged Networks
We create containers for source and destination
We create a linux bridge using brctl
We attach the containers to the bridge using veth pairs
We attach the bridge to the leaf using veth pairs

#Creating L3 Networks
We create containers for source and destination
We create a L3 bridge using docker
We attach the containers to the bridge using docker api
We attach the bridge to the leaf using using docker api

#Creating Vxlan  Networks
We create containers for source and destination
We create namespace corresponding to each container
We create a bridge in each namespace
And attach a Vxlan device to this bridge
We attach the containers to the bridge in the namespace
using veth pairs to connect containers to the namespace,
then add that interface to the bridge using brctl api
We attach the namespace to the leaf using using veth pairs
Appropriate routes are added in namespace,leaf and spine
to achieve end to end connectivity

#Creating GRE Networks
We create containers for source and destination
We attach each container to a different leaf
We create gre devices in each leafs
Appropriate routes are added in containers and leafs
to achieve end to end connectivity
For a new gre network, it uses the gre device already created in the leafs
