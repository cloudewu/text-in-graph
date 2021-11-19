import os
import networkx as nx
from graph import build_graph, plot_graph

# --- UTILITIES --- #
def ensure_exist(path):
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
            print(f'folder {path} created')
    except:
        return False
    return True

# --- METHODS --- #
def get_node_scores(G, strategy: str):
    return nx.__getattribute__(strategy)(G)

def get_keywords(scores:dict, n:int = None):
    sorted_scores = sorted(scores.items(), key=lambda item: -item[1])
    if not n:
        n = int(len(node_scores) / 3)
    return [token for token, _ in sorted_scores[:n]]

def get_keyphrase(document:list, keywords:list):
    keyphrases = [[]]
    pre_keyword = False
    for sent in document:
        for token in sent:
            if token in keywords:
                keyphrases[-1].append(token)
                pre_keyword = True
            elif pre_keyword:
                keyphrases[-1] = ' '.join(keyphrases[-1])
                keyphrases.append([])
                pre_keyword = False
    
    keyphrases = list(set(keyphrases[:-1]))
    return keyphrases

def save_keyphrases(keyphrases: list, strategy: str, CONFIG: dict):
    if 'dir' not in CONFIG: return False
    num = CONFIG['max'] or 'auto'

    with open(os.path.join(CONFIG['dir'], f'keyphrase.{strategy}.{num}.txt'), 'w') as f:
        f.write('\n'.join(keyphrases))
    return True

def save_keywords(keywords, G, strategy, CONFIG: dict):
    if 'dir' not in CONFIG: return False
    num = CONFIG['max'] or 'auto'
    
    with open(os.path.join(CONFIG['dir'], f'keyword.{strategy}.{num}.txt'), 'w') as f:
        f.write('\n'.join(keywords))
    plot_graph(G, highlight=keywords, show=False, save=os.path.join(CONFIG['dir'], f'graph.{strategy}.{num}.png'))
    return True

# --- MAIN --- #
if __name__ == '__main__':
    from graph import preprocess_document
    from argparse import ArgumentParser
    def parse_args():
        parser = ArgumentParser()
        parser.add_argument('file', help='input document file')
        parser.add_argument('output', type=str, help='the folder to save output')
        # available strategies: https://networkx.org/documentation/stable/reference/algorithms/centrality.html
        parser.add_argument('-s', '--strategy', nargs='+', default=['betweenness_centrality'], help='centrality algorithm')
        parser.add_argument('-m', '--maximum', type=int, help='max keyword numbers')
        return parser.parse_args()
    args = parse_args()

    # ASSERTIONS
    if not os.path.isfile(args.file):
        print(f'[ ERROR ] file {args.file} not exist')
        exit(1)

    # PREPARATIONS
    CONFIG = {
        'input': args.file,
        'dir': args.output,
        'strategy': args.strategy,
        'max': args.maximum,
    }
    ensure_exist(CONFIG['dir'])

    # MAIN
    with open(args.file, 'r') as f:
        document = f.read()
    tokens = preprocess_document(document, stopwords=[], punc='')

    G = build_graph(document, directed = True)
    for strategy in CONFIG['strategy']:
        node_scores = get_node_scores(G, strategy)
        keywords = get_keywords(node_scores, CONFIG['max'])
        save_keywords(keywords, G, strategy, CONFIG)
        phrases = get_keyphrase(tokens, keywords)
        save_keyphrases(phrases, strategy, CONFIG)