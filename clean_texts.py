import os, sys, webbrowser, re, getpass, operator
from langdetect import detect
from langdetect import lang_detect_exception
'''
Return the contents of a file
'''
def open_text(filename):
    if (file_exists(filename)):
        with open(filename, 'r', encoding='utf-8-sig') as f:
            contents = remove_non_breaking_hyphens(f.read())
        return contents.split()
    else:
        print("Error: {} does not exist in the provided path\nProgram will not exit".format(filename))
        sys.exit(0)

'''
Check whether the file exists in the specified directory
'''
def file_exists(filename):
    #Grab a list of the text files in the directory
    text_files = [i for i in os.listdir() if ".txt" in i]
    #Return a boolean value indicating if the text file is in the directory
    return filename in text_files

'''
Make sure the contents of the text file are ascii characters and replace any non-ascii characters
'''
def is_ascii(contents):
    replace_ords = [915,
                    8221,
                    8220,
                    8230,
                    233,
                    232, 
                    8217,
                    821,
                    9500,
                    241,
                    224,
                    8211,
                    8212,
                    228,
                    246,
                    234,
                    230,
                    239,
                    249,
                    339,
                    252,
                    226,
                    339,
                    244,
                    8216,
                    198,
                    196,
                    338,
                    200,
                    201,
                    207,
                    172,
                    231,
                    275,
                    333,
                    299,
                    257,
                    64257,
                    64258]
    for i in range(len(contents)):           #Iterate over the text
        for char in range(len(contents[i])): #Iterate over characters of each word
            curr_char = contents[i][char]    #Grab the current char
            start = max(i-5,0)               #Grab the five chars before the current 
            end = min(i+5,len(contents)-1)   #Grab the five chars after the current
            try:
                prev_char = contents[i][char-1]
            except IndexError:
                prev_char = " "
            try:                                
                next_char = contents[i][char+1] #Try grabbing the next char
            except IndexError:                  #If we get an IndexError we're at the the end of the document 
                next_char = " "                 #So we assign an empty space to the next char 
            if ord(curr_char) > 127:            #Find the characters who are not in ascii form
                #If the char is a recognized non-ascii char then automatically make the ascii substitution 
                if  ord(curr_char) in replace_ords:
                    print(contents[start:end])
                    #Get the ascii version of the word
                    new_word = replace_nonascii_punct(contents[i],ord(curr_char), ord(next_char),ord(prev_char))
                    #Replace the non-ascii version with the ascii version
                    contents[i] = new_word
                    print(contents[start:end])
                    print("")
                else:  #If the char is unrecognized, bring it to the user's attention. 
                    print(contents[start:end])
                    print("\nPrev_Char: {}   Prev_Ord: {}\nCurr_Char: {}   Curr_Ord: {}\nNext_Char: {}    Next_Ord: {}".format(prev_char, ord(prev_char),curr_char,ord(curr_char), next_char, ord(next_char)))
                    input("\nWaiting for User resolution...")
    return contents #Return the 

'''
Given a word with a non-ascii punctuation, return the ascii version
'''
def replace_nonascii_punct(faulty_word,curr_char, next_char, prev_char):
    if (next_char == 241 and curr_char == 9500) or ((curr_char == 257) or (curr_char == 228) or (curr_char == 9500) or (curr_char == 224) or (curr_char == 226)):
        replacement = "a"
    if (curr_char == 196):
        replacement = "A"
    if ((curr_char == 9500) and (next_char == 9570)) or (curr_char == 246) or (curr_char == 228) or (curr_char == 244) or (curr_char == 333):
        replacement = "o"
    if (curr_char == 915) or (curr_char == 8221) or (curr_char == 8220):
        replacement = "\""
    if (curr_char == 8230):
        replacement = "..."
    if (curr_char == 233) or (curr_char == 232) or (curr_char==234) or (curr_char == 275):
        replacement = "e"
    if (curr_char == 8217) or (curr_char == 8216):
        replacement = "\'"
    if (curr_char == 8211) or (curr_char == 8212):
        replacement = "-"
    if (curr_char == 230) or (curr_char == 339):
        replacement = "ae"
    if (curr_char == 198):
        replacement = "AE"
    if (curr_char == 239) or (curr_char == 299):
        replacement = "i"
    if (curr_char == 249) or (curr_char == 252):
        replacement = "u"
    if (curr_char == 338):
        replacement = "oe"
    if (curr_char == 200) or (curr_char == 201):
        replacement = "E"
    if (curr_char == 207):
        replacement = "I"
    if (curr_char == 172):
        replacement = "-"
    if (curr_char == 231):
        replacement = "c"
    if (curr_char == 64257) or (curr_char == 64258):
        replacement = "fi"
        
    idx = faulty_word.index(chr(curr_char)) #Find the index where the char is located
    ###DEBUGGING:See the integer value of the current char along with the following char
    ###print("\nCurr_Char: {}   Curr_Ord: {}\nNext_Char: {}    Next_Ord: {}".format(chr(curr_char),curr_char, chr(next_char), next_char))
    
    #Grab everything up to the index of the invalid char and replace it with the word along with an ascii quotation mark
    new_word = "".join(faulty_word[:idx] +  replacement + faulty_word[min(idx+1,len(faulty_word)):])
    return new_word #Replace the invalid entry with the valid one

'''
Until Dormammu provides a valid answer, Dr. Strange them.

(Until the user decides to play by the defined rules trap them in a while loop)
'''
def answer_me(text_in_question):
    '''
    y: Yes
    n: No
    r: Review
    '''
    valid_options = set(list("y,n,r"))  #Define the valid options
    while True:                         #Until the user supplies a valid answer
        answer = str(input("Remove: " + str(text_in_question) + " ")).lower() #Grab the user's answer
        if answer not in valid_options:
            print("Error: Invalid Option Selected.\n Try Again!")
        else:
            return answer  #Return the user's answer

'''
Remove all numbers
'''
def remove_digits(contents):
    return re.sub("(?=\s|\S)[\d](?=\d|\S|\.|\)){0,}","",contents)

'''
The names quite self-explanatory isn't it
'''
def remove_non_breaking_hyphens(contents):
    return re.sub("(-\\n)(?!=-)","",contents)

'''
The names really do explain themselves...
'''
def remove_underscores(contents):
    return re.sub("[_]","",contents)

def re_wrapper(contents):
    return remove_digits(remove_underscores(remove_non_breaking_hyphens(contents)))

def find_brackets(contents):
    symbols = [('(',')'),('[',']')]
    results = []
    start,counter = 0,0
    for x in range(len(symbols)):
        for i in range(len(contents)-1):
            if contents[i] == symbols[x][0]:
                if counter == 0:
                    start = i
                counter += 1
            elif contents[i] == symbols[x][1] and counter != 0:
                counter -= 1
                if counter == 0:
                    results.append((contents[start:i+1],start,i+1))
            else:
                    pass
            if i == len(contents) - 1 and counter != 0:
                print("Error: Origin Index: {}\nLandscape: {}\nProgram will now exit".format(start,contents[max(0,start-5),min(start+5,len(contents))]))
                sys.exit(0)
    results.sort(key=lambda elem: elem[1])
    return results
    
'''
Given a text file, find all non-english words in either brackets or parenthesis and remove them.
If the phrase inside a parenthesis or bracket is english we ask the user to decide whether to
remove the phrase
'''
def brac_paren_alterations(contents):
    corrections = find_brackets(contents)  #Grab the starting and ending location of the indices along with the text at and between said indices
    print("Number to Review:",len(corrections))
    manual_corrections = []    #Create a list to hold the phrases the user wants to review manually
    new_str = ""               #Create a string to hold the cleaned version
    prev_end = 0               #Create a psuedo pointer to reference the ending index of the last undesired symbol

    for i in range(len(corrections)):   #Examine each segement of the text which has been flagged
        correction_made = False         #Keep track of the decision to modify the contents
        curr_start = corrections[i][1]  #Grab the starting index
        curr_end = corrections[i][2]    #Grab the ending index
        text = corrections[i][0]        #Grab the text spanning the indices
        '''
        The problem with changing "de" to "en" and swapping the bodies of the if/else statements
        is there are some words, such as "\"spirit\"" which langdetect sees as Latvian...
        Since this tool is created with the intent of mass cleaning text files for a given author
        the solution is, for any non-english author, to change "'de'" to the two symbol shorthand 
        of the author's native langauge.
        '''
        try:
            if (len(text) == 2) or ("Footnote" in text) or (detect(text) == 'de'):                       
                new_str += contents[prev_end:curr_start] #Record from the previous ending index to where the symbol starts
                correction_made = True                   #Flip the switch showing an alteration was made
                print("Auto-Removed word/phrase: {}".format(text))
            else:
                #Handle any non-native language text
                answer = answer_me(text)   #Grab what the user wishes to do
                if answer == 'y':          #If they want to remove the entry   
                    new_str += contents[prev_end:curr_start]  #Record from the previous ending index to where the symbol starts
                    correction_made = True #Flip the switch showing an alteration was made
                    #print("Removed word/phrase: {}".format(text))
                elif answer == 'n':    #If the user wishes to keep the entry, do nothing
                    pass
                else:                                #If the user wishes to manually review the entry
                    manual_corrections.append(text)  #Grab the phrase in question and store it into a list
        except lang_detect_exception.LangDetectException:
            #Handle any non-native language text
            answer = answer_me(text)   #Grab what the user wishes to do
            if answer == 'y':          #If they want to remove the entry   
                new_str += contents[prev_end:curr_start]  #Record from the previous ending index to where the symbol starts
                correction_made = True #Flip the switch showing an alteration was made
                #print("Removed word/phrase: {}".format(text))
            elif answer == 'n':    #If the user wishes to keep the entry, do nothing
                pass
            else:                                #If the user wishes to manually review the entry
                manual_corrections.append(text)  #Grab the phrase in question and store it into a list
        if correction_made:        #If an alteration was made to the text
            prev_end = curr_end    #Set prev_end equal to the last index of the current "undesirable" symbol
                 
    new_str += contents[prev_end:] #After all alterations have been made, make sure to include everything after the final cut!
    print("Starting Length of Contents:", len(contents))
    print("Final Length of Contents:",len(new_str))
    return new_str, manual_corrections

'''
Save the cleaned file 
'''
def save_file(filename,contents):
    cleaned_filename  ="C:\\Users\\{}\\Documents\\GitHub\\ai-philosophy-generation\\Works\\Nietzsche\\".format(getpass.getuser()) +"[Cleaned]"+ filename                   #Give the cleaned file a new name
    with open(cleaned_filename, 'w', encoding='utf-8') as f:  #Save the contents to the file
        f.write(contents)
    return cleaned_filename

'''
If anything was flagged for review open up the cleaned version and iterate over the text 
the user needs to revies
'''
def make_manual_corrections(filename,manual_corrections):
    if manual_corrections:                 #If the user needed to review any of the proposed changes
        webbrowser.open(filename)          #Open the new file
        print("\n"*100)                    #Clear the terminal window
        print("{} Places require manual review".format(len(manual_corrections)))
        '''
        In case the name of the list isn't obvious, the user will have to open the text file
        and decide what action needs to be taken
        '''
        for to_fix in manual_corrections:  #Display each of the revisions one by one to the console
            print(to_fix)
            input("Press any key to continue")
        print("!!!---ATTENTION---!!!")
        print("Remember to save the file!")
        input("!!!---ATTENTION---!!!")
  
'''
Wrapper for cleaning
'''
def clean(filename):
    try:
        print("Cleaning {}".format(filename))
        contents,fix = brac_paren_alterations(re_wrapper(" ".join(is_ascii(open_text(filename)))))
        new_filename = save_file(filename,contents)
        make_manual_corrections(new_filename,fix)
        print("\n\n{} Cleaned\n\n".format(filename))
    except KeyboardInterrupt:
        print("Exiting the Matrix")
        
author = "Nietzsche"
filename = "On_the_Greek_State_&_Homer's_Contest.txt"
os.chdir("C:\\Users\\{}\\Desktop\\Text Files\\{}".format(getpass.getuser(), author))
#Grab all the text files in the author's folder
#works = [i for i in os.listdir() if ".txt" in i] #Grab the text file(s)
#for work in works:
clean(filename)

