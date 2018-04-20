#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
import re

# NFAs for the different symbols
curlyNfa = re.compile("(\{(\d+(\,\d+)*)?\})")
parenNfa = re.compile("(\((\d+((\*|\+)\d+)*)\))")
multNfa = re.compile("(\d+\*\d+)")
addNfa = re.compile("(\d+\+\d+)")
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
    global isCorrect
    setArray = []
    
    def solveExp(exp):
        multFactors = multNfa.findall(exp)

        while len(multFactors) != 0:
            digits = multFactors[0].split("*")
            a = int(digits[0])
            b = int(digits[1])
            c = list(set(setArray[a]).intersection(set(setArray[b])))
            c.sort()
            try:
                index = setArray.index(c)
            except ValueError:
                setArray.append(c)
                index = len(setArray) - 1
            exp = exp.replace(multFactors[0], str(index), 1)
            multFactors = multNfa.findall(exp)
            
        addFactors = addNfa.findall(exp)
        
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
            addFactors = addNfa.findall(exp)
            
        return exp
    
    leaf = leaf.split(";")

    for eqStr in leaf:
        setArray.clear()
        listEq = curlyNfa.findall(eqStr)
        
        for indSet in listEq:
            setArray.append(indSet[1].split(","))
            eqStr = eqStr.replace(indSet[0], str(len(setArray) - 1), 1)

        innerExps = parenNfa.findall(eqStr)
            
        while len(innerExps) != 0:
            for exp in innerExps:
                answer = solveExp(exp[1])
                eqStr = eqStr.replace(exp[0], answer, 1)
                
            innerExps = parenNfa.findall(eqStr)

        answer = solveExp(eqStr)
        answerList = answer.split("=")
        isEqual = True

        for i in range(1, len(answerList)):
            if answerList[0] != answerList[i]:
                isEqual = False

        if isEqual:
            print("Set expression verified: SUCCESS!")
        else:
            print("Set expression verified: FAILURE!!!")
            isCorrect = False

# UNDER CONSTRUCTION
def solveStrEqs(branch):
    #print("Solving string equation...")
    pass

# UNDER CONSTRUCTION
def solveAlgEqs(branch):
    #print("Solving algebra equation...")
    pass

# UNDER CONSTRUCTION
def solveBoolEqs(branch):
    #print("Solving boolean equation...")
    pass

main()
