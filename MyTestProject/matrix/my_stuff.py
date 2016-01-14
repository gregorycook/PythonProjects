def reverse_index(L):
    result={}
    for (index, words) in enumerate(L):
        word_list = set(words.split())
        for word in word_list:
            if not word in result:
                result[word] = set()
            result[word].add(index)
    return result

def orSearch(reverse_index, word_list):
    result = set()
    for word in word_list:
        result = result | reverse_index[word]
    return result


def andSearch(reverse_index, word_list):
    result = set()
    for x in reverse_index.values():
        result = result | x
    for word in word_list:
        result = result & reverse_index[word]
    return result

def myFilter(L, num):
    return [x for x in L if (x%num)!=0]

def myLists(L): return [[y+1 for y in list(range(x))] for x in L]

def myFunctionComposition(f, g): return {k:g[f[k]] for k in f.keys()}
