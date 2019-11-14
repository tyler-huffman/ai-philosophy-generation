'''
@author:Tyler Huffman
@date:11/10/2019
@description: Given a directory containing folders, iterate through each folder and remove text files and duplicates
'''
import os
from filecmp import cmp

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

def MCP():
    remove_text_files()
    clean_file_names()
    byte_compare()

MCP()