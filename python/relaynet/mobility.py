import math


def calculate_distance(node_a, node_b):
    """
    Calculate Euclidean distance between two nodes.
    """

    dx = node_a.x - node_b.x
    dy = node_a.y - node_b.y

    return math.sqrt(dx ** 2 + dy ** 2)


def calculate_rssi(source, relay):
    """
    Simple RSSI approximation based on distance.

    This is a simplified model for our Python prototype.
    NS-3 will later provide a more realistic radio model.
    """

    distance = calculate_distance(source, relay)

    if distance <= 1:
        return -40.0

    rssi = -40 - (20 * math.log10(distance))

    return max(-100.0, rssi)


def move_node(node, dx, dy):
    """
    Move a node by dx and dy.
    """

    node.x += dx
    node.y += dy