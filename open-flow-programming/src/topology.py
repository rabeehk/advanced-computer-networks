from mininet.topo import Topo

class TopoBasic(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        hosts = []
        for i in ['h1', 'h2', 'h3']:
          hosts.append(self.addHost(i))

        switches = []
        for i in ['s1', 's2']:
          switches.append(self.addSwitch(i))

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])
        self.addLink(switches[0], switches[1])
        self.addLink(hosts[2], switches[1])

class Topo2(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        hosts = []
        for i in ['h1', 'h2', 'h3', 'h4', 'h5']:
          hosts.append(self.addHost(i))

        switches = []
        for i in ['s1', 's2', 's3']:
          switches.append(self.addSwitch(i))

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])

        self.addLink(switches[0], switches[1])
        self.addLink(switches[1], switches[2])

        self.addLink(hosts[2], switches[2])
        self.addLink(hosts[3], switches[2])
        self.addLink(hosts[4], switches[2])

class Topo3(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        hosts = []
        for i in ['h1', 'h2', 'h3', 'h4']:
          hosts.append(self.addHost(i))

        switches = []
        for i in ['s1', 's2', 's3']:
          switches.append(self.addSwitch(i))

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])

        self.addLink(switches[0], switches[1])
        self.addLink(switches[1], switches[2])
        self.addLink(switches[0], switches[2])

        self.addLink(hosts[2], switches[1])
        self.addLink(hosts[3], switches[1])

topos = { 'topo2': (lambda: Topo2()),
          'topo3': (lambda: Topo3()),
          'topo': (lambda: TopoBasic())
          }
