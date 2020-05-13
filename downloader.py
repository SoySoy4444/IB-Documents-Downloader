#Created on May 12th, 2020
import requests
from bs4 import BeautifulSoup
import os
import threading
import time

#new URL system from Nov 2016 so it doesn't work

def scrape_table_links(baseURL):
    html_content = requests.get(baseURL)
    soup = BeautifulSoup(html_content.content, 'lxml')
    #print(soup.prettify())
    
    allSubjInGroup = [] #includes files from other subjects in the group like Business Management, Psychology, etc.
    rows = soup.find_all("td", class_="indexcolname")
    for row in rows:
        allSubjInGroup.append(row.a.get("href"))
    
    return allSubjInGroup

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
    print("Unfortunately, it does not work from November 2016 onwards yet")
    print()
    
    validMonths = ["November", "May"]
    validLevels = ["HL", "SL", "Both"]
    
    group1 = ["English_A1"]
    group2 = ["English_A2", "English_B", "English_ab_initio"]
    group3 = ["Economics", "Business Management", "Psychology", "Geography", "Global Politics", "History", "Environmental Systems and Societies"]
    group4 = ["Physics", "Chemistry", "Biology", "Design", "Computer Science", "Sports_exercise_and_health_science", "Astronomy"]
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
        baseURL = ""
        if year < 2016 or (year == 2016 and month == "May"): #before the new system
            baseURL = f"https://www.ibdocuments.com/IB%20PAST%20PAPERS%20-%20YEAR/{year}%20Examination%20Session/{month}%20{year}%20Examination%20Session/" #base url for year folder
            allGroupNames = scrape_table_links(baseURL) #['/IB%20PAST%20PAPERS%20-%20YEAR/2012%20Examination%20Session/', 'Group%201%20-%20Studies%20in%20language%20and%20literature/', 'Group%202%20-%20Language%20acquisition/', 'Group%203%20-%20Individuals%20and%20societies/', 'Group%204%20-%20Sciences/', 'Group%205%20-%20Mathematics/', 'Group%206%20-%20The%20arts/']
            groupName = allGroupNames[groupNumber]
            baseURL += groupName #base url for group folder
        else:
            #groupsDict = {1: "Studies_in_language_and_literature", 2: "Language_acquisition"} 
            #these group names also need a "-eng.html" suffix too...
            pass
            #baseURL =
    
        downloads.append({"baseURL": baseURL, "year": year, "month": month, "subject": subject, "level": level}) #append a dictionary of the key info
        
        #Once all information has been collected, ask whether to download more sets or start downloading
        x = input("Press enter to start downloading or any other key to download more sets")
        if x == "":
            break
    
    #Actually download 
    for downloadSet in downloads:
        allSubjInGroup = scrape_table_links(downloadSet["baseURL"])
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