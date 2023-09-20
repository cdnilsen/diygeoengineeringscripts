from bs4 import BeautifulSoup as bsoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from time import sleep

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)



searchURL = "https://brokercheck.finra.org"


def getBrokerInfo(listOfBrokers, idnumList, nameList, addressList, zipList):
    for broker in listOfBrokers:
        brokerName = broker.find_element(By.XPATH, ".//span[@class='sm:text-sm font-semibold text-base']").text
        brokerCRD = broker.find_element(By.XPATH, ".//div[@class='text-gray-85 text-left font-semibold mt-1 text-xs ng-star-inserted']").get_attribute('innerHTML')
        brokerCRD = brokerCRD.split('<span _ngcontent-')[2]
        brokerCRD = (brokerCRD.split('>'))[1]
        brokerCRD = (brokerCRD.split('<'))[0]
        idnumList.append(brokerCRD)
        nameList.append(brokerName)
        try:
            brokerAddress = broker.find_element(By.XPATH, ".//investor-tools-address").get_attribute('innerHTML')
            brokerAddress = brokerAddress.split('<')[0]
        except:
            brokerAddress = "NULL_ADDR"
        addressList.append(brokerAddress.strip())
        if len(brokerAddress) > 0:
            addressArray = brokerAddress.split("<")
            brokerAddress = addressArray[0].strip()
            brokerZip = (brokerAddress.split())[-1]
        else:
            addressArray = [""]
            brokerZip = "NULL_ZIP"
        zipList.append(brokerZip)



def processPageOfBrokers(tupleList, wantedZip, driver):
    brokerCRDList = []
    brokerNameList = []
    brokerAddressList = []
    brokerZipList = []

    listOfBrokersOnThisPage = driver.find_elements(By.XPATH, "//bc-individual-search-result-card")

    getBrokerInfo(listOfBrokersOnThisPage, brokerCRDList, brokerNameList, brokerAddressList, brokerZipList)

    for i in range(len(brokerCRDList)):
        if brokerZipList[i][0:2] == wantedZip[0:2]:
            tupleList.append((brokerCRDList[i], brokerNameList[i], brokerAddressList[i], brokerZipList[i]))

    return tupleList

def doASearch(driverName, urlPath, lastName, zipCode):
    driverName.get(urlPath)
    nameID = driverName.find_element(By.XPATH, "//input[@aria-label='individual-name']")
    zipID = driverName.find_element(By.XPATH, "//input[@aria-label='zip']")
    sendSearch = driverName.find_element(By.XPATH, "//button[@aria-label='IndividualSearch']")

    nameID.clear()
    zipID.clear()
    nameID.send_keys(lastName)
    zipID.send_keys(zipCode)

    sendSearch.click()
    driverName.refresh()
    finalTupleList = []
    canContinue = True
    while canContinue == True:
        sleep(0.5)
        try:
            buttonRibbon = driverName.find_element(By.XPATH, "//div[@class='grid grid-cols-1 gap-3 py-5 m-auto w-10/12']")
            buttonList = buttonRibbon.find_elements(By.XPATH, ".//button")
            ribbonText = buttonRibbon.find_element(By.XPATH, ".//div[@class='px-5']")
            ribbonTextSpan = ribbonText.find_element(By.XPATH, ".//span").text

            ribbonTextList = ribbonTextSpan.split()
            print(ribbonTextList)
            processPageOfBrokers(finalTupleList, zipCode, driverName)
            continueAfterwards = True
            
            buttonToClick = []
            for button in buttonList:
                canGoForward = ('svg-inline--fa fa-chevron-right fa-w-10 fa-fw fa-lg' in button.get_attribute('innerHTML'))
                if canGoForward == True:
                    buttonToClick.append(button)
                    buttonToClick[0].click()

            if(ribbonTextList[0] == ribbonTextList[2]):
                canContinue = False
        except:
            break
    return finalTupleList

def writeInfoToFile(driver, targeturl, targetZip, nameZipTupleList, outputFile):
    for tuple in nameZipTupleList:
        newFile = open(outputFile, "a")
        tempTupleList = doASearch(driver, targeturl, tuple[0], tuple[1])
        for entry in tempTupleList:
            lineToWrite = ""
            for subentry in entry:
                lineToWrite += (subentry + ", ")
            newFile.writelines(lineToWrite[0:-2] + "\n")
        driver.refresh()
    newFile.close()

def nameGluer(nameList, zipList):
    outputList = []
    for i in range(len(nameList)):
        outputNameTuple = (nameList[i], zipList[i])
        outputList.append(outputNameTuple)
    return outputList

def dictionaryZipper(nameZipTupleList, outputDict):
    for tuple in nameZipTupleList:
        if tuple[1] not in outputDict:
            outputDict[tuple[3]] = [(tuple[0], tuple[1])]
        else:
            outputDict[tuple[3]].append((tuple[0], tuple[1]))
    
    return(outputDict)

def main(inputFilePath, outputFilePath):
    urlPath = "https://brokercheck.finra.org/"
    myDriver = webdriver.Chrome(options=chrome_options)
    inputFile = open(inputFilePath, 'r')
    Lines = inputFile.readlines()
    finalDictionary = {}
    outputFile = open(outputFilePath, "a")
    for line in Lines:
        lineList = line.split(",")
        try:
            searchTuples = doASearch(myDriver, urlPath, lineList[1], lineList[0])
            dictionaryZipper(searchTuples, finalDictionary)
        except:
            continue
    zipList = list(finalDictionary.keys())
    zipList.sort()


    allLinesList = []
    for line in Lines:
        lineList = line.split(",")
        if lineList[0] in zipList:
            for broker in finalDictionary[lineList[0]]:
                allLinesList.append(lineList[0] + "#" + broker[0] + "#" + broker[1] + "\n")
    for nextLine in allLinesList:
        outputFile.writelines(nextLine)
    outputFile.close()
    


    




        



main("testInput.txt", "testOutput.txt")

'''
testDriver = webdriver.Chrome(options= chrome_options)
testTuples = doASearch(testDriver, "https://brokercheck.finra.org/", "Bonomi", "01089")

print(testTuples)
'''


#main("testinput.txt", "testouput.txt")




#Figure out why it's trying to run a search on 'FeigelmanBonomi'


'''


    buttonRibbon = driver.find_element(By.XPATH, "//div[@class='grid grid-cols-1 gap-3 py-5 m-auto w-10/12']")
    buttonList = buttonRibbon.find_elements(By.XPATH, ".//button")
    for button in buttonList:
        try:
            gofurtherButton = buttonList.find_element(By.XPATH, ".//svg[@class='svg-inline--fa fa-chevron-right fa-w-10 fa-fw fa-lg']")
            button.click()
        except:
            continue
    
        
        
        

    for i in range(len(brokerCRDList)):
        print(brokerCRDList[i] + "口" + brokerNameList[i] + "口" + brokerAddressList[i] + "口" + brokerZipList[i])
        #for component in addressArray:

        #brokerAddressList.append(brokerAddress)

        #print(brokerName.prettify())

        #print("Address of " + brokerName + ": " + brokerAddress)
        



doASearch(driver, searchURL, "Bonomi", "01089")


brokerIDs = []
brokerNames = []
brokerAddresses = []
#for idNum in range(1499900, allIDNumsLessThan):

def fetchData(urlPrefix, idNum, outputFile):
    url = urlPrefix + str(idNum)
    #response = requests.get(urlPrefix + str(idNum))
    driver.get(url)
    title = (driver.find_elements(By.TAG_NAME, "title")[0]).get_attribute('text')
    titleList = title.split()
    if titleList[0] != "BrokerCheck":
        innerHTML = driver.page_source #is a string
        soup = bsoup(innerHTML, 'html.parser')
        brokerIDs.append(idNum)
        brokerName = title.split(" - ")[0]

        #gets all other names
        otherNames = ""
        otherNameRaw = soup.find('span', attrs={ "data-testid":"other-names"})
        if otherNameRaw is not None:
            prettyOtherNames = otherNameRaw.prettify().split("\n")
            for line in prettyOtherNames:
                if "<" not in line:
                    otherNames += line
        #print("other names: " + str(otherNames))
        
        addressRaw = soup.find('investor-tools-address')
        finalAddress = ""
        if len(str(addressRaw)) > 25:
            prettyAddress = addressRaw.prettify()
            splitAddress = prettyAddress.split("\n")
            for myString in splitAddress:
                if len(myString) > 0:
                    if "<" not in myString and "+" not in myString :
                        myString.strip()
                        finalAddress += (myString + ", ")

        finalString = str(idNum) + "#" + brokerName + "#(" + str(otherNames).strip() + ")#" + finalAddress

        outputFile.writelines(finalString[0:-2] + "\n")

def writeBrokers(startID, endID, outputFile):
    startTime = datetime.now()
    currentID = startID
    while currentID <= endID:
        fetchData(currentID, outputFile)
        currentID += 1
    endTime = datetime.now()
    print("Time elapsed: ", (endTime - startTime))


idnum = 7250255 #Melissa Jane Bishop, zip code 93401

url = "https://brokercheck.finra.org/individual/summary/" + str(idnum)
response = requests.get(url)



driver = webdriver.Chrome()
driver.get(url)
rawhtml = driver.page_source
#title = (driver.find_elements(By.TAG_NAME, "title")[0]).get_attribute('text')
'''
