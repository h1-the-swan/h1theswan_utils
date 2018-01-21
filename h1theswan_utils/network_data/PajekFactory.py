from .AutoID import AutoID
from shutil import copyfileobj
from tempfile import TemporaryFile


class PajekFactory(object):
    """Factory to build a Pajek file"""

    def __init__(self, 
                    edge_stream=None, 
                    node_stream=None, 
                    weighted=False,
                    temp_dir=None, 
                    vertices_label='Vertices', 
                    edges_label='Arcs'):
        """Build a Pajek Writer.

        Args:
            edge_stream: If provided, a stream that edges will be written to. Otherwise a temporary file is used.
            node_stream: If provided, a stream that nodes will be written to. Otherwise a temporary file is used.
            weighted: True for weighted networks. Default is False.
            temp_dir: If provided, the directory to write temporary files to.
            vertices_label: label to use for the Vertices section of the output file. Default: 'Vertices'
            edges_label: label to use for the Edges section fo the output file. Note: directed graphs should use 'Arcs'. Undirected graphs should use 'Edges'. Default: 'Arcs'
        """
        self.ids = AutoID(first_id=1)
        self.edge_stream = edge_stream
        self.node_stream = node_stream
        self.weighted = weighted

        self.vertices_label = vertices_label
        self.edges_label = edges_label

        if not self.edge_stream:
            self.edge_stream = TemporaryFile("w+", dir=temp_dir)
        if not self.node_stream:
            self.node_stream = TemporaryFile("w+", dir=temp_dir)

        self.edge_count = 0

    def add_edge(self, source, dest, weight=1):
        """Add an edge from source to dest.

        Names, **not** ids should be used here.

        Args:
            source: Name of the source node
            dest: Name of the destination node

        Returns:
            None
        """

        if self.weighted is False and weight != 1:
            raise ValueError("Illegal `weight` argument given: {}. This should be an unweighted network. For a weighted network, set PajekFactory.weighted to True".format(weight))

        write_source = source not in self.ids
        sid = self.ids[source]

        write_dest = dest not in self.ids
        did = self.ids[dest]

        #TODO: Make a version of AutoID that just writes out nodes for us
        if write_source:
            self.node_stream.write('%s "%s"\n' % (sid, source))
        if write_dest:
            self.node_stream.write('%s "%s"\n' % (did, dest))

        if self.weighted is True:
            self.edge_stream.write("%s %s %s\n" % (sid, did, weight))
        else:
            self.edge_stream.write("%s %s\n" % (sid, did))
        self.edge_count += 1

    def write(self, output, vertices_label=None, edges_label=None):
        """Write pajek file to output"""
        self.edge_stream.seek(0)
        self.node_stream.seek(0)

        vertices_label = vertices_label or self.vertices_label
        edges_label = edges_label or self.edges_label

        output.write("*{} {}\n".format(vertices_label, len(self.ids)))
        copyfileobj(self.node_stream, output)
        output.write("*{} {}\n".format(edges_label, self.edge_count))
        copyfileobj(self.edge_stream, output)

    def __str__(self):
        return "<PJK {} vertices, {} edges>".format(len(self.ids), self.edge_count)
