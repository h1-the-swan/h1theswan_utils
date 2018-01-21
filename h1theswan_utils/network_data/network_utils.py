from timeit import default_timer as timer
from six import string_types
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

def extract_subgraph_from_pajek(fname_pjk, names):
    """Extract the relevant lines from a pajek file (subgraph using a list of <names> that is a subset of the original network)

    :fname_pjk: filename for the pajek file (.net or .pjk)
    :names: list of node names to extract
    :returns: dictionary: vertices -> list of lines representing the vertices;
                            'edges' -> list of lines representing the edges

    """
    lines = {
        'vertices': [],
        'edges': []
    }
    indices = []

    with open(fname_pjk, 'r') as f:
        mode = ''
        new_idx = 0
        old_new_idx_dict = {}
        for i, line in enumerate(f):
            if i in [10, 100, 1000, 10000, 100000, 1000000] or i % 5000000 == 0:
                logger.debug("reading line {}. currently in subgraph: {} vertices and {} edges".format(i, len(lines['vertices']), len(lines['edges'])))
            if line[0] == '*':
                if line[1].lower() == 'v':  # this should happen on the very first line
                    mode = 'v'
                    logger.debug("starting to process vertices. {}".format(line.strip()))
                elif line[1].lower() in ['a', 'e']:  # 'arcs' or 'edges'
                    indices = set(indices)
                    mode = 'e'
                    logger.debug("starting to process edges. {}".format(line.strip()))
                continue

            if mode == 'v':
                items = line.strip().split(' ')
                this_index = items[0]
                this_name = items[1].strip('"')
                if this_name in names:
                    new_idx += 1   # we want the new idx to start at 1
                    indices.append(this_index)
                    old_new_idx_dict[this_index] = new_idx
                    output_line = ' '.join([str(new_idx)] + items[1:])
                    output_line = output_line + '\n'
                    lines['vertices'].append(output_line)
            elif mode == 'e':
                # edges
                items = line.strip().split(' ')
                source_index = items[0]
                # we only care if both source and target are in this line
                if source_index in indices:
                    target_index = items[1]
                    if target_index in indices:
                        source_index_new = old_new_idx_dict[source_index]
                        target_index_new = old_new_idx_dict[target_index]
                        output_line = ' '.join([str(source_index_new), str(target_index_new)])
                        output_line = output_line + '\n'
                        lines['edges'].append(output_line)
    return lines

def write_pajek_from_full_lines(lines, outfname, vertices_label='vertices', edges_label='arcs'):
    """Given the full lines of the pajek file (as generated from extract_subgraph_from_pajek()), write pajek to file

    :lines: dictionary: vertices -> list of lines representing the vertices;
                            'edges' -> list of lines representing the edges
    :outfname: filename for the output pajek (.net)

    The lines in <lines> should contain newline characters at the end of each line

    """
    with open(outfname, 'w') as outf:
        num_vertices = len(lines['vertices'])
        logger.debug('writing {} {}...'.format(num_vertices, vertices_label))
        outf.write('*{} {}\n'.format(vertices_label, num_vertices))
        for line in lines['vertices']:
            outf.write(line)

        num_edges = len(lines['edges'])
        logger.debug('writing {} {}...'.format(num_vertices, edges_label))
        outf.write('*{} {}\n'.format(edges_label, num_edges))
        for line in lines['edges']:
            outf.write(line)

def extract_subgraph_from_pajek_and_write_to_pajek(input_fname, 
                                                    subset_names, 
                                                    output_fname, 
                                                    vertices_label='vertices', 
                                                    edges_label='arcs'):
    lines = extract_subgraph_from_pajek(input_fname, subset_names)
    write_pajek_from_full_lines(lines, output_fname, vertices_label=vertices_label, edges_label=edges_label)

def edgelist_to_pajek(f, sep='\t', header=True, temp_dir=None, weighted=False):
    """Convert an edgelist file to Pajek form.
    Takes a file containing an edgelist, and return a PajekFactory object.
    To write the pajek (.net) file, call write() on the PajekFactory, e.g.:
    pjk = edgelist_to_pajek(edgelist_file)
    with open(pajek_fname, 'w') as outf:
        pjk.write(outf)

    :f: edgelist file object or filename
    :sep: delimiter for the edgelist file
    :header: boolean. Does the edgelist file contain a header row
    :temp_dir: (optional) Directory for a temporary file used by the PajekFactory
    :weighted: boolean. Denotes a weighted network. If the network is unweighted, the input file should have two columns. If weighted, the input edgelist should have three columns.
    :returns: PajekFactory object

    """
    from . import PajekFactory
    pjk = PajekFactory(temp_dir=temp_dir, weighted=weighted)
    if isinstance(f, string_types):
        f = open(f, 'r')
        close_at_end = True
    else:
        close_at_end = False
    rownum = 0
    for i, line in enumerate(f):
        if header is True and i == 0:
            continue
        split = line.strip().split(sep)
        if weighted is True:
            pjk.add_edge(split[0], split[1], weight=split[2])
        else:
            pjk.add_edge(split[0], split[1])
        rownum += 1
        if (rownum in [1,5,10,50,100,1000,10000,100000,1e6,10e6] or (rownum % 50e6 == 0)):
            logger.debug('{} edges added'.format(rownum))
    logger.debug("done. {} edges added".format(rownum))
    if close_at_end:
        f.close()
    return pjk
