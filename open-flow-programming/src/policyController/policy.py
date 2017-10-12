from pox.core import core
from pox.lib.packet.arp import arp
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *

import pox.lib.packet as pkt
import pox.openflow.discovery

log = core.getLogger()

IP_H4 = "10.0.0.4"

dpid_to_name = {}
port_to_name = {}
name_to_port = {}

macH4 = None
macH3 = None

class Policy(EventMixin):
 
  def __init__(self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection


    self.mac_to_port = {}

    # This binds our PacketIn event listener
    connection.addListeners(self)
    core.openflow_discovery.addListeners(self)

  def send_packet(self, buffer_id, raw_data, out_port, in_port):
    msg = of.ofp_packet_out()
    msg.in_port = in_port
    if buffer_id != -1 and buffer_id is not None:
      # We got a buffer ID from the switch; use that
      msg.buffer_id = buffer_id
    else:
      # No buffer ID from switch -- we got the raw data
      if raw_data is None:
        # No raw_data specified -- nothing to send!
        return
      msg.data = raw_data

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

  def act_like_switch(self, packet, packet_in, switch_name):
    source = packet.src.toStr()
    dest = packet.dst.toStr()

    # the default is to save the source MAC address with the incoming port
    mac = source
    port = packet_in.in_port
    global macH4

    if switch_name == "s1":
      # must be sure we add this micro flow
      self.mac_to_port[macH4] = name_to_port[switch_name]['s3']

      # set the out port for H4 to be to s3
      if source == macH4:
        mac = macH4
        port = name_to_port[switch_name]['s3']
    elif switch_name == 's2':
      # set the out port for messages for H4 to be to s1, if packet came from s3
      if dest == macH4 and \
          packet_in.in_port == name_to_port[switch_name]['s3']:
        mac = source
        port = name_to_port[switch_name]['s1']
    else: # s3
      # send packet to s2 if it came from s1 and is to H4
      if dest == macH4 and \
          packet_in.in_port == name_to_port[switch_name]['s1']:
        mac = macH4
        port = name_to_port[switch_name]['s2']
      else:
        return

    self.mac_to_port[mac] = port

    if dest in self.mac_to_port:
      #      log.debug("in %s send %s to %d" % (switch_name, dest, self.mac_to_port[dest]))
      self.send_packet(packet_in.buffer_id, packet_in.data,
                       self.mac_to_port[dest], packet_in.in_port)
    else:
      self.send_packet(packet_in.buffer_id, packet_in.data,
                       of.OFPP_FLOOD, packet_in.in_port)

  def _handle_ConnectionUp(self, event):
    # we need to find out the name of the switch - can figure it out
    # from the list of ports
    for p in event.ofp.ports:
      if p.name.find("-") == -1:
        dpid_to_name[event.dpid] = p.name

    curName = dpid_to_name[event.dpid]

    port_to_name[curName] = {}
    name_to_port[curName] = {}

  def _handle_LinkEvent(self, event):
    # we have a new link
    l = event.link

    # remember association between the port id and the switch name
    port_to_name[dpid_to_name[l.dpid1]][event.portForDPID(l.dpid1)] = \
        dpid_to_name[l.dpid2]
    name_to_port[dpid_to_name[l.dpid1]][dpid_to_name[l.dpid2]] = \
        event.portForDPID(l.dpid1)

  def _handle_PacketIn(self, event):
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp


    srcip = None
    dstip = None
    if packet.find('arp'):
      srcip = packet.find('arp').protosrc
      dstip = packet.find('arp').protodst
    elif packet.find(pkt.ipv4):
      srcip = packet.find(pkt.ipv4).srcip
      dstip = packet.find(pkt.ipv4).dstip
    else:
      return

    global macH4, macH3

    #log.debug("received %s with %s to %s" % (dpid_to_name[event.dpid], str(packet.src), str(packet.dst)))

    # we need to find the mac address of H4 - we do this by checking the source IP
    if srcip == IP_H4:
      if macH4 == None:
        macH4 = packet.src.toStr()
    if dstip == IP_H4 and packet.dst.toStr() != 'ff:ff:ff:ff:ff:ff':
      if macH4 == None:
        macH4 = packet.dst

    self.act_like_switch(packet, packet_in, dpid_to_name[event.dpid])

def launch ():
  """
  Starts the component
  """

  pox.openflow.discovery.launch()
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Policy(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
