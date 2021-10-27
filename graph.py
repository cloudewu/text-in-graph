import re
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

def ngram(tokens, n=2):
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n-1)]

def preprocess_document(document):
    """
    1. splitted by spaces and punctuations
    2. punctuations are all removed
    3. stop words are removed (https://gist.github.com/sebleier/554280)
    """
    document = document.lower()
    document = re.findall(r'\w+', document)
    document = list(filter(lambda token: token not in STOPWORDS, document))
    return document

def get_entities(document):
    """ Generate nodes on the graph, which should be all unique words """
    unique_words = list(set(document))
    return unique_words

def get_relations(document, weighted=False):
    """ Generate edges on the graph, which should be all bigram connections """
    bigrams = ngram(document, 2)
    bigrams = Counter(bigrams)
    if not weighted:
        return [ gram.split(' ')  for gram in bigrams ]
    return [ [*gram.split(' '), count] for gram, count in bigrams.items() ]

def build_graph(doc, directed = False, weighted = False):
    pdoc = preprocess_document(doc)
    
    nodes = get_entities(pdoc)
    edges = get_relations(pdoc, weighted)
    
    # create graph structure with NetworkX
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(nodes)
    if weighted:
        G.add_weighted_edges_from(edges)
    else:
        G.add_edges_from(edges)
    
    return G

def plot_graph(G, title=None):
    """ 
    Display graph on the notebook. 
    Some errors may come up in `nx.draw_networkx_edge_labels`;
      you need to install graphviz first and then pygraphviz, 
      and make sure your graphviz installation is in your system path. (See the first cell)
    """
    
    # set figure size
    plt.figure(figsize=(10,10))
    
    # define position of nodes in figure
    pos = nx.nx_agraph.graphviz_layout(G)
    
    # draw nodes and edges
    nx.draw(G, pos=pos, with_labels=True)
    
    # get edge labels (if any)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    
    # draw edge labels (if any)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # plot the title (if any)
    plt.title(title)
    
    plt.show()
    return

def print_highest(scores: dict, n=10):
    sorted_scores = sorted(scores.items(), key=lambda item: -item[1])
    print(f' word           score')
    print(f'---------------------')
    for idx, (token, score) in enumerate(sorted_scores):
        if idx > n: break
            
        print(f'{token:15} {score:.2f}')

if __name__ == '__main__':
    import os
    from argparse import ArgumentParser
    def parse_args():
        parser = ArgumentParser()
        parser.add_argument('file', help='input document file')
        parser.add_argument('-s', '--stop-words', help='file containing a list of stop words')
        return parser.parse_args()
    args = parse_args()

    # ASSERTIONS
    if not os.path.isfile(args.file):
        print(f'[ ERROR ] file {args.file} not exist')
        exit(1)
    
    if args.stop_words and not os.path.isfile(args.stop_words):
        print(f'[ ERROR ] file {args.stop_words} not exist')
        exit(1)


    # PREPARATIONS
    if args.stop_words:
        with open(args.stop_words, 'r') as f:
            STOPWORDS = f.read().split()

    with open(args.file, 'r') as f:
        document = f.read() 


    # MAIN
    G = build_graph(document)
    node_scores = nx.betweenness_centrality(G)
    print_highest(node_scores, 20)

