sudo ip link del hw4br0
sudo ip link del hw4br1
sudo ip netns del CSins0
sudo ip netns del CSjns0
sudo ip netns del CSkns1
sudo ip netns del CSlns1

docker stop leaf0
docker stop leaf1
docker stop leaf2
docker stop leaf3
docker stop leaf4

docker rm leaf0
docker rm leaf1
docker rm leaf2
docker rm leaf3
docker rm leaf4

docker stop spine0
docker stop spine1
docker stop spine2
docker stop spine3
docker stop spine4

docker rm spine0
docker rm spine1
docker rm spine2
docker rm spine3
docker rm spine4

docker stop CSa
docker rm CSa
docker stop CSb
docker rm CSb
docker stop CSc
docker rm CSc
docker stop CSd
docker rm CSd
docker stop CSe
docker rm CSe
docker stop CSf
docker rm CSf
docker stop CSg
docker rm CSg
docker stop CSh
docker rm CSh
docker stop CSi
docker rm CSi
docker stop CSj
docker rm CSj
docker stop CSk
docker rm CSk
docker stop CSl
docker rm CSl
docker stop CSm
docker rm CSm
docker stop CSn
docker rm CSn
docker stop CSo
docker rm CSo
docker stop CSp
docker rm CSp
