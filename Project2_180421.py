#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import re
import time

# NFAs for the different symbols
curlyNfa = re.compile("(\{(\d+(\,\d+)*)?\})")
parenNfa = re.compile("(\((\d+((\*|\+)\d+)*)\))")
starNfa = re.compile("(\d+\*\d+)")
plusNfa = re.compile("(\d+\+\d+)")
equalsNfa = re.compile("(\d+\=\d+)")

isCorrect = True


def main():
    os.system('clear')
    filename = filedialog.askopenfilename()
    root = ET.parse(filename).getroot()
    tree = parseMarkup(root)
    parseElement(tree)

    root = tk.Tk()
    root.withdraw()

    if isCorrect:
        messagebox.showinfo('Check Completed', 'File has correct expressions')
    else:
        messagebox.showwarning('Check Completed', 'File has incorrect expressions')


# Reads in XML data and converts to "tree" list
def parseMarkup(root):
    def consolidate(str):
        return "".join(str.split())

    def parseXML(root):
        tree = [root.tag, consolidate(root.text)]
        if len(root) > 0:
            for i in range(0, len(root)):
                tree.append(parseXML(root[i]))
                if consolidate(root[i].tail) != "":
                    tree.append(consolidate(root[i].tail))
        return tree
    
    return parseXML(root)


# Loops through each element in the tree
def parseElement(branch):
    for i in range(0, len(branch)):
        if i == 0:
            branchTag = branch[0]
        else:
            if isinstance(branch[i], str):
                if branchTag == "sets":
                    solveSetEqs(branch[i])
                elif branchTag == "algebra":
                    solveAlgEqs(branch[i])
                elif branchTag == "boolean":
                    solveBoolEqs(branch[i])
                elif branchTag == "strings":
                    solveStrEqs(branch[i])
                else:
                    print("Invalid tag.")
            else:
                parseElement(branch[i])


def solveSetEqs(leaf):
    
    def solveExp(exp):
        multFactors = starNfa.findall(exp)

        while len(multFactors) != 0:
            digits = multFactors[0].split("*")
            a = int(digits[0])
            b = int(digits[1])
            c = list(set(setArray[a]).intersection(set(setArray[b])))
            c.sort()

            try:
                index = setArray.index(c)
            except ValueError:
                print("Adding table entry for: " + str(c))
                setArray.append(c)
                index = len(setArray) - 1

            exp = exp.replace(multFactors[0], str(index), 1)
            multFactors = starNfa.findall(exp)
            
        addFactors = plusNfa.findall(exp)
        
        while len(addFactors) != 0:
            digits = addFactors[0].split("+")
            a = int(digits[0])
            b = int(digits[1])
            c = list(set(setArray[a]).union(set(setArray[b])))
            c.sort()
            
            try:
                index = setArray.index(c)
            except ValueError:
                setArray.append(c)
                index = len(setArray) - 1
                
            exp = exp.replace(addFactors[0], str(index), 1)
            addFactors = plusNfa.findall(exp)
            
        return exp
    
    # Start of function
    global isCorrect
    setArray = []
    leaf = leaf.split(";")

    for eqStr in leaf:
        setArray.clear()
        listEq = curlyNfa.findall(eqStr)
        
        for indSet in listEq:
            try:
                index = setArray.index(indSet[1])
                print("indSet[1]")
                print(index)
            except ValueError:
                setArray.append(indSet[1])
                index = len(setArray) - 1
                print("Set Array at index " + str(index) + ": ")
                print(setArray[index])
            
            eqStr = eqStr.replace(indSet[0], str(len(setArray) - 1), 1)

        isDone = False
        tests = [eqStr.find("*") == -1, eqStr.find("+") == -1]
            
        if all(tests):
            isDone = True

        while isDone == False:
            innerExps = parenNfa.findall(eqStr)
                
            while len(innerExps) != 0:
                for exp in innerExps:
                    answer = solveExp(exp[1])
                    eqStr = eqStr.replace(exp[0], answer, 1)
                    
                innerExps = parenNfa.findall(eqStr)

            for exp in eqStr.split("="):
                print("spit eq: " + exp)
                answer = solveExp(exp)
                eqStr = eqStr.replace(exp, answer, 1)
                print("answer: " + answer)
                print("eqStr: " + eqStr)
                
            tests = [eqStr.find("*") == -1, eqStr.find("+") == -1]
            
            if all(tests):
                isDone = True

        answerList = eqStr.split("=")
        isEqual = True
        print("eqStr: " + eqStr)
        
        for i in range(1, len(answerList)):
            if answerList[0] != answerList[i]:
                isEqual = False

        if isEqual:
            print("Set expression verified: SUCCESS!")
        else:
            print("Set expression verified: FAILURE!!!")
            isCorrect = False


def solveStrEqs(leaf):
    
    def solveExp(innerParen):
        starFactors = starNfa.findall(innerParen)

        while len(starFactors) != 0:
            digits = starFactors[0].split("*")
            base = str(digits[0])
            power = int(digits[1])
            result = ""
            
            for i in range(0, power):
                result += base

            innerParen = innerParen.replace(starFactors[0], result, 1)
            starFactors = starNfa.findall(innerParen)
            
        plusFactors = plusNfa.findall(innerParen)
        
        while len(plusFactors) != 0:
            digits = plusFactors[0].split("+")
            a = str(digits[0])
            b = str(digits[1])
            c = a + b
            innerParen = innerParen.replace(plusFactors[0], c, 1)
            plusFactors = plusNfa.findall(innerParen)

        return innerParen

    # Start of function
    global isCorrect
    leaf = leaf.split(";")

    for statement in leaf:
        isDone = False
        tests = [statement.find("*") == -1, statement.find("+") == -1]
            
        if all(tests):
            isDone = True
        
        while isDone == False:
            parenEqs = parenNfa.findall(statement)
            
            while len(parenEqs) != 0:
                for innerParen in parenEqs:
                    answer = solveExp(innerParen[1])
                    statement = statement.replace(innerParen[0], answer, 1)
                
                parenEqs = parenNfa.findall(statement)

            statement = solveExp(statement)
            tests = [statement.find("*") == -1, statement.find("+") == -1]
            
            if all(tests):
                isDone = True

        answerList = statement.split("=")
        isEqual = True

        for i in range(1, len(answerList)):
            if answerList[0] != answerList[i]:
                isEqual = False

        if isEqual:
            print("String expression verified: SUCCESS!")
        else:
            print("String expression verified: FAILURE!!!")
            isCorrect = False


def solveAlgEqs(branch):
    pass


def solveBoolEqs(branch):
    pass


main()
