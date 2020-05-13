import requests
from bs4 import BeautifulSoup
import os
import time

#new URL from 2016

#year = int(input("Enter year: "))
#month = input("Enter month: ")
year = 2015
month = "May"

group1 = ["Japanese", "English"]
group2 = ["Japanese B", "English B"]
group3 = ["Economics", "Business Management", "Psychology", "Geography", "Global Politics", "History", "Environmental Systems and Societies"]
group4 = ["Physics", "Chemistry", "Biology", "Design", "Computer Science"]
group5 = ["Mathematics"]
group6 = ["Music", "Visual Art", "Theatre", "Film"]

validSubjectSelected = False
while True:
    subject = "Chemistry"
    #subject = input("Enter subject: ")
    
    if subject in group1:
        groupNumber = 1
        break
    elif subject in group2:
        groupNumber = 2
        break
    elif subject in group3:
        groupNumber = 3
        break
    elif subject in group4:
        groupNumber = 4
        break
    elif subject in group5:
        groupNumber = 5
        break
    elif subject in group6:
        groupNumber = 6
        break
    else:
        print("Not a valid subject, please try again")
    

groups = {1: "Studies%20in%20language%20and%20literature", 2: "Language%20acquisition", 3: "Individuals%20and%20societies", 4: "Experimental%20sciences" if year < 2014 else "Sciences", 5: "Mathematics", 6: "The%20arts"}
groupName = groups[groupNumber]
print(groupName)

baseURL = ""
if year < 2016: #before the new system
    baseURL = f"https://www.ibdocuments.com/IB%20PAST%20PAPERS%20-%20YEAR/{year}%20Examination%20Session/{month}%20{year}%20Examination%20Session/Group%20{groupNumber}%20-%20{groupName}/"
else:
    pass
    #baseURL = 

# ---------------------------------------------- Web Scraping --------------------------------------------------------
html_content = requests.get(baseURL)
soup = BeautifulSoup(html_content.content, 'lxml')
#print(soup.prettify())

allSubjInGroup = [] #includes files from other subjects in the group like Business Management, Psychology, etc.
rows = soup.find_all("td", class_="indexcolname")
for row in rows:
    allSubjInGroup.append(row.a.get("href"))

subjectFiles = [] #a list of all subject files, e.g. a list of all Economics papers
for file in allSubjInGroup: #for each file in the files of all subjects,
    if subject in file: #if the file name contains the subject name, e.g. 'Economics_paper_1_TZ1_HL.pdf' which contains the subject name "Economics",
        subjectFiles.append(file)

#subjectFiles contains both HL and SL papers, so weed out the ones we don't want

while True:
    level = input("Enter HL, SL or Both: ")
    
    levelFiles = []
    if level == "HL":
        for file in subjectFiles:
            if "SL" not in file: #dont add SL files, but do add HL files or mutual files - e.g. papers for both HL and SL candidates
                levelFiles.append(file)
        break #Valid level input, so break out of the loop
    elif level == "SL":
        for file in subjectFiles:
            if "HL" not in file: #don't add HL files
                levelFiles.append(file)
        break
    elif level == "Both":
        levelFiles = subjectFiles[:]
        break
    else:
        print("Invalid level!")
    


# -------- Finally, download the files -------------

#make a directory to store the files
folderName = str(year) + " " + month + " " + subject + " " + level
os.mkdir(folderName)

start = time.perf_counter()
for file in levelFiles:
    print(f"Downloading {file}...")
    
    fileURL = baseURL + file
    r = requests.get(fileURL)
    
    with open(os.path.join(folderName, file), "wb") as f:
        f.write(r.content)
    print(f"Finished downloading {file}")

finish = time.perf_counter()
print(f"Finished in {round(finish-start, 2)} second(s)")
