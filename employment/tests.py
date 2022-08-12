from django.test import TestCase

# Create your tests here.
from django.utils.datastructures import MultiValueDictKeyError
from employment.models import *
from django.core.exceptions import ObjectDoesNotExist
from collections import Counter

##
## test for any new_value which is the same as value (to avoid circular references)
##
def value_change():
    print('Test for circular references between value and new_value (Enter to test)\n')
    input()
    for model in Choice, Dependency, Comment:
        ids=model.objects.all()
        for pkey in ids:
            record=model.objects.get(id=int(str(pkey)))
            if record.value == record.new_value:
                print('new_value is not new in '+str(model) + ': ' + str(record.key)+'-'+
                    str(record.value))

##
## test Dependency for key = ref_key (circular reference)
##
def dependency_circular_reference():
    print('\nTest for circular references between key and ref_key in Dependency (Enter to test)\n')
    input()
## all unique keys
    keys=[]

    ids=Dependency.objects.all()
    for d in ids:
        record=Dependency.objects.get(id=str(d))
## a particular key cannot be dependent on itself, i.e. cannot be the same as its ref_key
        if record.key == record.ref_key:
            print('Self reference in Dependency at key: ' +str(record.key)+' '+
                str(record.value))
## create a stack of all unique keys
        if record.key not in keys:
            keys.append(str(record.key))

    for k in keys:
## for each key, start following up its dependencies, and follow them up to find
## reference back to key
        # print('Evaluation of next key - ' + str(k))
## list of all unique reference keys (dependencies immediate or further on the line) 
## which have to be checked / evaluated for a particular key
        ref_keys=[]

## list of immediate reference keys of a particular key
        ref_list=[]

## a stack of reference keys of a key to work from, i.e. to follow up / check (until it is empty)
        check_stack=[]

        ids=Dependency.objects.filter(key=k)
## create the initial lists for this key
        for d in ids:
            record=Dependency.objects.get(id=str(d))
            rk= str(record.ref_key)
            if rk != "":
                if rk == k:
                    print(str(k) + ' has a circular reference at record ' + str(record) )
                    input()
                if rk not in ref_list:
                    ref_list.append(rk)
                    # print(rk + ' appended to ref_list for ' + str(k))
                if rk not in ref_keys:
                    ref_keys.append(rk)
                    # print(rk + ' appended to ref_keys')
                if rk not in check_stack:
                    check_stack.append(rk)
        #             print(rk + ' appended to check_stack')
        # print('\nImmediate reference keys for the key - ' + str(k) + ' - are ' + 
        #     str(ref_list) + '\n')
        while len(check_stack) > 0:
            check=check_stack.pop()
            # print('\n' + str(check) + ' - popped from check_stack. This is a new key to check.\n')
            ids=Dependency.objects.filter(key=check)
            # print(ids)
            ref_list=[]
            if len(ids) > 0:
                for d in ids:
                    record=Dependency.objects.get(id=str(d))
                    rk= str(record.ref_key)
                    if rk != "":
                        if rk == k:
                            print(str(k) + ' has a circular reference at record ' + str(record) )
                            input()
                        if rk not in ref_list:
                            ref_list.append(rk)
                            # print(rk + ' appended to ref_list for ' + str(check))
                        if rk not in ref_keys:
                            ref_keys.append(rk)
                            # print(rk + ' appended to ref_keys')
                        if rk not in check_stack:
                            check_stack.append(rk)
                #             print(rk + ' appended to check_stack')
                # print('Immediate reference keys for ref_key - ' + str(check) + ' - are - ' + 
                #     str(ref_list))

##
## Each new_key has to be an attribute 
##
## Tests whether each new_key assigned in Direction is in the list of attributes,
## i.e. it is properly evaluated somewhere
##
def new_key_evaluation():
    new_value_classes=[Choice, Comment, Dependency]
    final_value_classes=[Reference, Direction]
    exit_classes=[Abort, Exit, Other]
    classes=new_value_classes+final_value_classes+exit_classes
    keys_extract=[]
    pairs=[]
    print('Each new_key must be also an attribute (Enter to test)\n')
    input()
## (1) Extract all keys (attribute names) from the classes into a list of unique "attributes"
## (2) extract all key/value pairs into the list "pairs" with not 
##   necessarily unique elements 
    for c in classes:
        a=c.objects.all()
        for i in a:
            record=c.objects.get(id=int(str(i)))
            p=(str(record.key)+'-'+str(record.value))
            pairs.append(p)
            keys_extract.append(str(record.key))
    unique_set=set(keys_extract)
    attributes=list(unique_set)
    d=Direction.objects.all()
    for i in d:
        record=Direction.objects.get(id=int(str(i)))
        if str(record.key) == "" \
            or str(record.value)=="" \
            or str(record.final_value)=="" \
            or str(record.new_key)=="":
            print('Direction at Id '+str(i)+' has empty value.')
        p=str(record.new_key)
        if p not in attributes:
            print('ID ' + str(i))
            print('New key '+ p +' is not evaluated.')
## key / new_value evaluation 
## Take key / new_value pairs from classes with new_value field and test whether they
## all are evaluated somewhere, i.e. they appear in the list of key/value pairs

    new_value_classes=[Choice, Comment, Dependency]
    print('Test for evaluation of all key new_value pairs. (Enter to test)\n')
    input()
    for c in new_value_classes:
        a=c.objects.all()
        for i in a:
            record=c.objects.get(id=int(str(i)))
            p=(str(record.key)+'-'+str(record.new_value))
            if p not in pairs:
                print('New pair '+str(p)+' is not evaluated at value '+str(record.value)+
                    ' in '+str(c))

##
## Dependency - Reference - Direction ####################
##
## (1) each reference pair in Dependency  
## should be in Reference as value/final_value pair, with only a few exceptions when 
## the reference was made to a key/final_value pair in Direction.
## Otherwise the dependency (or reference) in Dependency can never be satisfied and 
## the new_value can never be assigned to the corresponding key, i.e. the record would 
## be obsolate.
##
def dependency_reference():
## Creating / preparing lists to work from
    d=Dependency.objects.all()
    dependency_reference_pairs=[]
    dependency_ref_keys=[]
    print('Test consistency within Dependency, and in Reference (Enter to test)\n')
    input()
## from Dependancy extract all ref_key / ref_value Pairs into a list of unique
## 'key-value' elements, and check for inconsistencies on the way.
    for i in d:
        record=Dependency.objects.get(id=int(str(i)))
        if str(record.key) == "":
            print('Dependency at Id '+str(i)+' empty key.')
        if str(record.value)=="":
            print('Dependency at Id '+str(i)+' empty value.')
        if str(record.new_value)=="":
            print('Dependency at Id '+str(i)+' empty new_value.')
        if str(record.ref_key) != "":
            dependency_ref_keys.append(str(record.ref_key))
            dependency_reference_pairs.append(str(record.ref_key)+'-'+str(record.ref_value))

## create lists of unique values
    dependency_ref_keys=list(set(dependency_ref_keys))
    dependency_reference_pairs=list(set(dependency_reference_pairs))
    
## from Reference extract 
## (1) all key / final_value Pairs into a list of 'key-final_value'
## elements and check for inconsistencies on the way. (the elements must be unique)
## (2) the unique list of keys.

    ref=Reference.objects.all()

## Reference key-final_value pairs
    reference_pair=[]

## all keys in Reference
    ref_key=[]

    for i in ref:
        record=Reference.objects.get(id=int(str(i)))
        if str(record.key) == "":
            print('Reference at Id '+str(i)+' empty key.')
        if str(record.value)=="":
            print('Reference at Id '+str(i)+' empty value.')
        if str(record.final_value)=="":
            print('Reference at Id '+str(i)+' empty final_value.')
        reference_pair.append(str(record.key)+'-'+str(record.final_value))
        ref_key.append(str(record.key))
    duplicates=[key for key in Counter(reference_pair).keys() if Counter(reference_pair)[key]>1]
    if len(duplicates) > 0:
        print('Duplicate keys in Reference: '+str(duplicates))

## from Direction extract 
## (1) all key / final_value Pairs into a list of 'key-final_value'
## elements and check for inconsistencies on the way. (the elements must be unique)
## (2) the unique list of keys.

    dir=Direction.objects.all()
    dir_pair=[]
    dir_key=[]
    for i in dir:
        record=Direction.objects.get(id=int(str(i)))
        if str(record.key) == "":
            print('Direction at Id '+str(i)+' empty key.')
        if str(record.value)=="":
            print('Direction at Id '+str(i)+' empty value.')
        if str(record.final_value)=="":
            print('Direction at Id '+str(i)+' empty final_value.')
        dir_pair.append(str(record.key)+'-'+str(record.final_value))
        dir_key.append(str(record.key))
    duplicates=[key for key in Counter(dir_pair).keys() if Counter(dir_pair)[key]>1]
    if len(duplicates) > 0:
        print('Duplicate keys in Direction: '+str(duplicates))

## In Dependency, each reference_pair has to be a Key-Final_value in Reference 
## with only a few exception when the reference pair is in Direction
    for x in dependency_ref_keys:
        if x in ref_key:
            pass
        elif x in dir_key:
            pass
        else:
            print('Dependency reference key '+str(x)+' is not evaluated')
    for y in dependency_reference_pairs:
        if y in reference_pair:
            pass
        elif y in dir_pair:
            pass
        else:
            print('Dependency reference pair '+str(y)+' is not found')
##
## Test for consistency between the output files and records of class Law
##    
def test_law():
    BASE_DIR = 'C:\\Users\\Andrash\\Google Drive\\AI research\\LawRobot\\Programming\\LawRoby'
    RELEVANT_LAW = BASE_DIR + '\\employment\\legislation\\relevant_law\\'
    FULL_SECTIONS = BASE_DIR + '\\employment\\legislation\\full_sections\\'
    print(RELEVANT_LAW)
    print(FULL_SECTIONS)
    print(' Test for consistency between output files and class Law (Enter to test)\n')
    input()        
    l = Law.objects.all()
    for i in l:
        record = Law.objects.get(id = int(str(i)))
        fname = str(record.relevant_law)
        if fname == '':
            pass
        else:
            try:
                r = open( RELEVANT_LAW + fname + ".pdf", "rb" )
            except:
                print('Relevant Law ' + fname + ' is missing')
            else:
                r.close()

    for i in l:
        record = Law.objects.get(id = int(str(i)))
        fname = str(record.full_section)
        if fname == '':
            pass
        else:
            try:
                r = open( FULL_SECTIONS + fname + ".pdf", "rb" )
            except:
                print('Full Section ' + fname + ' is missing')
            else:
                r.close()
           
##  
## Check unique Pairs
##
## Arrange all Pairs from those classes that must not have duplication of Pairs, and
## put them into a list of Pairs with dash connection then check for uniqueness;
## ( each Pair in Question must also appear in Choice in multiple times, so Choice 
## cannot be tested here; Pairs are not unique in Dependency either.)
## 
def pair_uniqueness():
    pairs=[]
    unique_model = [Question, Abort, Exit, Other, Reference, Direction, Comment]
    print( 'Check for duplication for Pairs in Classes where Pair should be unique (Enter to test)\n')
    input()
# append the list of pairs of each model into the list pairs
    for m in unique_model:
        pair_list=pairs_in_model(m)
        for p in pair_list:
            pairs.append(p)
## the following inclusion of Dependency refers to a case when each Pair in Dependency
## is assigned a new value either by a satisfied reference, or by an unconditional new value
## assignment in case of no reference satisfied.
    # dep=pairs_in_model(Dependency)
    # unique_pairs=set(dep)
    # dep_pairs=list(unique_pairs)
    # pairs=pairs + dep_pairs

# Check whether the pairs in the list pairs are unique
    num_duplicate=len(pairs) - len(set(pairs))
    if num_duplicate > 0:
        print(num_duplicate, ' duplicate found')
        dups=set([x for x in pairs if pairs.count(x) > 1])
        unique_model.append(Dependency)
        for d in dups:
            for m in unique_model:
                pair_list=pairs_in_model(m)
                if d in pair_list:
                    print(d, ' is in ', m)

##
## test consistency between questions and choices (answers)
##
def question_choices():
    print('Each Pair in class Question must appear more than once in Choice (Enter to test)')
    input()
    quest=pairs_in_model(Question)
    ch=pairs_in_model(Choice)
    for q in quest:
        appear=0
        for c in ch:
            if q == c:
                appear=appear + 1
        if appear == 1:
            print(q, ' appears only once in Choice')
        if appear == 0:
            print(q, ' is not in Choice')

##
## Each Pair in Dependency either (1) takes a new value when a reference is satisfied,
## or (2) takes a new value when no reference has been satisfied (if there is a new value
## assignment without condition at the end), or (3) it will be found in
## other tables (e.g. Question, Direction...etc)
##
def dependency_assignments():
    print('Testing the evaluation / assignment of pairs in Dependency')
    ids = Dependency.objects.all()
    unique_pairs = []
## get all ids in Dependency, and create a list of unique key / value pairs
    for i in ids:
        record = Dependency.objects.get(id=int(str(i)))
        pair = [str(record.key), str(record.value)]
        if pair not in unique_pairs:
            unique_pairs.append(pair)
## get the ids of all Dependency records with the same key / value pair
    for pair in unique_pairs:
        same_pair_ids = Dependency.objects.filter(key=pair[0], value=pair[1])
        for id in same_pair_ids:
            record = Dependency.objects.get(id=int(str(id)))
## if one of the records has an empty ref_key (i.e. there is no condition for
## taking a new value), go to the next unique pair
            if str(record.ref_key) == "":
                break
## otherwise (i.e. there is no new value if no reference is satisfied)
## try the pair in the other classes (it must be in one of them)
        else:
            classes = [Abort, Exit, Comment, Direction, Other, Question, Reference]
            found = try_in(pair[0], pair[1], classes)
            if found == 0:
                print( 'ERROR!! the pair '+ str(pair)+ ' is not evaluated')
            elif found > 1:
                print( 'ERROR!! the pair '+ str(pair)+ ' is evaluated more than once')
            


#####################################################
## Definition of functions called from test functions
#####################################################

## (1) Extract all keys (attribute names) from the classes into a list of unique "attributes"
def all_keys():
    new_value_classes=[Choice, Comment, Dependency]
    final_value_classes=[Reference, Direction]
    exit_classes=[Abort, Exit, Other]
    classes=new_value_classes+final_value_classes+exit_classes
    keys_extract=[]
    for c in classes:
        a=c.objects.all()
        for i in a:
            record=c.objects.get(id=int(str(i)))
            keys_extract.append(str(record.key))
    unique_set=set(keys_extract)
    keys=list(unique_set)
    return keys

## extract all key/value pairs into a list of unique Pairs 
def all_pairs():
    new_value_classes=[Choice, Comment, Dependency]
    final_value_classes=[Reference, Direction]
    exit_classes=[Abort, Exit, Other]
    classes=new_value_classes+final_value_classes+exit_classes
    pairs_extract=[]
    for c in classes:
        a=c.objects.all()
        for i in a:
            record=c.objects.get(id=int(str(i)))
            p=(str(record.key)+'-'+str(record.value))
            pairs_extract.append(p)
    unique_pairs=set(pairs_extract)
    pairs=list(unique_pairs)
    return pairs

## returns a list of all key-value pairs for the class
def pairs_in_model(class_name):
    ids = class_name.objects.all()
    pairs=[]
## append each pair into the list pairs
    for i in ids:
        record=class_name.objects.get(id=int(str(i)))
        pairs.append(str(record.key)+'-'+str(record.value))
    if len(ids) != len(pairs):
        print('mismach of ids and pairs in model ', class_name)
    # if len(ids) > len(set(pairs)):
    #     print('duplicate pair in model ', class_name)
    return pairs

## returns the list of new_value for the Pair in class class_name     
def new_values(class_name, key, value):
    ids = class_name.objects.filter( key=key, value=value )
    print('Id list for '+str(key)+'-'+str(value)+' in '+str(class_name)
          +' is ' +str(ids))
    nv=[]
    if len(ids) > 0:
        for x in ids:
            record = class_name.objects.get( id=int(str(x)) )
            nv.append(str(record.new_value))
            print(nv + ' from ' + str(class_name) + 
                ' appended to newvalues for '+value)
    return nv
  

def try_in(key, value, classes):
    final = 0
    for cl in classes:
        try:
            a = cl.objects.get( key=key, value=value )
            final += 1
            # print(value + ' is in ' + str(cl))
        except:
            pass
    return final  


## returns a list of all key-new_value pairs
def new_pairs_in_model(class_name):
    ids = class_name.objects.all()
    pairs=[]
# append each pair into the list pairs
    for i in ids:
        record=class_name.objects.get(id=int(str(i)))
        pairs.append(str(record.key)+'-'+str(record.new_value))
    if len(ids) != len(pairs):
        print('mismach of ids and new pairs in model ', class_name)
    if len(ids) > len(set(pairs)):
        print('duplicate new pair in model ', class_name)
 
#################
## Testing
#################

# pair_uniqueness()
# question_choices()
test_law()
# new_key_evaluation()
# value_change()
# dependency_circular_reference()
# dependency_reference()
# dependency_assignments()