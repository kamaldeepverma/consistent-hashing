import hashlib
import binascii
import bisect

class SimpleConsistentHashTable(object):
    def __init__(self, nodelist):
        """Initialize a consistent hash table for the given list of nodes"""
        baselist = [(hashlib.md5(str(node).encode('utf-8')).digest(), node) for node in nodelist]
        # Build two lists: one of (hashvalue, node) pairs, sorted by
        # hashvalue, one of just the hashvalues, to allow use of bisect.
        self.nodelist = sorted(baselist, key=lambda x: x[0])
        self.hashlist = [hashnode[0] for hashnode in self.nodelist]

    def find_nodes(self, key, count=3, avoid=None):
        """Return a list of count nodes from the hash table that are
        consecutively after the hash of the given key, together with
        those nodes from the avoid collection that have been avoided.

        Returned list size is <= count, and any nodes in the avoid collection
        are not included."""
        if avoid is None:  # Use an empty set
            avoid = set()
        # Hash the key to find where it belongs on the ring
        hv = hashlib.md5(str(key).encode('UTF-8')).digest()
        # Find the node after this hash value around the ring, as an index
        # into self.hashlist/self.nodelist
        initial_index = bisect.bisect(self.hashlist, hv)
        next_index = initial_index
        results = []
        avoided = []
        while len(results) < count:
            if next_index == len(self.nodelist):  # Wrap round to the start
                next_index = 0
            node = self.nodelist[next_index][1]
            if node in avoid:
                if node not in avoided:
                    avoided.append(node)
            else:
                results.append(node)
            next_index = next_index + 1
            if next_index == initial_index:
                # Gone all the way around -- terminate loop regardless
                break
        return results

    def __str__(self):
        return ",".join(["(%s, %s)" %
                         (binascii.hexlify(nodeinfo[0]), nodeinfo[1])
                         for nodeinfo in self.nodelist])
    
def preference_list(bucket_name):
    nodeList = ['172.18.16.38', '172.18.16.47', '172.18.16.86', '172.18.16.123']
    sch = SimpleConsistentHashTable(nodeList)
    x = sch.find_nodes(bucket_name)
    return x,nodeList
    #print(sch.hashlist)
