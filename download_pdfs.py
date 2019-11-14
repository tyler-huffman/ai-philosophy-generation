'''
@author: Tyler Huffman
@date: November 5, 2019
@description: Given the results of a search on archive.org, download all results
              in pdf format.
'''
'''
The link to all philosophy text that are in english and always avaliable.
https://archive.org/search.php?query="Philosophy&andSIN=mediatype%3A"texts"&and[]=languageSorter%3A"English"&and[]=loans__status__status%3A"-1"&and[]=mediatype%3A"texts"
'''

import os, sys, time, shelve, wget, os.path
from filecmp import cmp

try:
    import selenium                     #Try to import selenium
    from selenium import webdriver      #Import webdrivers from selenium
except ImportError:                     #If the module is not installed then let the user know and exit the program
    print("Error: Module \"Selenium\" is not installed\nProgram will now exit")
    sys.exit(0)

'''
Create and return a browser instance
'''
def permission_check():    
    try:
        print("Creating Browser")
        driver = webdriver.Firefox()  #Create a browser instance
        print("Browser Created")
        driver.maximize_window()      #Maximize the browser instance
        print("Handing off Broswer Control\n")
        return driver                 #Return the browser instance
    except PermissionError:           #Catch the case where the program needs to run with admin privileges
        print("Error: Program requires administrator priviliges\n Program will not exit")

'''
Scroll to the bottom of a given page
'''
def inf_scroll(driver):
    SCROLL_PAUSE_TIME = 2                                                         #Number of seconds to pause

    last_height = driver.execute_script("return document.body.scrollHeight")      #Get scroll height
    while True:                                                                   #While we are not at the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  #Scroll down to bottom
        time.sleep(SCROLL_PAUSE_TIME)                                             #Wait x seconds for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")   #Calculate new scroll height and compare with last scroll height
        if new_height == last_height:                                             #If the scroll heights are the same we are at the bottom of the page
            break                                                                 #Break out of the loop/program
        last_height = new_height                                                  #Update the last height with the current scroll height

'''
Given the name of an author navigate to a page containing their work, scroll to the very bottom of the page, scrape all the book urls on the page,
and store them in a dictionary where the author is the key and a list containing the urls is the value
'''
def grab_book_links(driver,author):
                                                        #Navigate to the catalouged texts of the author which are in english and do not require a loan/waitlist
    driver.get("https://archive.org/search.php?query=creator%3A%22{}%22&and[]=mediatype%3A%22texts%22&and[]=languageSorter%3A%22English%22&and[]=loans__status__status%3A%22-1%22".format(author))
    inf_scroll(driver)                                  #Load all the works by scrolling to the very bottom of the page
    raw_material = driver.find_elements_by_xpath('/html/body/div[1]/main/div[3]/div/div[2]/div[2]/div/div/div/div[2]/div[1]//a[@href]') #Grab the links to the works                                 
    book_links = []                                     #Create a list to hold the urls 
    for elem in raw_material:                           #Iterate over the object containing the links
        book_links.append(elem.get_attribute("href"))   #Store the urls in the list associated with the author
        ###print(len(book_links))                       ###DEBUGGING: Confirm whether or not we are scraping all the urls
    return book_links                                   #Return the dictionary of urls

'''
Given a list of authors collect the urls to pdfs of their work using the "grab_book_links" method
'''
def urls_to_scrape(driver):
    #Create a list holding the names of the authors whose works we want to scrape
    '''
    Authors with no works published on archives.org:
        Wittenstein
        Roussea
    ====================
    Already Downloaded:
        ["Nietzsche"
        ,"Aristotle"
        ,"Kant"
        ,"Ayn Rand"
        ,"Baruch Spinoza"
        ,"Plato"
        ,"David Hume"
        ,"Karl Marx"
        ,"John Locke"
        ,"Diogenes"
        ,Gottfried Wilhelm Leibniz"]
    '''
    authors = ["G. W. Leibniz"] 
    '''
                "Acquinas"]
               ,"Voltaire"
               ,"Thomas Hobbes"
               ,"Augustine of Hippo"
               ,"Al-Ghazali"
               ,"Montesquieu"
               ,"George Berkeley"
               ,"Simone de Beauvoir"
               ,"Sun Tzu"
               ,"John Stuart Mill"
               ,"Ralph Waldo Emerson"
               ,"Michel Foucault"
               ,"C.G. Jung"
               ,"Epicurus"
               ,"Seneca"
               ,"Marcus Aurelius"
               ,"Epictetus"
               ,"St. Augustine"
               ,"St. Thomas"
               ,"Diderot"
               ,"Fichte"
               ,"Hegel"
               ,"Schopenhauer"
               ,"Freud"
               ,"Heidegger"
               ,"John Dewey"
               ,"Peter Sloterdijk"
               ,"John Rawls"
               ,"Robert Nozick"
               ,"Fyodor Dostoyevsky"
               ,"Otto Rank"
               ,"Goethe"
               ,"Robert Frost"
               ,"Hitler"
               ,"Lenin"]
    '''
    
    '''
    Use shelve to store a dictionary containing the author as the key
    and a list of the urls to their works as the value into a database
    '''
    print("Checking for new authors")
    with shelve.open('scrape_results') as db:  #Open the database
        for author in authors:                 #Iterate over the authors
            if author not in db.keys():        #If the author is not in the database
                print("Adding {}'s works to database".format(author))
                db[author] = grab_book_links(driver,author) #Grab a list of the urls to their work
        print("Cleaning dictionary of old authors")
        '''
        This will only remove authors and their links from the scraping process
        If pdfs have been downloaded the user will have to remove them theirself
        '''
        for existing_authors in db.keys():      #Iterate back over the database
            if existing_authors not in authors: #If the database contains an author not in the provided list
                db.pop(existing_authors,None)   #Remove it from the dictionary
                print("{}'s works have been purged from database".format(existing_authors))
    print("Database Population Complete\n")
    
'''
Create a folder to hold an author's works
'''
def create_folder(path):
    try:
        os.makedirs(path) #Attempt to create the directory
    except OSError:       #If the directory already exists the system will throw an error
        pass              #We respond to the system's throw by telling it to do nothing

'''
Returns True if a file with a given filename already exists
'''
def file_exists(loc):
    return os.path.exists(loc)

'''
Store the file at the end of the url to path
'''
def download(url,path,item):
    path += '\\%s'%item.text         #Define where to store the results of our stream request
    if file_exists(path) == False:   #If no file with the given name exists
       wget.download(url,path)       #Download the file

'''
Show the author and number of works to fetch
'''
def author_info(author,num_of_works):                   #Given the author's name and the number of works
    print("Author: {}".format(author))                  #Print the name of the author whose works we are downloading
    print("Number of Works: {}".format(num_of_works))   #Print the number of works we will attempt to download

'''
Given a list of urls for archive.org, go to the url, navigate to the show all panel, and grab the download links
'''
def download_book_links(driver):
    with shelve.open('scrape_results') as db:
        for author in db.keys():                            #Iterate over each of the authors
            path = "D:\\CS 155\\CS155 Project\\PDFs\\{}".format(author)
            if len(db[author]) == 0:                        #If the author does not have any works                      
                   print("\n{} does not have any works to fetch!\n".format(author))  #Let the user know and move to the next author
            else:                                           #If the author does have works
                create_folder(path)                         #Create the folder to hold the authors work
                author_info(author,len(db[author]))         #Display the current author and the number of works to download
                for i in range(len(db[author])):            #Iterate over each of the authors links
                    driver.get(db[author][i])               #Navigate to the book's link
                    time.sleep(2)                           #Give the page x seconds to load
                    show_all_button = driver.find_element_by_css_selector('a.boxy-ttl:nth-child(2)')  #Define the button to move into a different view of the options to download
                    show_all_button.click()                 #Click the button
                    time.sleep(2)                           #Give the page x seconds to load
                    links = driver.find_elements_by_xpath('/html/body/div[1]/main/div/div/pre/table/tbody//a[contains(@href,".pdf")]') #Grab all the download links containing '.pdf'
                    for item in links:                      #Iterate over the urls in the list
                        try:
                            url = driver.current_url + "//" + item.text  #Define the url where the pdf is, probably, located  
                            download(url,path,item)         #Download the file
                        except:
                            err = sys.exc_info()[0]         #Grab the error
                            print("Error:{}".format(err))   #Print the error
    driver.quit()  #Terminate the browser instance

def MCP():
    print("Starting MCP")
    browser = permission_check() #Create the browser
    urls_to_scrape(browser)      #Create the database of authors and the urls to their works
    download_book_links(browser) #Download the pdfs
    print("\nClosing MCP")

MCP()