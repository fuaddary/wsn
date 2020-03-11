import random
import wsnsimpy.wsnsimpy_tk as wsp

# SOURCE = [9,49,99,94,90]
SOURCE = [99]
ACTIVE= [1,0,0,0,0,0]
SINK = 0

hole = []
received = []

###########################################################
class MyNode(wsp.Node):
    tx_range = 100

    ##################
    def init(self):
        super().init()
        self.recv = False
        #test initial energy
        self.energy = 100

    ##################
    def run(self):
        # print("node id : "+ str(self.id) + "time now: "+str(sim.now))
        if self.id in SOURCE:
            self.scene.nodecolor(self.id,0,0,0)
            self.recv = True
            yield self.timeout(2)
            self.start_process(self.start_send())
        if self.id == SINK:
            self.scene.nodecolor(self.id,0,1,0)
        else:
            self.scene.nodecolor(self.id,.7,.7,.7)

    ##################
    def on_receive(self, sender, **kwargs):
        self.energy -=2
        self.log(f"Receive message from {sender}")
        if self.id == SINK:
            self.log(f"SINK Received from {sender}")
            received.append(sender)
            print (received)
            return
        self.log(f"New message; prepare to forward")
        self.scene.nodecolor(self.id,1,0,0)
        yield self.timeout(random.uniform(0.5,1.0))
        seq = kwargs['seq']
        self.forward(self.id,seq)

    def forward(self,src,seq):
        self.energy -=5
        self.next = self.get_sgp()
        self.log(f"Forwarded to SINK via {self.next}")
        self.send(self.next, msg='data', src=src, seq=seq)

    def get_sgp(self):
        distances = list()
        for neighbor in self.neighbors:
            if neighbor.id == SINK:
                return SINK
            for distance in neighbor.neighbor_distance_list:
                if distance[1].id == SINK:
                    instances = (distance[0],neighbor)
                    distances.append(instances)
        return min(distances)[1].id

    def start_send(self):
        print(self.id)
        self.scene.clearlinks()
        seq = 0
        while True: 
            yield self.timeout(1)
            self.log(f"start send from source with seq {seq}")
            self.forward(self.id, seq)
            seq += 1
###########################################################
sim = wsp.Simulator(
        until=100,
        timescale=1,
        visual=True,
        terrain_size=(700,700),
        title="Flooding Demo")
for x in range(10):
    for y in range(10):
        px = 50 + x*60 + random.uniform(-20,20)
        py = 50 + y*60 + random.uniform(-20,20)
        node = sim.add_node(MyNode, (px,py))
        node.tx_range = 100
        node.logging = True

sim.run()
