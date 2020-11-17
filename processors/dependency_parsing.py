from pyhanlp import *
from queue import Queue

def build_hpsg_list(head_list):
    """构建hpsg列表，hpsg即在句法依存树中，每个结点所覆盖的idx范围

    Args:
        head_list (list of int): [每个lexicon在句法依存树中的父节点idx]]

    Returns:
        [ [hpsg_span1], [hpsg_span2], ... ]: 即每个lexicon在句法依存树中所覆盖的范围的列表, 且此hpsg_span区间为左闭右闭的
    """
    # tree_list[i] 表示[i]个lexicon的子节点idx， 树节点的编号从1开始。虚拟的root编号为0，所以是 len(head_list) + 1
    tree_list = [[] for i in range(len(head_list) + 1)]
    for cur, parent in enumerate(head_list):
        tree_list[parent].append(cur + 1)
    #而后做一个逆的层次遍历，也就是从叶子节点向上进行层次遍历
    #先用正常的层次遍历，得到从上到小的内部节点，再reverse
    que = Queue()
    que.put(0)
    level_tree_list = []
    hpsg_list = [[] for i in range(len(head_list) + 1)]
    while not que.empty():
        cur = que.get()
        if len(tree_list[cur]) > 0:
            for i in tree_list[cur]:
                que.put(i)
            level_tree_list.append(cur)
        else: #叶子，叶子结点的lexicon覆盖的范围就是它本身
            hpsg_list[cur].extend([cur,cur])
    level_tree_list.reverse()
    # 此时level_tree_list则存着从最底层的内部节点向上到根节点的层次遍历
    for node in level_tree_list:
        min_idx, max_idx = len(head_list) + 1 , 1
        for i in tree_list[node]: #找到当前结点的子节点中，覆盖范围下界的最小值 和 覆盖范围上界的最大值来作为当前节点的覆盖范围
            min_idx = min(min_idx, hpsg_list[i][0])
            max_idx = max(max_idx, hpsg_list[i][1])
        min_idx = min(min_idx, node)
        max_idx = max(max_idx, node)
        hpsg_list[node].extend([min_idx, max_idx])
    # 不返回idx为0的根节点的hpsg_span
    return [tuple(hpsg_span) for hpsg_span in hpsg_list[1:]]

def build_leaves_list(head_list):
    """构建每个lexicon下的叶子list

    Args:
        head_list (list of int): [每个lexicon在句法依存树中的父节点idx]]

    Returns:
        [ [leaves_list1], [leaves_list2], ... ]: 即每个lexicon在句法依存树中结点所包含的叶子list
    """
    # tree_list[i] 表示[i]个lexicon的子节点idx， 树节点的编号从1开始。虚拟的root编号为0，所以是 len(head_list) + 1
    tree_list = [[] for i in range(len(head_list) + 1)]
    for cur, parent in enumerate(head_list):
        tree_list[parent].append(cur + 1)
    #而后做一个逆的层次遍历，也就是从叶子节点向上进行层次遍历
    #先用正常的层次遍历，得到从上到小的内部节点，再reverse
    que = Queue()
    que.put(0)
    level_tree_list = []
    leaves_list = [[] for i in range(len(head_list) + 1)]
    while not que.empty():
        cur = que.get()
        if len(tree_list[cur]) > 0:
            for i in tree_list[cur]:
                que.put(i)
            level_tree_list.append(cur)
        #每个lexicon都要关注它本身, 但是这种写法会让上层结点关注所有子树结点
        # leaves_list[cur].append(cur)
        else: #叶子，叶子结点的lexicon覆盖的范围就是它本身
            leaves_list[cur].append(cur)
    level_tree_list.reverse()
    # 此时level_tree_list则存着从最底层的内部节点向上到根节点的层次遍历
    for node in level_tree_list:
        for i in tree_list[node]: #把当前结点的子结点的leaf_list加入当前结点即可
            leaves_list[node].extend(leaves_list[i])
    # 每个结点还要关注其本身
    for node in level_tree_list:
        leaves_list[node].append(node)

    # 不返回idx为0的根节点的 leaf_list
    return [leaf_list for leaf_list in leaves_list[1:]]

def parse_dependency(input_text):
    parse_rlt = HanLP.parseDependency(input_text)
    lexicon_list = []
    head_list = []
    for word in parse_rlt.iterator():
        head_list.append(word.HEAD.ID)
        lexicon_list.append(word.LEMMA)
    return lexicon_list, head_list
  
def main():
    print(HanLP.parseDependency("浙商银行企业信贷部叶老桂博士则从另一个角度对五道门槛进行了解读。叶老桂认为，对目前国内商业银行而言，"))
    lexicon_list, head_list = parse_dependency("浙商银行企业信贷部叶老桂博士则从另一个角度对五道门槛进行了解读。叶老桂认为，对目前国内商业银行而言，")
    print(build_leaves_list(head_list))

if __name__ == "__main__":
    main()