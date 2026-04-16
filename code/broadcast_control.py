from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

BROADCAST_LIMIT = 20   # keep high for stable ping
broadcast_count = {}
mac_to_port = {}


def _handle_ConnectionUp(event):
    log.info("Switch %s connected", event.connection.dpid)


def _handle_PacketIn(event):
    packet = event.parsed
    dpid = event.connection.dpid
    in_port = event.port

    if not packet.parsed:
        return

    mac_to_port.setdefault(dpid, {})
    broadcast_count.setdefault(dpid, 0)

    src = packet.src
    dst = packet.dst

    # Learn MAC
    mac_to_port[dpid][src] = in_port

    # 🚨 Broadcast detection
    if dst.is_broadcast:
        broadcast_count[dpid] += 1
        log.info("Broadcast detected (Count %d)", broadcast_count[dpid])

        # Limit broadcast
        if broadcast_count[dpid] > BROADCAST_LIMIT:
            log.warning("Dropping broadcast packet")
            return

        out_port = of.OFPP_FLOOD

    else:
        # Selective forwarding
        if dst in mac_to_port[dpid]:
            out_port = mac_to_port[dpid][dst]
        else:
            out_port = of.OFPP_FLOOD

    # Install flow rule
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet, in_port)
    msg.actions.append(of.ofp_action_output(port=out_port))
    event.connection.send(msg)

    # Send packet
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=out_port))
    event.connection.send(msg)


def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Broadcast Traffic Control Loaded")
