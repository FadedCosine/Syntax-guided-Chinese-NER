import numpy as np

def count_entropy(p):
    normal_p = p / np.sum(p)
    print(normal_p)
    entropy = 0.
    for pi in normal_p:
        entropy -= pi * np.log(pi)
    return entropy

org_p = np.array([0.6, 0.2, 0.1, 0.06, 0.04])
filter_p = np.array([ 0.2, 0.1, 0.06, 0.04])
print(count_entropy(org_p))
print(count_entropy(filter_p))