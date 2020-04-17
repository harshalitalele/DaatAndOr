import sys

path_input_corpus = sys.argv[1]
path_output_result = sys.argv[2]
path_input_queries = sys.argv[3]

outputfile = open(path_output_result, "w")

class postingsList:    
    def __init__(self):
        self.list = []
    
    def addToList(self, posting, totalWords):
        for index,obj in enumerate(self.list):
            for k in self.list[index]:
                curP = k
            if int(curP) == int(posting):
                self.list[index][curP] += 1/totalWords
                return False
            elif int(curP) > int(posting):
                self.list.insert(index, {posting: 1/totalWords})
                return True
        self.list.append({posting: 1/totalWords})
        return True
    
    def getPostingList(self):
        listStr = ''
        for p in self.list:
            for docid in p:
                listStr += docid + ' '
        return listStr

INDEXES = {}
N = 0

def indexDoc(doc, docid):
    words = doc.split(" ")
    totalWords = len(words)
    for w in words:
        w= w.strip()
        if w in INDEXES:
            isNewEntry = INDEXES[w]['list'].addToList(docid, totalWords)
            if isNewEntry:
                INDEXES[w]['df'] += 1
        else:
            newPostingList = postingsList()
            newPostingList.addToList(docid, totalWords)
            INDEXES[w] = {'df': 1, 'list': newPostingList}

def processDocument(docDetails):
    docDetails = docDetails.split('\t')
    docid = docDetails[0]
    doc = docDetails[1]
    indexDoc(doc, docid)

corpus = open(path_input_corpus, "r")
line = corpus.readline()
while line:
    processDocument(line)
    line = corpus.readline()
    N += 1
corpus.close()

def getPostingLists(qterm):
    outputfile.write('GetPostings\n')
    outputfile.write(qterm + '\n')
    outputfile.write('Postings list: ' + INDEXES[qterm]['list'].getPostingList().strip() + '\n')

def dfsort(tup):
    return tup[1]

def tfidfsort(obj):
    for docid in obj:
        return obj[docid]

def DaatAnd(qterms):
    dfindexTuple = []
    noOfTerms = len(qterms)
    
    for qt in qterms:
        dfindexTuple.append((qt, INDEXES[qt]['df']))
    dfindexTuple.sort(key=dfsort)
    
    postingPointers = [0]*noOfTerms
    docid = -1
    docScore = {}
    daatAndPostings = []
    tfidfPostings = []
    maxDocsCheck = dfindexTuple[0][1]
    fterm = dfindexTuple[0][0]
    flist = INDEXES[fterm]['list'].list
    noOfComparisons = 0
    
    for eachDocId in range(maxDocsCheck):
        docObj = flist[eachDocId]
        for k in docObj:
            fdocid = k
            docScore[fdocid] = 1
        tfidftotal = 0
        
        for i,pointer in enumerate(postingPointers):
            if i == 0:
                tfidftotal += docObj[fdocid]*(N/INDEXES[fterm]['df'])
                continue
            else:
                curTerm = dfindexTuple[i][0]
                curTermList = INDEXES[curTerm]['list'].list
                curDocIdIndex = postingPointers[i]
                curDocObj = curTermList[curDocIdIndex]
                for k in curDocObj:
                    curDocId = k
                if curDocId < fdocid:
                    noOfComparisons += 1
                    while curDocId < fdocid and curDocIdIndex < (len(curTermList)-1):
                        noOfComparisons += 1
                        postingPointers[i] += 1
                        curDocIdIndex = postingPointers[i]
                        curDocObj = curTermList[curDocIdIndex]
                        for k in curDocObj:
                            curDocId = k
                if curDocId == fdocid:
                    noOfComparisons += 1
                    docScore[curDocId] += 1
                    tfidftotal += curDocObj[curDocId]*(N/INDEXES[curTerm]['df'])
                elif curDocId > fdocid:
                    noOfComparisons += 1
                    postingPointers[0] += 1
        if docScore[fdocid] >= noOfTerms:
            daatAndPostings.append(fdocid)
            postingPointers[0] += 1
            # calculate tf idf
            tfidfPostings.append({fdocid: tfidftotal})
        tfidftotal = 0
    
    tfidfPostings.sort(key=tfidfsort, reverse=True)
    
    # Printing/Writing job
    termsStr = ''
    for term in qterms:
        termsStr += term + ' '
    daatAndStr = ''
    noOfDocs = 0
    for docid in daatAndPostings:
        daatAndStr += docid + ' '
        noOfDocs += 1
    tfidfStr = ''
    for obj in tfidfPostings:
        for docid in obj:
            tfidfStr += docid + ' '
    
    if daatAndStr == '':
        daatAndStr = 'empty'
    if tfidfStr == '':
        tfidfStr = 'empty'
    outputfile.write('DaatAnd\n')
    outputfile.write(termsStr.strip() + '\n')
    outputfile.write('Results: ' + daatAndStr.strip() + '\n')
    outputfile.write('Number of documents in results: ' + str(noOfDocs) + '\n')
    outputfile.write('Number of comparisons: ' + str(noOfComparisons) + '\n')
    outputfile.write('TF-IDF\n')
    outputfile.write('Results: ' + tfidfStr.strip() + '\n')

def DaatOR(qterms):
    dfindexTuple = []
    noOfTerms = len(qterms)
    docidTerm = {}
    daatOrDocs = []
    termsStr = ''
    noOfDocs = 0
    docTfidf = []
    
    for qt in qterms:
        termsStr += qt + ' '
        curList = INDEXES[qt]['list'].list
        for docObj in curList:
            for k in docObj:
                docid = k
                tf = docObj[k]
            if docid not in docidTerm:
                docidTerm[docid] = [{qt: tf}]
                daatOrDocs.append(docid)
                noOfDocs += 1
            else:
                docidTerm[docid].append({qt: tf})
    
    for d in docidTerm:
        curDocTerms = docidTerm[d]
        curDocTfidf = 0
        for t in curDocTerms:
            for k in t:
                term = k
                tf = t[k]
            idf = N/INDEXES[term]['df']
            curDocTfidf += tf*idf
        docTfidf.append({d: curDocTfidf})
    docTfidf.sort(key=tfidfsort, reverse=True)
    daatOrDocs.sort()
        
    #Printing job
    tfidfStr = ''
    for doc in docTfidf:
        for k in doc:
            docid = k
        tfidfStr += docid + ' '
    if tfidfStr == '':
        tfidfStr = 'empty'
    
    daatOrDocsStr = ''
    for d in daatOrDocs:
        daatOrDocsStr += d + ' '
    if daatOrDocsStr == '':
        daatOrDocsStr = 'empty'
    
    outputfile.write('DaatOr\n')
    outputfile.write(termsStr.strip() + '\n')
    outputfile.write('Results: ' + daatOrDocsStr.strip() + '\n')
    outputfile.write('Number of documents in results: ' + str(noOfDocs) + '\n')
    outputfile.write('Number of comparisons: ' + str(noOfDocs-1) + '\n')
    outputfile.write('TF-IDF\n')
    outputfile.write('Results: ' + tfidfStr.strip() + '\n')

queries = open(path_input_queries, "r")
line = queries.readline()
while line:
    qterms = line.strip().split(' ')
    for term in qterms:
        getPostingLists(term)
    DaatAnd(qterms)
    DaatOR(qterms)
    outputfile.write('\n')
    line = queries.readline()
queries.close()

outputfile.close()




