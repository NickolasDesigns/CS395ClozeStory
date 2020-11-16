import chains
from pprint import pprint


def parse_test_instance(story):
    """Returns TWO ParsedStory instances representing option 1 and 2"""
    # this is very compressed
    id = story.InputStoryid
    story = list(story)
    sentences = [chains.nlp(sentence) for sentence in story[2:6]]
    alternatives = [story[6], story[7]]
    return [chains.ParsedStory(id, id, chains.nlp(" ".join(story[2:6]+[a])), *(sentences+[chains.nlp(a)])) for a in alternatives]

def story_answer(story):
    """Tells you the correct answer. Return (storyid, index). 1 for the first ending, 2 for the second ending"""
    #obviously you can't use this information until you've chosen your answer!
    return story.InputStoryid, story.AnswerRightEnding

# Load training data
data, table = chains.process_corpus("train.csv", 1000) # train words on train.csv and build table to use in determining answer. 
#print(table.pmi("move", "nsubj", "move", "nsubj"))

# load testing data
test = chains.load_data("val.csv")
n = 0 #values for testing performance. n is num right, tn is total count
tn = 0
for t in test:
    one, two = parse_test_instance(t)
    one_deps = chains.extract_dependency_pairs(one)
    two_deps = chains.extract_dependency_pairs(two)
    #pprint(one_deps)
    #pprint(one[2:])
    #pprint(two_deps)
    #pprint(two[2:])
    #Look at dependecy list and find out which sentence offers more verbs to the main entity (protagonist). More relevence means more coherent answer. 
    #0 is first entity, 1 is second entity, etc. 
    if (len(one_deps[0])>len(two_deps[0])):
        print("my answer: 1")
        if(t.AnswerRightEnding == 1): #check if the answer is correct
            n+=1
        print("right so far :"+str(n))
    elif (len(one_deps[0])==len(two_deps[0])):  #if dependency lists are the same size for the main entity, look at the occurances of the words from the test data and choose one that occurs most 
        total = 0
        for (w1,w2) in zip(one_deps[1][0],two_deps[1][0]):  #iterate through first entities 
            word1 = w1[0]
            verb1 = w1[1]
            word2 = w2[0]
            verb2 = w2[1]
            total += table.pmi(word1, verb1,word2, verb2)  #return the most occuring instances of the two versions of verb dependencies.
        if(total <= 0):
            total = 1
        else: #if total is 0 then the words are the same.
            total = 2
        if(t.AnswerRightEnding == total):
            n+=1
        print("right so far :"+str(n))
    else:
        print("my answer: 2") #if the second dependency list is larger than it contains an extra centence that fits in the story, thus the 5th sentence is correct. 
        if(t.AnswerRightEnding == 2):
            n+=1
        print("right so far :"+str(n))
    # logic to choose between one and two
    tn+=1 #increment after each round to keep track of total stories tested. 
    print("total"+str(tn))
    pprint("answer:"+ str(story_answer(t)))

print(str((n/tn)*100) + "%") #percentage of correct decisions. For testing purposes