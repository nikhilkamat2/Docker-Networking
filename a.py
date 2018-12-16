import docker as d
import os
import random
import sys

#List for Storing Things
containerlist=[]
networklist=[]

leaflist=[]
spinelist=[]

#Counters for Counting
ipcount=0

brcount=0
bripcount=1

l3count=0

nscount=0
nsipcount=1
nslcount=0

numleaf=int(sys.argv[1])
numspine=int(sys.argv[2])
imagefile=sys.argv[3]
csvfile=sys.argv[4]

#Class Container
class container():
    def __init__(self,name,con):
        self.name=name
        self.id=""
        self.pid=""
        self.image=""
        self.con=con
        self.network=[]

#Network Class
class netwk():
    def __init__(self):
        self.name=""
        self.oftype=""
        self.ip=[]
        self.containers=[]

def createcontainer(name,host):
    #Create Container
    #Find it's pid
    #Store in in Containerlist
     con=host.containers.run(image=imagefile,tty=True,detach=True,stdin_open=True,privileged=True,name=name)
     cont=container(name,con)
     cont.id=con.id
     containerlist.append(cont)
     out=os.popen("sudo docker inspect --format '{{.State.Pid}}' "+name).read()
     cont.pid=str(out)
     return cont

def createvethbwncon(host,con1,con2):
    #Create veth Between Containers
    global ipcount
    v1=con1.name+"to"+con2.name
    v2=con2.name+"to"+con1.name
    v1ip="192.168."+str(ipcount)+".1"
    v2ip="192.168."+str(ipcount)+".2"
    #Create Veth Pair
    com1=run("sudo ip link add "+v1+" type veth peer name "+v2)
    #Attach Veth Pair
    com2=run("sudo ip link set "+v1+" netns "+con1.pid)
    com3=run("sudo ip link set "+v2+" netns "+con2.pid)

    execrun(con1.con,"ip addr add "+v1ip+"/24 dev "+v1)
    execrun(con1.con,"ip link set "+v1+" up")
    execrun(con2.con,"ip addr add "+v2ip+"/24 dev "+v2)
    execrun(con2.con,"ip link set "+v2+" up")

    #Create a Network Veth and Put it in Containers and Containers in Network
    veth=netwk()
    veth.name=v1+'/'+v2
    veth.ip.append(v1ip)
    veth.ip.append(v2ip)
    veth.containers.append(con1)
    veth.containers.append(con2)
    con1.network.append(veth)
    con2.network.append(veth)
    networklist.append(veth)

    ipcount=ipcount+1

#To run commands on containers
def execrun(container,command):
    container.exec_run(command, stdin=True, privileged=True, detach=True)

#To run comannds on System
def run(command):
    com=os.system(command)
    return com

def createleafspine(host,numleaf,numspine):
    #Creating Leaf and Spine Containers
    #Attaching each Leaf Container with each spine container

    #Create Leaf Containers
    for i in range(numleaf):
        name='leaf'+str(i)
        leaf=createcontainer(name,host)
        leaflist.append(leaf)
        #Create Spine Containers
        for i in range(numspine):
            name='spine'+str(i)
            flag=0
            #Use SpineList Here
            for container in containerlist:
                if(container.name==name):
                   spine=container
                   flag=1
            if flag==0:
                spine=createcontainer(name,host)
                spinelist.append(spine)
            createvethbwncon(host,leaf,spine)

    #Adding Routes to Achieve Connectivity
    addroutes(host)

def addroutes(host):
    #Function for Establishing Connectivity between Leaves and Spines
    i=0
    for i in range(len(leaflist)):
        l1=leaflist[i]
        for j in range(i+1,len(leaflist)):
            l2=leaflist[j]
            for k in range(0,len(l1.network)):
                r1ip1,r1ip2,r2ip1,r2ip2=parseip(l2.network[k].ip[0],l1.network[k].ip[1])
                execrun(l1.con,"ip route add "+r1ip1+"/24 via "+r1ip2)
                execrun(l2.con,"ip route add "+r2ip1+"/24 via "+r2ip2)

def parseip(ip1,ip2):
    R1IP1=list(ip1)
    R1IP2=list(ip2)
    R2IP1=list(ip2)
    R2IP2=list(ip1)
    R1IP1[10]='0'
    R1IP2=R1IP2[0:11]
    R2IP1[10]='0'
    R2IP2=R2IP2[0:11]
    R2IP2[10]='2'
    r1ip1="".join(R1IP1)
    r1ip2="".join(R1IP2)
    r2ip1="".join(R2IP1)
    r2ip2="".join(R2IP2)
    return r1ip1,r1ip2,r2ip1,r2ip2

def createvethbwnconbr(con,bridge):
    global brcount
    global bripcount
    v1=con.name+"to"+bridge.name
    v2=bridge.name+"to"+con.name
    #Create Veth Pair
    com1=run("sudo ip link add "+v1+" type veth peer name "+v2)
    #Attach Veth Pair To Container
    com2=run("sudo ip link set "+v1+" netns "+con.pid)
    execrun(con.con,"ip addr add 10.10."+str(brcount)+"."+str(bripcount)+"/24 dev "+v1)
    bripcount=bripcount+1
    execrun(con.con,"ip link set "+v1+" up")
    #Attach Veth Pair to Bridge
    com3=run("sudo brctl addif "+bridge.name+" "+v2)
    com3=run("sudo ip link set "+v2+" up")

def createnetwork(host,source,dest,network):
    if(network=="Bridge"):
        createnetworkbridge(host,source,dest)
    elif(network=="L3"):
        createnetworkl3(host,source,dest)
    elif(network=="VXLAN"):
        createnetworkvxlan(host,source,dest)
    elif(network=="GRE"):
        createnetworkgre(host,source,dest)

def createbridge(bridge):
    com1=run("sudo brctl addbr "+bridge.name)
    com2=run("sudo ip link set "+bridge.name+" up")
    com3=run("sudo ip addr add "+bridge.ip+" dev "+bridge.name)

def createnetworkbridge(host,source,dest):
    global brcount
    global bripcount
    bripcount=1
    print("Creating Bridge Network")
    #Create Containers
    scon=createcontainer(source,host)
    dcon=createcontainer(dest,host)
    #Create Bridge
    bridgename='hw4br'+str(brcount)
    bridge=netwk()
    bridge.name=bridgename
    bridge.oftype='Bridge'
    bridge.ip="10.10."+str(brcount)+"."+str(bripcount)+"/24"
    createbridge(bridge)
    bripcount=bripcount+1
    #Attach Containers to Bridge
    createvethbwnconbr(scon,bridge)
    createvethbwnconbr(dcon,bridge)
    #Attach Bridge to Leaf
    leafno=random.randint(0,numleaf-1)

    for container in containerlist:
        if(container.name=='leaf'+str(leafno)):
            createvethbwnconbr(container,bridge)

    brcount=brcount+1

def createnetworkl3(host,source,dest):
    print("Creating l3 Network")
    global l3count

    #Create Network
    name='hw4net'+str(l3count)
    l3network=host.networks.create(name)
    l3count=l3count+1

    #Create Containers
    scon=createcontainer(source,host)
    dcon=createcontainer(dest,host)

    #Connect Network to Containers
    l3network.connect(scon.name)
    l3network.connect(dcon.name)

    leafno=random.randint(0,numleaf-1)

    for container in containerlist:
        if(container.name=='leaf'+str(leafno)):
            l3network.connect(container.name)

def createvethbwnconns(con,nsname,hasbridge):
    global nslcount
    global nsipcount
    v1=con.name+"to"+nsname
    v2=nsname+"to"+con.name
    v1ip="10.11."+str(nslcount)+"."+str(nsipcount)
    nsipcount=nsipcount+1
    if(hasbridge!=1):
        v2ip="10.11."+str(nslcount)+"."+str(nsipcount)
        nsipcount=nsipcount+1

    #Create Veth Pair
    com1=run("sudo ip link add "+v1+" type veth peer name "+v2)
    #Attach Veth Pair To Container
    com2=run("sudo ip link set "+v1+" netns "+con.pid)
    execrun(con.con,"ip addr add "+v1ip+"/24 dev "+v1)
    execrun(con.con,"ip link set "+v1+" up")
    #Attach Veth Pair to NameSpace
    com3=run("sudo ip link set "+v2+" netns "+nsname)
    if(hasbridge!=1):
        com4=run("sudo ip netns exec "+nsname+" ip addr add "+v2ip+"/24 dev "+v2)
    com5=run("sudo ip netns exec "+nsname+" ip link set "+v2+" up")

    #Store Info for Later Use 
    veth=netwk()
    veth.name=v1+'/'+v2
    veth.ip.append(v1ip)
    if(hasbridge!=1):
        veth.ip.append(v2ip)
    veth.containers.append(con)
    veth.containers.append(nsname)
    con.network.append(veth)
    networklist.append(veth)

    return veth

def createnetworkvxlan(host,source,dest):
    print("Creating Vxlan Network")
    global nscount
    global nslcount

    #Create Containers
    scon=createcontainer(source,host)
    dcon=createcontainer(dest,host)

    #Create Namespaces
    ns1name=scon.name+'ns'+str(nscount)
    ns2name=dcon.name+'ns'+str(nscount)
    com1=run("sudo ip netns add "+ns1name)
    com2=run("sudo ip netns add "+ns2name)

    #Veth between Containers and Namespace
    #1,0 specify if it has a bridge or not
    vethscon=createvethbwnconns(scon,ns1name,1)
    vethdcon=createvethbwnconns(dcon,ns2name,1)
    nslcount=nslcount+1
    #Attach Namespace to Leaf
    vethleaf0=createvethbwnconns(leaflist[0],ns1name,0)
    vethleaf1=createvethbwnconns(leaflist[1],ns2name,0)
    nslcount=nslcount+1

    #Create Bridge in NameSpace
    bridge1=scon.name+'br'
    bridge2=dcon.name+'br'

    run("sudo ip netns exec "+ns1name+" brctl addbr "+bridge1)
    run("sudo ip netns exec "+ns2name+" brctl addbr "+bridge2)

    run("sudo ip netns exec "+ns1name+" ip link set "+bridge1+" up")
    run("sudo ip netns exec "+ns2name+" ip link set "+bridge2+" up")

    if1=vethscon.name.split('/')[1]
    if2=vethdcon.name.split('/')[1]

    run("sudo ip netns exec "+ns1name+" brctl addif "+bridge1+" "+if1)
    run("sudo ip netns exec "+ns2name+" brctl addif "+bridge2+" "+if2)

    #Create Vxlan in NameSpace
    vxlans=scon.name+"vxl"+str(nscount)
    vxland=dcon.name+"vxl"+str(nscount)
    vxlid=50+nscount
    vxldp=4900+nscount

    dev1=vethleaf0.name.split('/')[1]
    dev2=vethleaf1.name.split('/')[1]

    run("sudo ip netns exec "+ns1name+" ip link add name "+vxlans+" type vxlan id "+str(vxlid)+" dev "+dev1+" remote "+vethleaf1.ip[1]+" dstport "+str(vxldp))
    run("sudo ip netns exec "+ns1name+" ip link set dev "+vxlans+" up")
    run("sudo ip netns exec "+ns1name+" brctl addif "+bridge1+" "+vxlans)

    run("sudo ip netns exec "+ns2name+" ip link add name "+vxland+" type vxlan id "+str(vxlid)+" dev "+dev2+" remote "+vethleaf0.ip[1]+" dstport "+str(vxldp))
    run("sudo ip netns exec "+ns2name+" ip link set dev "+vxland+" up")
    run("sudo ip netns exec "+ns2name+" brctl addif "+bridge2+" "+vxland)
    #Add Routes

    #Route in Namespace1
    remoteip1=vethleaf1.ip[1]
    remoteip2=vethleaf0.ip[1]

    run("sudo ip netns exec "+ns1name+" ip route add "+remoteip1+" via "+vethleaf0.ip[0])

    #Route in Namespace2
    run("sudo ip netns exec "+ns2name+" ip route add "+remoteip2+" via "+vethleaf1.ip[0])

    #Route in Leaf0
    l0ip1=leaflist[0].network[0].ip[0]
    l0ip2=leaflist[0].network[0].ip[1]

    execrun(leaflist[0].con,"ip route add "+remoteip1+" via "+l0ip2)

    #Route in Leaf1
    l1ip1=leaflist[1].network[0].ip[0]
    l1ip2=leaflist[1].network[0].ip[1]

    execrun(leaflist[1].con,"ip route add "+remoteip2+" via "+l1ip2)

    #Route in Spine0
    execrun(spinelist[0].con,"ip route add "+remoteip1+" via "+l1ip1)
    execrun(spinelist[0].con,"ip route add "+remoteip2+" via "+l0ip1)

    nscount=nscount+1

def createnetworkgre(host,source,dest):
    print("Creating gre Network")

    #Create Containers
    scon=createcontainer(source,host)
    dcon=createcontainer(dest,host)

    #Attach Containers to Leafs
    leaf0=leaflist[0]
    leaf1=leaflist[1]
    createvethbwncon(host,scon,leaf0)
    createvethbwncon(host,dcon,leaf1)

    grename=""
    greflag=0
    for network in networklist:
        if ( network.name == "gretun" ):
            greflag=1
            break

    if greflag==0:
        #Create GRE in Leafs
        #Leaf0
        local0=leaf0.network[0].ip[0]
        remote0=leaf1.network[0].ip[0]
        gre=netwk()
        grename="gretun"
        gre.name=grename
        execrun(leaf0.con,"ip tunnel add "+grename+" mode gre local "+local0+" remote "+remote0)
        execrun(leaf0.con,"ip link set dev "+grename+" up")
        #Leaf1
        local1=leaf1.network[0].ip[0]
        remote1=leaf0.network[0].ip[0]
        execrun(leaf1.con,"ip tunnel add "+grename+" mode gre local "+local1+" remote "+remote1)
        execrun(leaf1.con,"ip link set dev "+grename+" up")
        networklist.append(gre)
    else:
        grename="gretun"

    #Add Routes
    #Scon
    sconip1=dcon.network[0].ip[0]
    sconip2=scon.network[0].ip[1]

    execrun(scon.con,"ip route add "+sconip1+" via "+sconip2)

    #Dcon
    dconip1=scon.network[0].ip[0]
    dconip2=dcon.network[0].ip[1]

    execrun(dcon.con,"ip route add "+dconip1+" via "+dconip2)

    #Leaf0
    execrun(leaf0.con,"ip route add "+sconip1+" dev "+grename)

    #Leaf1
    execrun(leaf1.con,"ip route add "+dconip1+" dev "+grename)


if __name__=="__main__":
    host=d.from_env()
    createleafspine(host,numleaf,numspine)
    topo=open(csvfile,'r')
    for line in topo.read().splitlines():
        source=line.split(', ')[0]
        dest=line.split(', ')[1]
        network=line.split(', ')[2]
        createnetwork(host,source,dest,network)

