# Deploying Container Network Topology

## Overview:
Python Program creates container leaf-spine topology,<br/>
accepts input from csv file specifying containers and networks ( L2, L3, Vxlan, GRE ) used to connect them to each other,<br/>
creates containers and networks,<br/>
connects them to leaf-spine topology<br/>
and configures routes for achieving end-to-end connectivity.<br/>

![alt text](https://github.com/nikhilkamat2/Docker-Networking/blob/master/Container%20Topology.PNG)
## Requirements:
Docker  
brctl  
iproute2  

## To run:
```
sudo python a.py <numleaf> <numspine> <imagefile> <csvfile>
```
eg.
```
sudo python a.py 2 2 assignmentimage topology.csv
```

numleaf = number of leaf containers<br/>
numspine = number of spine containers<br/>
imagefile = image file used for docker containers<br/>
csvfile = contains data of containers and their networks<br/>
  
```  
sh del.sh 
````
removes the creaated containers, and networking devices for the above command, for the given csvfile.

## Working:
The script uses topology.csv to run<br/>
please modify topology.csv according to input<br/>

The code uses Container and Network class to keep a track<br/>
of the Containers and Networks created.<br/>
The containers and networks are appended to their respective lists.<br/>
The container object has reference to networks it is connected to and<br/>
the network has references to containers that use it.<br/>

IP addresses are assigned incrementally for every newly created network type<br/>

## Creating Leaf and Spine
Creates Leaf containers named leaf0,leaf1...<br/>
Creates Spine containers named spine0,spine1...<br/>
Each leaf container is connected to each spine container by veth pairs<br/>
Appropriate routes are added to achieve end to end connectivity<br/>

## Creating Bridged Networks
Creates containers for source and destination<br/>
Creates a linux bridge using brctl<br/>
Attaches the containers to the bridge using veth pairs<br/>
Attaches the bridge to the leaf using veth pairs<br/>

## Creating L3 Networks
Creates containers for source and destination<br/>
Creates a L3 bridge using docker<br/>
Attaches the containers to the bridge using docker api<br/>
Attaches the bridge to the leaf using using docker api<br/>

## Creating Vxlan  Networks
Creates containers for source and destination<br/>
Creates namespace corresponding to each container<br/>
Creates a bridge in each namespace<br/>
Attaches a Vxlan device to this bridge<br/>
Attaches the containers to the bridge in the namespace<br/>
using veth pairs to connect containers to the namespace,<br/>
then adds that interface to the bridge using brctl api<br/>
Attaches the namespace to the leaf using using veth pairs<br/>
Appropriate routes are added in namespace,leaf and spine<br/>
to achieve end to end connectivity<br/>

## Creating GRE Networks
Creates containers for source and destination<br/>
Attaches each container to a different leaf<br/>
Creates gre devices in each leafs<br/>
Appropriate routes are added in containers and leafs<br/>
to achieve end to end connectivity<br/>
For a new gre network, it uses the gre device already created in the leafs<br/>
