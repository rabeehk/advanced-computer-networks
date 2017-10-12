from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()



class MicroFlow(object):
  def __init__(self, connection):
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # stores relation between mac address and port
    self.mac_to_port = {}


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

  def act_like_switch(self, packet, packet_in):
    source = packet.src.toStr()
    dest = packet.dst.toStr()

    self.mac_to_port[source] = packet_in.in_port

    if dest in self.mac_to_port:
      match = of.ofp_match()
      # match every pachet that has this MAC destination
      match.dl_dst = packet.dst

      fm = of.ofp_flow_mod()
      fm.match = match
      fm.in_port = packet_in.in_port
      fm.buffer_id = packet_in.buffer_id
      # set timeout
      fm.hard_timeout = 10
      # set action to send to the associated port
      fm.actions.append(of.ofp_action_output(port = self.mac_to_port[dest]))

      self.connection.send(fm)
    else:
      self.send_packet(packet_in.buffer_id, packet_in.data,
                       of.OFPP_FLOOD, packet_in.in_port)


  def _handle_PacketIn(self, event):
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.act_like_switch(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    MicroFlow(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
