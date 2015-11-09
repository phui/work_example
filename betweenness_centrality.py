# author: Pik-Mai Hui (huip@indiana.edu)
# usage: python betweenness_centrality.py -i input_fpath -o output_path [-d delimiter]
# input should be a edge list of input graph with node id seperated by delimiter
# output format: ("node_id\tbetweenness\tdegree\n")+
import gzip
import networkx as nx
from optparse import OptionParser



if __name__ == '__main__':
    # parse arguments
    parser = OptionParser()

    parser.add_option(
        "-i", "--input", dest="in_fname", help="read from IN", metavar="IN"
    )
    parser.add_option(
        "-o", "--output", dest="out_fname", help="write to OUT", metavar="OUT"
    )
    parser.add_option(
        "-d", "--delim", dest="delimiter", help="set delimiter to DELIM",
        metavar="DELIM"
    )

    (options, args) = parser.parse_args()

    # check parsed arguments
    if options.in_fname is None:
        raise Exception("Please specify input filename with -i option...Exit")
    if options.out_fname is None:
        raise Exception("Please specify output filename with -o option...Exit")

    delim = '\t'
    if options.delimiter is None:
        print "Set delimiter of reader to \\t"
    else:
        print "User-specified delimiter caught"
        delim = options.delimiter

    # read graph input
    G = nx.read_edgelist(options.in_fname, delimiter=delim)

    # extract largest connected component
    largest_subg = sorted(nx.connected_component_subgraphs(G), key=len,
            reverse=True)[0]

    # estimate betweenness centraility
    # algorithm reference :
    # Ulrik Brandes: A Faster Algorithm for Betweenness Centrality. Journal of
    # Mathematical Sociology 25(2):163-177, 2001.
    node_b_centrality = nx.betweenness_centrality(largest_subg, k=15,
            normalized=False)

    # calculate degree for each node
    node_degree = nx.degree(largest_subg)

    # output results in gzip
    fstream = open(options.out_fname, 'wb')
    fgzipped = gzip.GzipFile(mode='wb', fileobj=fstream)
    for node in node_b_centrality.keys():
        fgzipped.write( "%s\t%f\t%d\n" %
                (node, node_b_centrality[node], node_degree[node]) )
    fgzipped.close()
    fstream.close()
