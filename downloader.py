#Created on May 12th, 2020
import requests
from bs4 import BeautifulSoup
import os
import threading
import time

#new URL system from Nov 2016 so it doesn't work

#1. scraping group names for < May 2016
#2. scraping file names for < May 2016 and > May 2018
def scrape_table_links(baseURL, classAttribute):
    html_content = requests.get(baseURL)
    soup = BeautifulSoup(html_content.content, 'lxml')
    
    rows = soup.find_all("td", class_=classAttribute)    
    allSubjInGroup = [row.a.get("href") for row in rows if row.find("a") is not None] #includes files from other subjects in the group like Business Management, Psychology, etc.
    return allSubjInGroup

#scraping group names for 2018 onwards
def scrape2(baseURL, language="eng"):
    fallbackLang = "-eng"
    
    html_content = requests.get(baseURL)
    soup = BeautifulSoup(html_content.content, "lxml")
    
    containerDiv = soup.find("section", id="services").find_all("div", class_="container")[1].find("div", class_="row services")
    groupNames = [link.get('href') for link in containerDiv.find_all('a')]
    
    dictWithLanguageOptions = {}
    for fullGroupName in groupNames:
        dashIndex = fullGroupName.find("-") #the fullGroupName is something like Studies_in_language_and_literature-eng.html. If we do fullGroupName.split("-"), the - is not included in the langSuffix like ['Studies_in_language_and_literature', 'eng.html']
        groupName = fullGroupName[:dashIndex] #"Studies_in_language_and_literature", "The_arts", etc
        languageSuffix = fullGroupName[dashIndex:] #'-ls.html', '-eng.html', '-fre.html', '-spa.html' etc
        
        if groupName not in dictWithLanguageOptions.keys():
            dictWithLanguageOptions[groupName] = [languageSuffix]
        else: #it already exists inside the dict
            dictWithLanguageOptions[groupName].append(languageSuffix)
    
    """
    print(dictWithLanguageOptions) #a beautiful dictionary that looks something like this:
    {'Studies_in_language_and_literature': ["-ls.html", '-eng.html', '-fre.html', '-spa.html'], 
    'Language_acquisition': ['-ls.html', '-eng.html', '-fre.html', '-spa.html'], 
    'Individuals_and_societies': ['-ls.html', '-eng.html', '-fre.html', '-spa.html'], 
    'Experimental_sciences': ['-ls.html', '-eng.html', '-fre.html', '-spa.html'], 
    'Mathematics': ['-eng.html', '-fre.html', '-spa.html'], 
    'The_arts': ['-eng.html', '-spa.html']}
    """ 
    
    del groupNames[:] #delete all groupNames
    groupNames.append("BUFFER") #so that when we later do groupNames[groupNumber], it is aligned since Python is 0 indexed and Group Number starts from 1
    
    #Now create a list of 
    for group, listOfLangOptions in dictWithLanguageOptions.items():
        for languageOption in listOfLangOptions:
            if language in languageOption: #e.g. if "eng" in "-eng.html", then we found a match so break
                groupNames.append(group + languageOption)
                break #break out of the inner loop only
        else: #code here will only be executed if the requested language option was not found for this particular group, and for loop was not broken, in which case use the fallback language
            groupNames.append(group + fallbackLang)
    
    return groupNames

def get_files(allSubjInGroup, level, subject):
    #a list of all subject files, e.g. a list of all Economics papers
    subjectFiles = [file for file in allSubjInGroup if subject in file]
    if subjectFiles == []: #if subjectFiles is STILL empty, then it means no files were found for this subject
        return False
    
    #subjectFiles contains both HL and SL papers, so weed out the ones we don't want  
    levelFiles = []
    if level == "HL":
        #don't add SL files, but do add HL files or mutual files - e.g. papers for both HL and SL candidates
        levelFiles = [file for file in subjectFiles if "HLSL" in file or "SL" not in file]
    elif level == "SL":
        #don't add HL files, but do add HL files or mutual files - e.g. papers for both HL and SL candidates
        levelFiles = [file for file in subjectFiles if "HLSL" in file or "HL" not in file]
    else: #level == "Both
        levelFiles = subjectFiles[:]
    if levelFiles == []: #if subjectFiles is not empty but levelFiles is empty, then that means the subject is available but only at a certain level (e.g. only SL ESS)
        return False
    
    return levelFiles #a list of all the files we want to download

#make a directory to store the files,  return the folder name if successful, False if it already exists
def create_dir(year, month, subject, level):
    folderName = str(year) + " " + month + " " + subject + " " + level
    try:
        os.mkdir(folderName)
        return folderName
    except FileExistsError:
        return False 

#Helper threaded function for download()
def download_paper(file, folderName):
    
    fileURL = baseURL + file
    r = requests.get(fileURL)
    
    #before 2016, file = Biology_paper_2__TZ1_SL.pdf, but after 2018, file = Individuals and societies/Geography_paper_2__question_booklet_HLSL.pdf WITH the group name
    if "/" in file:
        file = file[file.index("/")+1:]
    
    with open(os.path.join(folderName, file), "wb") as f:
        f.write(r.content)
    print(f"Finished downloading {file}")

#given a list of all files 
def download(filesToBeDownloaded, folderName):
    start = time.perf_counter() #start timer
    threads = [] #list of threads
    for file in filesToBeDownloaded:
        print(f"Downloading {file}...")
        
        t = threading.Thread(target=download_paper, args=[file, folderName]) #start a new thread to download each paper
        t.start()
        threads.append(t)
    
    for thread in threads:
        thread.join() #Make sure all the threads are complete
    
    finish = time.perf_counter()
    print(f"Finished in {round(finish-start, 2)} second(s)")

# --------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    print("Hello, this script will download past papers from IB Documents.")
    print("Unfortunately, it does not work from November 2016 to November 2017 yet")
    print()
    
    validMonths = ["November", "May"]
    validLevels = ["HL", "SL", "Both"]
    
    group1 = ["English_A1", "French_A1"]
    group2 = ["English_A2", "English_B", "English_ab_initio"]
    group3 = ["Economics", "Business Management", "Psychology", "Geography", "Global Politics", "History"]
    group4 = ["Physics", "Chemistry", "Biology", "Design", "Computer Science", "Sports_exercise_and_health_science", "Astronomy", "Environmental_systems_and_societies"]
    group5 = ["Mathematics"]
    group6 = ["Music", "Visual Art", "Theatre", "Film"]
    
    groups = [group1, group2, group3, group4, group5, group6]
    
    downloads = []
    #For each set of downloads,
    while True:
        
        #Get valid year from user
        while True:
            year = input("Enter year (1991 - 2019): ")
            if year.isnumeric() and 1991 <= int(year) <= 2019: #by short circuiting, year.isnumeric() guarantees int(year) will work
                year = int(year)
                break
            else:
                print("Invalid year!")
        
        #Get valid month from user
        while True:
            month = input("Enter month (November or May): ")
            if month in validMonths:
                break
            else:
                print("Invalid month!")
        
        #Get valid level from user
        while True:
            level = input("Enter level (HL, SL or Both): ")
            if level in validLevels:
                break
            else:
                print("Invalid level!")
        
        #Get valid subject from user
        print("Available subjects are: ")
        for group in groups:
            print(group)
        while True:
            groupNumber = 0
            subject = input("Enter subject to download: ")
            
            for groupNum, group in enumerate(groups):
                if subject in group:
                    groupNumber = groupNum+1 #enumerate() starts from 0, so groupNumber needs to be groupNum + 1
                    break
                
            if groupNumber == 0: #if groupNumber is 0, that means subject was in none of the groups, so we need to try again
                print("Invalid subject, please try again.")
            else:
                break

        #Create the baseURL        
        baseURL = f"https://www.ibdocuments.com/IB%20PAST%20PAPERS%20-%20YEAR/{year}%20Examination%20Session/{month}%20{year}%20Examination%20Session/" #base url for year folder, for both pre- and post-2016 system
        if year < 2016 or (year == 2016 and month == "May"): #before the new system
            allGroupNames = scrape_table_links(baseURL, "indexcolname") #['/IB%20PAST%20PAPERS%20-%20YEAR/2012%20Examination%20Session/', 'Group%201%20-%20Studies%20in%20language%20and%20literature/', 'Group%202%20-%20Language%20acquisition/', 'Group%203%20-%20Individuals%20and%20societies/', 'Group%204%20-%20Sciences/', 'Group%205%20-%20Mathematics/', 'Group%206%20-%20The%20arts/']

            #print("ALL GROUP NAMES", allGroupNames)
            for _groupName in allGroupNames[1:]: #Skip the first element, the '/IB%20PAST%20PAPERS%20-%20YEAR/1998%20Examination%20Session/May%201998%20Examination%20Session/' buffer
                groupNumInGroupName = _groupName[8] #the group names are like 'Group%204%20-%20Sciences/', so the 8th index is '4' in this case, i.e. the group number
                if int(groupNumInGroupName) == groupNumber:
                    groupName = _groupName
                    break

            baseURL += groupName #base url for group folder for pre-2016 system
        elif (year == 2017 or year == 2016 and month == "November"):
            print("SORRY, 2016 NOV to 2017 NOV PAPERS ARE NOT SUPPORTED YET")
            break
        else: #from 2018 onwards
            if groupNumber == 1 or groupNumber == 2: #if user wants to download a language course
                if "English" in subject:
                    requestedLang = "eng"
                elif "French" in subject:
                    requestedLang = "fre"
                elif "Spanish" in subject:
                    requestedLang = "spa"
                else:
                    requestedLang = "ls"
            else: #a non language course, i.e. group 3 - 6
                #TODO: Currently, user cannot select a language for a non language course like I&S or Experimental Sciences
                requestedLang = "eng" #english by default
            
            allGroupNames = scrape2(baseURL, language=requestedLang)
            groupName = allGroupNames[groupNumber]
            baseURL += groupName
    
        downloads.append({"baseURL": baseURL, "year": year, "month": month, "subject": subject, "level": level}) #append a dictionary of the key info
        
        #Once all information has been collected, ask whether to download more sets or start downloading
        x = input("Press enter to start downloading or any other key to download more sets")
        if x == "":
            break
    
    #Actually download 
    for downloadSet in downloads:
        if int(downloadSet["year"]) >= 2018:
            allSubjInGroup = scrape_table_links(downloadSet["baseURL"], None)
        else:
            allSubjInGroup = scrape_table_links(downloadSet["baseURL"], "indexcolname")
        
        
        print(allSubjInGroup)
        filesToBeDownloaded = get_files(allSubjInGroup, downloadSet["level"], downloadSet["subject"])
        
        if filesToBeDownloaded:
            folderName = create_dir(downloadSet["year"], downloadSet["month"], downloadSet["subject"], downloadSet["level"]) #customise this if you want
            
            if folderName:
                download(filesToBeDownloaded, folderName)
                print()
                print(f"Downloaded {folderName}...")
            else: #create_dir returned False, which means the directory already exists
                print("You have already downloaded this set!")
        else: #scrape() returned False, which means it was not able to find papers to download
            print(f"No papers were found for {downloadSet['subject']} at {downloadSet['level']} level in {downloadSet['month']} {downloadSet['year']} :(")