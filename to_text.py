import os, sys, pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
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
                        convert_scan_to_text(title,work)
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
    print("Working on Converting a scan of {}".format(title))
    pages = convert_from_path(pdf,500) #Convert the pdf into images
    print("All pages stored in variable")
    image_counter = 1                  #An image counter for the number of pages

    for page in pages:                                 #Look at each page in the pdf
        filename = "page_" + str(image_counter) + "."  #Set the filename to correspond with the page number
        page.save(filename,'JPEG')                     #Save the image locally
        image_counter += 1                             #Increase the page counter
        print("Page {} is a model".format(image_counter))

    file_limit = image_counter - 1
    print("Extracting text from image")
    with open(title, 'a') as f:
        for i in range(1,file_limit + 1):
            filename = "page_"+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace('-\n','')
            f.write(text)
    print("Pause, The text should be converted... Should. Go check on it")
    input()

def MCP():
    convert_to_text()
    
MCP()