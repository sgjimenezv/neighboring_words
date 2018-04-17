from nltk.corpus import wordnet as wn
from  functools import reduce
import math


CACHE={}
def neighbors(word):
    def get_related_synsets(synset):
        return [synset]+\
            synset.hypernyms()+\
            synset.instance_hypernyms()+\
            synset.hyponyms()+\
            synset.instance_hyponyms()+\
            synset.member_holonyms()+\
            synset.substance_holonyms()+\
            synset.part_holonyms()+\
            synset.member_meronyms()+\
            synset.substance_meronyms()+\
            synset.part_meronyms()+\
            synset.attributes()+\
            synset.entailments()+\
            synset.causes()+\
            synset.also_sees()+\
            synset.verb_groups()+\
            synset.similar_tos()#+\
            #reduce(lambda x,y:x+y.hypernyms(),synset.hypernyms(),[])#+\
            #reduce(lambda x,y:x+y.hyponyms(),synset.hyponyms(),[])

    def related_lemmas(lemma):
        return lemma.topic_domains()+\
            lemma.region_domains()+\
            lemma.usage_domains()+\
            lemma.derivationally_related_forms()+\
            lemma.pertainyms()+\
            lemma.hypernyms()+\
            lemma.instance_hypernyms()+\
            lemma.hyponyms()+\
            lemma.instance_hyponyms()+\
            lemma.member_holonyms()+\
            lemma.substance_holonyms()+\
            lemma.part_holonyms()+\
            lemma.member_meronyms()+\
            lemma.substance_meronyms()+\
            lemma.part_meronyms()+\
            lemma.attributes()+\
            lemma.entailments()+\
            lemma.causes()+\
            lemma.also_sees()+\
            lemma.verb_groups()+\
            lemma.similar_tos()+\
            lemma.antonyms()#+\
            #reduce(lambda x,y:x+y.hypernyms(),lemma.hypernyms(),[])#+\
            #reduce(lambda x,y:x+y.hyponyms(),lemma.hyponyms(),[])

    def morphy(multi_word):
        morphyed_words=[]
        for word in multi_word.split("_"):
            morphyed_word=wn.morphy(word,wn.VERB)
            if morphyed_word==None:
                morphyed_word=word
                #print word,"not found in WN"
            morphyed_words.append(morphyed_word)
        r="_".join(morphyed_words)
        return r
    
    if word in CACHE:
        x=CACHE[word]
        return x
    
    # gets all related synsets to 'word' 
    related_synsets=set(reduce(lambda x,y:x+get_related_synsets(y),wn.synsets(word),[]))

    if word[-2:]=="ly":
        #print "\tADVERB:",word
        morphyed_word=morphy(word[:-2])
    else:
        morphyed_word=morphy(word)
    if word!=morphyed_word:
        #print "Adding morphyed form",word,morphyed_word
        related_synsets=related_synsets.union(set(reduce(lambda x,y:x+get_related_synsets(y),wn.synsets(morphyed_word),[])))

    stopwords=set((
        "other","others","toward","towards","me","my","myself","we","our","ours",
        "ourselves","you","your","yours","yourself","yourselves","he","him","his","himself",
        "she","her","hers","herself","it","its","itself","they","them","their","theirs",
        "themselves","what","which","who","whom","this","that","these","those","am",
        "is","are","was","were","be","been","being","have","has","had","having","do","does",
        "did","doing","a","an","the","and","but","if","or","because","as","until","while",
        "of","at","by","for","with","about","against","between","into","through","during",
        "before","after","above","below","to","from","up","down","in","out","on","off",
        "over","under","again","further","then","once","here","there","when","where",
        "why","how","all","any","both","each","few","more","most","other","some","such",
        "no","nor","not","only","own","same","so","than","too","very","s","t","can",
        "will","just","don","should","now",

        
        "one","person","used","make","act","especially","someone","cause","state","usually",
        "position","place","part","made","quality","form","body","move","people","time",
        "another","small","order","two","become","one","person","used","make","act","especially",
        "someone","cause","state","usually","position","place","part","made","quality",
        "form","body","move","people","time","another","small","order","two","become",
        "change","group","action","particular","change","group","action","particular",

        "lacking","consisting","containing","relating","property","giving","etc","capable","coming","persons","resulting","using","whose",# 1048

        "something","somebody","e","g",""))
    punctuation=(".",",",";",":","-","(",")","[","]","?","!","`","'")

    def keywords_definition(synset):
        definition=synset.definition()
        for punct_mark in punctuation:
            definition=definition.replace(punct_mark," ")
        words=definition.split()
        keywords=[]
        for word in words:
            if not word in stopwords:
                keywords.append(word)

        return set(keywords)
    
    # sets as synonyms all lemmas-names associated to related synsets
    synonyms=set(reduce(lambda x,y:x+y.lemma_names(),related_synsets,[]))
    # adds words from definitions to synonyms
    synonyms=synonyms.union(reduce(lambda x,y:x.union(keywords_definition(y)),related_synsets,set()))
    # gets all lemmas related to related synsets
    lemmas_related_synsets=set(reduce(lambda x,y:x+y.lemmas(),related_synsets,[]))
    #1 gets all lemmas related to lemmas related to related synsets
    lemmas_related_lemmas_related_synsets=set(reduce(lambda x,y:x+related_lemmas(y),lemmas_related_synsets,[]))

    #2 adds lemmas-names related to lemmas related to related synsets as synonyms
    synonyms=synonyms.union(set([x.name() for x in lemmas_related_lemmas_related_synsets]))
    #3 merges all related lemmas
   
    CACHE[word]=synonyms
    return synonyms


def COSINE(A,B):
    A=set(neighbors(A))
    B=set(neighbors(B))
    A_intersection_B=A.intersection(B)
    return len(A_intersection_B)/math.sqrt(len(A)*len(B))

