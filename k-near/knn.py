from numpy import *
import operator

def createDataSet():
    group = array([[1.0,1.1],[1.0,1.0],[0,0],[0,0.1]])
    labels = ['A','A','B','B']
    return group,labels

def classify0(inX,dataSet,labels,k):
    dataSetSize = dataSet.shape[0]
    #距离计算
    diffMat = tile(inX,(dataSetSize,1)) - dataSet
    sqDiffMat = diffMat ** 2
    sqDistaces = sqDiffMat.sum(axis = 1)
    distances = sqDistaces ** 0.5
    sortedDisIndicies = distances.argsort()
    
    classCount={}
    
    #选择距离最小的点
    for i in range(k):
        voteIlabel = labels[sortedDisIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1


    #排序
    sortedClassCount = sorted(classCount.items(),key=operator.itemgetter(1),reverse = True)
    return sortedClassCount[0][0]    

def file2matrix(filename):
    fr = open(filename)
    arrayOnLines = fr.readlines()
    numberOfLines = len(arrayOnLines)
    #创建以0填充的二维数组
    returnMat = zeros((numberOfLines,3))
    classLabelVector = []
    index = 0
    for line in arrayOnLines:
        line = line.strip()#去掉最后的\n
        listFromLine = line.split('\t')#按照'\t'分割字符串为数组
        returnMat[index,:] = listFromLine[0:3]
        classLabelVector.append(int(listFromLine[-1]))
        index = index + 1
    fr.close()
    return returnMat,classLabelVector

def autoNorm(dataSet):
    minVal = dataSet.min(0)
    maxVal = dataSet.max(0)
    ranges = maxVal - minVal
    normDataSet = zeros(shape(dataSet))
    m = dataSet.shape[0]
    normDataSet = dataSet - tile(minVal,(m,1))
    normDataSet = normDataSet/tile(ranges,(m,1))
    return normDataSet,ranges,minVal


def datingClassTest():
    hoRatio = 0.07
    datingDataMat,datingLabels = file2matrix('datingTestSet2.txt')
    normMat,ranges,minVals = autoNorm(datingDataMat)
    m = normMat.shape[0]
    numTestVecs = int(m*hoRatio)
    errorCount = 0.0
    for i in range(numTestVecs):
        classifyResult = classify0(normMat[i,:],normMat[numTestVecs:m,:],\
                                   datingLabels[numTestVecs:m],3)
        print("the classfiyier came back with: %d,the real answer is: %d" %(\
            classifyResult,datingLabels[i]))
        if(classifyResult != datingLabels[i]):errorCount += 1.0
        
    print("the total error rate is: %f " %(errorCount/float(numTestVecs)))

def classifyPerson():
    resultList = ['not at all','in small doses','in large doses']
    percentTats = float(input("平均每周在视频游戏上花费的时间比?"))
    flyMailes = float(input("每年飞行距离?"))
    iceCream = float(input("每年消耗的冰激凌公升数?"))
    datingDataMat,datingLabels = file2matrix('datingTestSet2.txt')
    normMat,ranges,minVals = autoNorm(datingDataMat)
    inArr = array([flyMailes,percentTats,iceCream])
    classifyResult = classify0((inArr-minVals)/ranges,normMat,datingLabels,3)
    print("you will probably like this person:",resultList[classifyResult-1])
        
    
