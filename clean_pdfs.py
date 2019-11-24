'''
@author:Tyler Huffman
@date:11/10/2019
@description: Given a directory containing folders, iterate through each folder and remove text files and duplicates
'''

import os, sys, pytesseract, tempfile
from filecmp import cmp
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

'''
Check the format of the name of the pdf
'''
def clean_file_names():
    path = r"D:\CS 155\CS155 Project\PDFs"
    authors = os.listdir(path)                          #Grab a list containing the folders at the given path location
    for author in authors:
        os.chdir(path+"\{}".format(author))             #Change the working directory to each author's folder
        works = os.listdir(path+"\{}".format(author))   #Grab a list of the works stored in the folder
        print("Checking {}'s file names".format(author))
        for work in works:                              #Iterate over each of the works in the folder
            new_name = work.strip().replace(" ","_").replace(",","").replace("_text","") #Replace spaces with underscores, eliminate commas, and "_text"s
            if new_name != work:                        #If the name has been modified
                try:                              
                    os.rename(work,new_name)            #Attempt to rename the file
                    print("Renamed from {} to {}".format(work,new_name))
                except FileExistsError:                 #If the file already exists
                    '''
                    This will, hopefully, help detect and remove duplicates
                    '''
                    if compare_size(new_name,work):   #Compare the pre_existing file's size against the current work
                        os.remove(work)               #If the pre-existing file is larger, delete the current work
                    else:                             #If the pre-existing file is smaller
                        os.remove(new_name)           #Delete the "original" file
                        os.rename(work,new_name)      #Rename the current work
                        print("Renamed from {} to {}".format(work,new_name))
'''
Compare the size of two files where "original" represents the file already in possession of the name
and "other" represents the file whose rename causes the error. 
'''
def compare_size(original,other):
    original_size = os.stat(original)                #Find the file size of the current work
    other_size = os.stat(other)                      #Find the file size of the work attempting to rename
    if original_size.st_size >= other_size.st_size:  #If the currently named work is of equal size or bigger then the other return True
        return True                                  
    else:
        return False
'''

'''
def find_dupes(info):
    for i in range(len(info)-1):           #Iterate over the list
        for k in range(i+1,len(info)-1):   #Compare the ith object to every proceeding object
            if info[i][1] == info[k][1]:   #If the pdf titles are the same
                os.remove(info[k][0])      #Remove the kth item
'''
Iterate through the author's directory and remove text files and files containing "_bw"

Note: Files containing "_bw" are duplicate pdfs
'''
def remove_text_files():
    path = r"D:\CS 155\CS155 Project\PDFs"
    authors = os.listdir(path)                          #Grab a list containing the folders at the given path location
    for author in authors:
        os.chdir(path+"\{}".format(author))             #Change the working directory to each author's folder
        works = os.listdir(path+"\{}".format(author))   #Grab a list of the works stored in the folder
        print("Scouring {}'s works for degenerate files".format(author))
        for item in works:                              #Iterate over each of the works in the folder
            ###print(item)                              ###DEBUGGING: See the name of the item
            if item.endswith(".txt") or "_bw" in item:  #If the item is a text file or a copy of another pdf or not related
                os.remove(item)                         #Delete it
                print("Deleted {}".format(item))

'''
Iterate through each author's directory and remove files based on whether or not the byte data is the same

Note: This is not fool proof. Different uploaders have different versions of different quality.
      In other words, there is no guarantee we can catch duplicates by attempting to match their bytes.
      Hence why the "clean_file_names" method was created.
'''
def byte_compare():
    path = r"D:\CS 155\CS155 Project\PDFs"    #Provide the path to the directory containing the author's and their work
    authors = os.listdir(path)               #Grab a list containing the folders at the given path location

    for author in authors:                                           #Iterate through each folder
        works = os.listdir(path+"\{}".format(author))                #Grab a list of the works stored in the folder
        os.chdir(path+"\{}".format(author))                          #Change the working directory to each author's folder
        print("Checking {}'s works for duplicates".format(author))
        
        '''
        Check the author's pdfs for duplicate files by comparing the bytes of the pdf
        '''
        for k in range(len(works)):                                  #Starting at the front of the list                                        
            ###print("Work:{}".format(work))                         ###DEBUGGING: Check which file is being compared
            for i in range(k+1,len(works)-1):                        #Compare the file to every file in front of it
                ###print("Work[i]:{}".format(num_of_works[i]))       ###DEBUGGING: Check which file is being compared against
                if cmp(works[k],works[i], shallow=False):                #If the works are similiar
                    os.remove(works[i])                              #Delete the file from the hard drive
                    works.remove(works[i])                           #Update the list
                    print("Removed {}".format(works[i]))

'''
Create a folder to hold an author's works
'''
def create_folder(path):
    try:
        os.makedirs(path) #Attempt to create the directory
    except OSError:       #If the directory already exists the system will throw an error
        pass              #We respond to the system's throw by telling it to do nothing
'''
Grab the pdfs located at a given path, convert them to text, and save the text file to another given path
'''
def convert_to_text():
    path_to_pdfs = r"D:\CS 155\CS155 Project\[Cleaned] PDFs"    #Provide the path to the directory containing the author's and their work
    authors = os.listdir(path_to_pdfs)                          #Grab a list containing the folders at the given path location
    for author in authors:                                      #Iterate through each folder
        works = os.listdir(path_to_pdfs + "\{}".format(author)) #Grab a list of the works stored in the folder
        save_path  = r"D:\CS 155\CS155 Project\Text Files" + "\{}".format(author) #Define where to save the text files
        create_folder(save_path)                                #Create a folder for the author in the
        os.chdir(path_to_pdfs + "\{}".format(author))           #Change the working directory to each author's folder
        print("Converting {}\'s works".format(author))
        for work in works:                                                    #Iterate over each of the author's works
            if work[-4:] == ".pdf":                                           #Check the file extenstion to make sure we are working with a pdf
                title = work.replace(work[-3:],"txt")                         #Grab the name to assign the text file
                if title not in os.listdir(save_path):                        #If the text file does not exist in the save path
##                    try:                                                      #Attempt to convert the pdf to text, catching the instances where the pdf requires a password
                    print("\nAttempting to convert {}".format(work))
                    text = convert_pdf_to_txt(work)                       #Grab the text contents of the pdf
                    '''
                    If the length of the converted text is less than roughly 5000 characters then we have either hit one of google's scanned pdfs
                    and if the length is 0 then we have a scanned pdf. Either way, we are left with a scanned pdf and no text to show from it.
                    Thus, we turn to pycor and attempt to convert the pdf to text via image analysis. 
                    '''
                    if len(text) > 5000:                    
                        complete_save_path = os.path.join(save_path,title)        #Create the path to save the text file
                        with open(complete_save_path,'w',encoding='utf-8') as f:  #Open and write the converted text into a file at the designated location
                            f.write(text)           
                        print("{} Converted".format(work))
                    else:
                        print("Passed on {}".format(work))
                        pass
                        #convert_scan_to_text(title,work)
##                    except TypeError:                                             #If the pdf requires a password skip it
##                        print("\n!!!")
##                        print("Attention: {} requires password, skipping.".format(work))
##                        print("!!!\n")
                else:
                    print("{} already exists!".format(title))
            else:
                print("\nAttention: {} does not belong with the pdfs.\nPlease remove the file from {}\'s PDF directory.\n".format(work,author))
        
        print("")
    print("Conversion Complete")

'''
I can piece together the gist of what this snippet of code is doing but some of the library specifics escape me.
At a later date I will go back through and add comments... Mabye

Source: https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
'''
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True 
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text

def convert_scan_to_text(title,pdf):
    print("Converting a scan of {}".format(pdf))
    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(pdf, output_folder=path) #Convert the pdf into images and save in a temp directory
        print("All pages stored in temporary storage")
        image_counter = 1                  #An image counter for the number of pages

        for page in images_from_path:                                 #Look at each page in the pdf
            filename = "page_" + str(image_counter) + "."  #Set the filename to correspond with the page number
            ###File does not save
            page.save(filename,'JPEG')                     #Save the image locally
            image_counter += 1                             #Increase the page counter
            print("Page {} is a model".format(image_counter))

        file_limit = image_counter - 1
        print("Extracting text from image")
        with open(title, 'a') as f:
            for i in range(1,file_limit + 1):
                filename = "page_"+str(i)+".jpeg"
                text = str(((pytesseract.image_to_string(Image.open(filename)))))
                text = text.replace('-\n','')
                f.write(text)
        print("Pause, The text should be converted... Should. Go check on it")
        input()

def MCP():
    convert_to_text()
    
MCP()