from classes.consts import ADNETWORKS_full, MAX_PRICE
from classes.node import Node

class Layer:

    def __init__(self, layer_id = None, serial_start = 0):

        self.nodes = []
        self.layer_id = layer_id

        for adnetwork in ADNETWORKS_full:
            for price in range(MAX_PRICE):
                node = Node(adnetwork, layer_id, serial_start, price)
                self.nodes.append(node)
                serial_start += 1

    def get_node_by_id(self, id):
        """return the found node according to id"""
        found_node = None
        for node in self.nodes:
            if node.node_id == id:
                found_node = node
                break
        return found_node