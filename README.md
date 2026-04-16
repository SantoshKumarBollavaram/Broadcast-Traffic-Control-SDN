# Broadcast Traffic Control using POX

## How to Run

1. Start POX:
cd ~/pox
./pox.py misc.broadcast_control

2. Start Mininet:
sudo mn --topo single,4 --controller=remote --switch ovsk,protocols=OpenFlow10

3. Test:
pingall
h1 ping h2
iperf h1 h2

## Features
- Broadcast detection
- Broadcast limiting
- OpenFlow rule installation
- Performance testing
