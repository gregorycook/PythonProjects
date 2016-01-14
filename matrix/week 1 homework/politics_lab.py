from vec import Vec
import math

voting_data = list(open("voting_record_dump109.txt"))

## print(voting_data)

## Task 1

def create_voting_dict():
    """
    Input: None (use voting_data above)
    Output: A dictionary that maps the last name of a senator
            to a list of numbers representing the senator's voting
            record.
    Example: 
        >>> create_voting_dict()['Clinton']
        [-1, 1, 1, 1, 0, 0, -1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, 1]

    This procedure should return a dictionary that maps the last name
    of a senator to a list of numbers representing that senator's
    voting record, using the list of strings from the dump file (strlist). You
    will need to use the built-in procedure int() to convert a string
    representation of an integer (e.g. '1') to the actual integer
    (e.g. 1).

    You can use the split() procedure to split each line of the
    strlist into a list; the first element of the list will be the senator's
    name, the second will be his/her party affiliation (R or D), the
    third will be his/her home state, and the remaining elements of
    the list will be that senator's voting record on a collection of bills.
    A "1" represents a 'yea' vote, a "-1" a 'nay', and a "0" an abstention.

    The lists for each senator should preserve the order listed in voting data. 
    """
    result={}
    for line in voting_data:
        record=[int(thing) for (index, thing) in enumerate(line.split()) if index >= 3]
        name=line.split()[0]
        result[name]=record.copy()
    return result
    
dict_voting = create_voting_dict()

def get_voting_vec1(record):
    return Vec(set(range(len(record))), {k:v for (k,v) in enumerate(record)})

def get_voting_vec2(sen, voting_dict):
    return get_voting_vec1(voting_dict[sen])

def get_similarity(sen1, sen2, voting_dict):
    return get_voting_vec2(sen1, voting_dict) * get_voting_vec2(sen2, voting_dict)

## Task 2

def policy_compare(sen_a, sen_b, voting_dict):
    """
    Input: last names of sen_a and sen_b, and a voting dictionary mapping senator
           names to lists representing their voting records.
    Output: the dot-product (as a number) representing the degree of similarity
            between two senators' voting policies
    Example:
        >>> voting_dict = {'Fox-Epstein':[-1,-1,-1,1],'Ravella':[1,1,1,1]}
        >>> policy_compare('Fox-Epstein','Ravella', voting_dict)
        -2
    """
    voting_a = get_voting_vec2(sen_a, voting_dict)
    ## print(voting_a)
    voting_b = get_voting_vec2(sen_b, voting_dict)
    ## print(voting_b)
    return voting_a*voting_b

## print(policy_compare("Murray", "Crapo", dict_voting))

## Task 3

def most_similar(sen, voting_dict):
    """
    Input: the last name of a senator, and a dictionary mapping senator names
           to lists representing their voting records.
    Output: the last name of the senator whose political mindset is most
            like the input senator (excluding, of course, the input senator
            him/herself). Resolve ties arbitrarily.
    Example:
        >>> vd = {'Klein': [1,1,1], 'Fox-Epstein': [1,-1,0], 'Ravella': [-1,0,0]}
        >>> most_similar('Klein', vd)
        'Fox-Epstein'

    Note that you can (and are encouraged to) re-use you policy_compare procedure.
    """
    most_closely_related_record = 0
    most_closely_related_name = ""
    for name in voting_dict:
        similarity = get_similarity(sen, name, voting_dict)
        if (similarity > most_closely_related_record) & (name!=sen):
            most_closely_related_record = similarity
            most_closely_related_name = name
    return most_closely_related_name

## print(most_similar("Murray", dict_voting))   

## Task 4

def least_similar(sen, voting_dict):
    """
    Input: the last name of a senator, and a dictionary mapping senator names
           to lists representing their voting records.
    Output: the last name of the senator whose political mindset is least like the input
            senator.
    Example:
        >>> vd = {'Klein': [1,1,1], 'Fox-Epstein': [1,-1,0], 'Ravella': [-1,0,0]}
        >>> least_similar('Klein', vd)
        'Ravella'
    """
    most_closely_related_record = 10000
    most_closely_related_name = ""
    for name in voting_dict:
        compare_record = get_voting_vec1(voting_dict[name])
        similarity = get_similarity(sen, name, voting_dict)
        if (similarity < most_closely_related_record) & (name!=sen):
            most_closely_related_record = similarity
            most_closely_related_name = name
    return most_closely_related_name
    
## print(least_similar("Murray", dict_voting))   

## Task 5

most_like_chafee    = most_similar("Chafee", dict_voting)
least_like_santorum = least_similar("Santorum", dict_voting)


# Task 6

def find_average_similarity(sen, sen_set, voting_dict):
    """
    Input: the name of a senator, a set of senator names, and a voting dictionary.
    Output: the average dot-product between sen and those in sen_set.
    Example:
        >>> vd = {'Klein': [1,1,1], 'Fox-Epstein': [1,-1,0], 'Ravella': [-1,0,0]}
        >>> find_average_similarity('Klein', {'Fox-Epstein','Ravella'}, vd)
        -0.5
    """
    return sum([get_similarity(sen, x, voting_dict) for x in sen_set])/len(sen_set)

##print(find_average_similarity("Murray", {"Cantwell", "Chafee", "Santorum"}, dict_voting))

###most_average_Democrat = ... # give the last name (or code that computes the last name)


# Task 7

def find_average_record(sen_set, voting_dict):
    """
    Input: a set of last names, a voting dictionary
    Output: a vector containing the average components of the voting records
            of the senators in the input set
    Example: 
        >>> voting_dict = {'Klein': [-1,0,1], 'Fox-Epstein': [-1,-1,-1], 'Ravella': [0,0,1]}
        >>> find_average_record({'Fox-Epstein','Ravella'}, voting_dict)
        [-0.5, -0.5, 0.0]
    """
    ##print(sum([get_voting_vec2(sen, voting_dict) for sen in sen_set])/len(sen_set))
    return [v for v in (sum([get_voting_vec2(sen, voting_dict) for sen in sen_set])/len(sen_set)).f.values()]

## print(find_average_record({"Murray", "Cantwell"}, dict_voting))
## print({line.split()[0] for line in voting_data if line.split()[1]=="D"})
##print(len({line.split()[0] for line in voting_data if line.split()[1]=="D"}))
average_Democrat_record = find_average_record({line.split()[0] for line in voting_data if line.split()[1]=="D"}, dict_voting)
print(type(average_Democrat_record))
print(average_Democrat_record)

# Task 8

def bitter_rivals(voting_dict):
    """
    Input: a dictionary mapping senator names to lists representing
           their voting records
    Output: a tuple containing the two senators who most strongly
            disagree with one another.
    Example: 
        >>> voting_dict = {'Klein': [-1,0,1], 'Fox-Epstein': [-1,-1,-1], 'Ravella': [0,0,1]}
        >>> bitter_rivals(voting_dict)
        ('Fox-Epstein', 'Ravella')
    """
    ##worst_similarity = 0;
    ##worst1 = ""
    ##worst2 = ""
    ##for thing1 in voting_dict:
    ##    record1=get_voting_vec2(thing1, voting_dict)
    ##    for thing2 in voting_dict:
    ##        record2=get_voting_vec2(thing2, voting_dict)
    ##        similarity = record1*record2
    ##        if (similarity < worst_similarity):
    ##            worst_similarity = similarity
    ##            worst1=thing1
    ##            worst2=thing2
    ##return (worst1, worst2)
    pass

## print(bitter_rivals(dict_voting))
