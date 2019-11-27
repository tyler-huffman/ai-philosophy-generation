'''
Not perfect but it severly reduces the amount of time I will have to spend cleaning the text files
'''
import re, os, nltk.data, getpass


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')    #Load NLTK's toenzier for english

path_to_authors = "D:\\CS 155\\CS155 Project\\Text Files"
authors = os.listdir(path_to_authors)

#for author in authors:
for i in range(1):
    author = "Nietzsche"
    os.chdir(path_to_authors+"\{}".format(author))                          #Change the working directory to each author's folder
    #path_to_works = "D:\\CS 155\\CS155 Project\\Text Files\\{}".format(author)
    #works = os.listdir()
    works = ["On_the_Pathos_of_Truth.txt","On_Truth_and_Lying.txt","On_the_Greek_State_&_Homer\'s_Contest.txt","The_Dionysian_Vision_of_the_World.txt","The_Philosopher_Reflections_on_the_Struggle_Between_Art_and_Knowledge.txt"]
    for work in works:
        print("Cleaning {}".format(work))
        #Read in the contents of the text file and break the contents into a list
        with open(work,'r', encoding='utf-8') as f:
            contents = f.read().split()

        '''
        Iterate over the text file removing the numbers and chucking the results into a string
        '''
        punc = set([".","?","!"])     #Define the punctuation chars
        new_str = ""                  #Create a string to hold the cleaned text
        for word in contents:         #Iterate over each word of the work
            for char in word:         #Iterate over each character
                if char.isdigit():    #If the character is a digit we do not append it to the new string
                    pass
                elif char in punc:    #If the character is a punctutation mark append the character to the new string along with a new line char
                    new_str += char + "\n"
                else:                 #If the character is a normal character then append the character to a string
                    new_str +=  char
            new_str += " "            #Throw a space after each word
        
        ### A re attempt to define how to handle hyphens after a sentence
        ### new_str =  re.sub("[!.?\"](?!(-|\s-))$","\n",new_str)

        '''
        Some of the works include the german words in brackets. While useful and enlightenting they are not helpful to a program learning
        to construct sentences. Thus, when we find a bracket we remove them and their contents
        '''
        new_str = re.sub("\[.*\]","",new_str)
        text = tokenizer.tokenize(new_str)    #Tokenize the text and throw it into a list
        final_text = " ".join(text)           #Create one large body of work from the tokenized text
        path_to_save = "C:\\Users\\{}\\Documents\\GitHub\\ai-philosophy-generation\\Works\\{}\\{}".format(getpass.getuser(), author,work)
        with open(path_to_save, 'w', encoding='utf-8') as f:
            f.write(final_text)
        print("{} Cleaned\n".format(author))
        #print(new_str)