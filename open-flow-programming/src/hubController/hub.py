from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Hub(object):
  def __init__(self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

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


  def act_like_hub(self, packet, packet_in):
    # flood every message
    self.send_packet(packet_in.buffer_id, packet_in.data,
                     of.OFPP_FLOOD, packet_in.in_port)

  def _handle_PacketIn(self, event):
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.act_like_hub(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Hub(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
