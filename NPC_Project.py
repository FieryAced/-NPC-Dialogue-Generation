from random import randint
import openai
import sys

openai.api_key = '' ##Insert API Key Here

def gpt3(prompt, engine='text-davinci-002', response_length=64,
         temperature=0.7, top_p=1, frequency_penalty=0, presence_penalty=0,
         start_text='', restart_text='', stop_seq=[]):
    response = openai.Completion.create(
        prompt=prompt + start_text,
        engine=engine,
        max_tokens=response_length,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop_seq,
    )
    answer = response.choices[0]['text']
    answer = answer.strip()
    new_prompt = prompt + start_text + answer + restart_text
    return answer, new_prompt

# def chat(prompt, name = None, file = None):
#     if name is None:
#         name = "NPC"
#     name += ":"
#     if (file is not None):
#         file.write(prompt)
#     endFlag = False
#     while True:
#         if endFlag:
#             return
#         playerMsg = input('Player: ')
#         if len(playerMsg) == 0:
#             endFlag = True
#         if endFlag:
#             print("Did the NPC do a good job in it's task?")
#             selfEval(prompt,name)
#             prompt += "Did the NPC do a good job in it's task?"
#         else:
#             prompt += "\nPlayer: "+ playerMsg
            
#         if (file is not None):
#             file.write("Player: "+ playerMsg+"\n")
#         answer, prompt = gpt3(prompt,
#                               temperature=0.77,
#                               frequency_penalty=0.33,
#                               presence_penalty=0.2,
#                               top_p=0.9,
#                               start_text='\n'+name+':',
#                               restart_text='',
#                               stop_seq=['\nPlayer:', '\n']) ## Subject to change
#         if (file is not None):
#             file.write(answer + "\n")
#         print(name+ answer)      


def autochat(NPCHeader, PlayerHeader, NPC, name = None, file = None, length = 10,
             temp = 0.9, model = 'text-davinci-002'):
    if name is None:
        name = "NPC"
    name += ":"
    if (file is not None):
        file.write("NPC Header:\n"+NPCHeader+"===============================\n")
        file.write("Player Header:\n"+PlayerHeader+"===============================\n")
    dialogue = name + " " + NPC.greeting + "\n"
    NPC_history = []
    player_history = []
    dynamic_frequency = 0
    for messages in range(length):
        for attempts in range(3):
            answer, prompt = gpt3(PlayerHeader+dialogue, ## Swapped headers for Player header
                                temperature=temp,
                                engine=model,
                                frequency_penalty=0.33+dynamic_frequency,
                                presence_penalty=0.75, ## Player should always try to approach new subjects
                                top_p=1,
                                response_length=128,
                                start_text='\nPlayer:',
                                restart_text='',
                                stop_seq=['\nPlayer:','Player:','\n'+name, name])
            answer = "".join(filter(lambda char: char not in "\n", answer)) ## Remove all instances of newline characters
            if player_history.count(answer) > 1 or len(answer.strip()) == 0:
                dynamic_frequency += 0.33
                continue
            else:
                break
        dynamic_frequency = 0
        dialogue += "Player:" + answer + "\n"
        player_history.append(answer)
        print("Player:" + answer + "\n") ##optional print statements
        for attempts in range(3):
            answer, prompt = gpt3(NPCHeader+dialogue, ## Swapped headers for NPC header
                                temperature=temp,
                                engine=model,
                                frequency_penalty=0.33+dynamic_frequency,
                                presence_penalty=0.5,
                                top_p=1,
                                response_length= 256,
                                start_text='\n'+name,
                                restart_text='',
                                stop_seq=['\nPlayer:','Player:','\n'+name, name])
            answer = "".join(filter(lambda char: char not in "\n", answer)) ## Remove all instances of newline characters
            if NPC_history.count(answer) > 1 or len(answer.strip()) == 0: ## I.e. if there's more than one appearance already in the dialogue, rerun with higher penalties
                dynamic_frequency += 0.33
                continue
            else:
                break
        answer = "".join(filter(lambda char: char not in "\n", answer)) ## Remove all instances of newline characters
        dialogue += name + answer + "\n"
        dynamic_frequency = 0
        NPC_history.append(answer)
        print(name + answer + "\n") ##optional print statements
    file.write(dialogue)
    return dialogue
    

def generateNPCHeader(worldPrompt=None, 
                npcType = None,
                traits = None,
                state = None,
                goal = None,
                name = None,
                genre = None):
    prompt = "You are an NPC in a game.\n"
    if (name is not None):
        prompt += "Your name is " + name +"\n"
    if (worldPrompt is not None):
        prompt += worldPrompt +"\n"
    if (npcType is not None):
        prompt += "NPC Type: " + npcType +"\n"
        if genre is not None:
            npcObject = NPC(type=npcType,genre=genre)
        else:
            npcObject = NPC(type=npcType)
    else:
        if genre is not None:
            npcObject = NPC(genre=genre)
        else:
            npcObject = NPC()
    if (traits is not None):
        prompt += "Traits: " + traits +"\n"
    if (state is not None):
        prompt += "State: " + state +"\n"
    if (goal is not None):
        prompt += "Goal: " + goal +"\n"
    

    return prompt+"\n",npcObject

def generatePlayerHeader(worldPrompt=None, 
                npcType = None,
                traits = None,
                state = None,
                goal = None,
                name = None):
    prompt = "You are a Player in a video game.\nThis is a conversation between an NPC and a player.\n"
    if (npcType is not None):
        type = npcType.lower()
        if (name is not None):
            npcName = name
        else:
            npcName = "the NPC"
        if (type == "vendor"):
            prompt += "You are approaching " + npcName + " to buy some items.\n"
        elif (type == "quest giver"):
            prompt += "You are approaching " + npcName + " to obtain a quest.\n"
        elif (type == "service"):
            prompt += "You are approaching " + npcName + " to seek the service they specialize in.\n"
        elif (type == "companion"):
            prompt += npcName + " is your traveling companion currently.\n"
        elif (type == "ally"):
            prompt += npcName + " is an ally to you.\n"
        elif (type == "story teller"):
            prompt += npcName + " has a wealth of knowledge to share.\n"
    if (name is not None):
        prompt += "The NPC's name is " + name +"\n"
    if (worldPrompt is not None):
        prompt += worldPrompt +"\n"
    if (npcType is not None):
        prompt += "NPC Type: " + npcType +"\n"
    if (traits is not None):
        prompt += "NPC Traits: " + traits +"\n"
    if (state is not None):
        prompt += "NPC State: " + state +"\n"
    if (goal is not None):
        prompt += "NPC's Goal: " + goal +"\n"

    return prompt+"\n"

def selfEval(dialogue, file, type, genre):
    type_skip = False
    if type is None:
        type = "None" ## Need this or it errors on the evalList for some reason
        type_skip = True
    elif type == "service":
        type = "service provider"
    else:
        type = type.lower()
    if genre is None or genre == "real-world":
        genre == "real world"
    else:
        genre = genre.lower()
    coherencyExample = open("self-eval\\coherency_primer.txt")      ## For Windows file systems
    #coherencyExample = open("self-eval/coherency_primer.txt")      ## For Linux file systems
    coherencyExample = coherencyExample.read()
    believabilityExample = open("self-eval\\believability_primer.txt")      ## For Windows file systems
    #believabilityExample = open("self-eval/believability_primer.txt")      ## For Linux file systems
    believabilityExample = believabilityExample.read()
    repetivityExample = open("self-eval\\repetivity_primer.txt")      ## For Windows file systems
    #repetivityExample = open("self-eval/repetivity_primer.txt")      ## For Linux file systems
    repetivityExample = repetivityExample.read()
    points = 0
    ambiguous = 0
    preamble = "Below is a conversation between an NPC and a player.\nUse this conversation to answer the questions that follow.\n\n"
    promptAid = "Answer the question using only the options provided.\nShort answers, no explanations needed, select only one option."
    evalList = ["From a scale of 1-5, how well did the NPC act as a(n) "+type+"? Please answer the question using only a number, 1 to 5, with \"1\" being badly and \"5\" being very well.",
                "From a scale of 1-5, how likely is it for the above conversation to be set in a "+genre+" setting? Please answer the question using only a number, 1 to 5, with \"1\" being least likely and \"5\" being most likely.",
                "From a scale of 1-5, how coherently did the NPC act and behave? Please answer the question using only a number, 1 to 5, with \"1\" being least coherent and \"5\" being most coherent.",
                "From a scale of 1-5, how believable did the NPC act and behave? Please answer the question using only a number, 1 to 5, with \"1\" being least believable and \"5\" being most believable.",
                "From a scale of 1-5, how much did the NPC repeat a sentence? Please answer the question using only a number, 1 to 5, with \"1\" being barely any repeated sentences and \"5\" being many instances of repeated sentences."]
    writeBuffer = ""
    ##FIX
    for i in range(len(evalList)):
        question = evalList[i]
        dynamicPrompt = preamble+dialogue+"\n\n"+promptAid+question
        if i == 0 and type_skip:
            ambiguous += 5
            writeBuffer += "\n<No type specified>\n>"
            continue
        elif i == 2:
            dynamicPrompt = coherencyExample + dynamicPrompt
        elif i == 3:
            dynamicPrompt = believabilityExample + dynamicPrompt
        elif i == 4:
            dynamicPrompt = repetivityExample + dynamicPrompt
        response = openai.Completion.create(
                                        prompt=dynamicPrompt,
                                        engine="text-davinci-002",
                                        max_tokens=32,
                                        temperature=0, ## Deterministic completions only
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0,
                                        logprobs=5
                                        )
        answer = response.choices[0]['text']
        answer = answer.strip()

        if answer.isnumeric():
            if i == 4:
                points += 6 - int(answer) ## Inverted scale for repetivity
            else:
                points += int(answer) ##normal scale for rest
        else: 
            ambiguous += 5
            ## The chance of this happening is incredibly small.
            ## However, in the case that it somehow doesn't generate
            ## a number, remove 5 from the total possible score and ignore
            ## this result.
            
        print(points) ## mostly here for debug purposes
        writeBuffer += "\n"+question+"\n>"+answer+"\n"
    file.write("Score: "+ str(points)+"/"+ str((len(evalList)*5)-ambiguous))
    file.write("===========================================") ## To make it look pretty. It matters.
    file.write(writeBuffer)


class NPC:
    
    def __init__(self, type=None, genre="real-world"):

        if type is not None:
            type = type.lower()
        genre = genre.lower()
        greeting_dict = {
            "sci-fi": ["Hey there","Hello","Greetings",""],
            "fantasy": ["Good day","Hello","Greetings","Well met","Hail"],
            "real-world": ["Hey there","Hello","Hi",""],
            "western": ["Howdy","Greetings","Well met","Salutations"]
        } ## this is all debatable.

        inquiry_dict = {
            "ally":["Nice to see you around","Nice to see a friendly face","Need anything?"],
            "companion":["What is it?","What's up?","Need anything?","Yes?", "We should get going."],
            "story teller":["Did you hear about what happened?","Got some information you might be interested in."], ## Story teller as in an NPC that provides more background detail about the world
            "vendor":["Buying or browsing?","Anything catch your interest?","Need something?","Need anything?"],
            "service":["Need a hand?","Need something?","Need something done?","Need something?","Need anything?"],
            "quest giver":["I need a hand with something.","Could you help with something?","Got something I need a hand with."],
            "enemy":["You shouldn't be here.", "You'll regret coming here.","Leave, I don't wish to speak to you"],
            "villain":["Have you come to stop me?","We meet again.","Ah, my least favorite person."]
        } ## put stuff in here later. Maybe remove some
        self.greeting = greeting_dict[genre][randint(0,len(greeting_dict[genre])-1)] ## "The greeting is a randomly chosen greeting from the greeting dictionary in respect to it's genre."
        if type is not None:
            if type == "enemy" or type == "villain":
                self.greeting = inquiry_dict[type][randint(0,len(inquiry_dict[type])-1)]
            elif len(self.greeting) == 0:
                self.greeting += inquiry_dict[type][randint(0,len(inquiry_dict[type])-1)]
            else:
                self.greeting += ", "+inquiry_dict[type][randint(0,len(inquiry_dict[type])-1)]


if __name__ == "__main__":  ## That is to say, if this file was opened and not imported
    if len(sys.argv) >= 2:
       inFile = open(sys.argv[1], "r")     ## First argument of command line is input file
        ##note: Input file should be formatted with each line as a seperate NPC
        ##      Each section should end with a semicolon
        ##  e.g "<World Prompt>;<NPC Type>;<NPC Traits>;<State>;<NPC Goal/motivations>;<name>;<genre>"
        ##      If no input is wanted, just leave that space empty but keep the semicolon.
        ##      NPC name is optional. Genre is optional but defaults to real world setting. 
    else:
        inFile =open("<inputfile>.txt","r")
        outFileName = "<Output File Name>"
    
    if len(sys.argv) >= 3:
       outFileName = sys.argv[2]    ## Second argument of command line is output file
       runNum = 0
    else:
        outFile = None
    for line in inFile:
        npcParser = line.strip().split(";")
        print(npcParser)
        for i in range(len(npcParser)):
            if len(npcParser[i]) == 0:
                npcParser[i] = None ## Replace all empty strings with None
        for temp in range(11):
            for model in ['text-davinci-002','text-curie-001',"text-babbage-001"]: 
                ## Run w/ all promptaids
                outFile = open("out\\"+outFileName+"_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_FullPrompt.txt","a")           ## Second argument of command line is output file
                evalFile = open("out\\"+outFileName+"_Eval_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_FullPrompt.txt","a")     ## Second argument of command line is output file
                #outFile = open("out/"+outFileName+"_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_FullPrompt.txt","a")          ##Linux file directory version
                #evalFile = open("out/"+outFileName+"_Eval_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_FullPrompt.txt","a")    ##Linux file directory version 
                npcHeader = generateNPCHeader(npcParser[0],npcParser[1],npcParser[2],npcParser[3],npcParser[4],npcParser[5],npcParser[6])
                pHeader = generatePlayerHeader(npcParser[0],npcParser[1],npcParser[2],npcParser[3],npcParser[4],npcParser[5])
                dialogue = autochat(npcHeader[0], pHeader, npcHeader[1], npcParser[5],file=outFile,temp=temp/10,model=model)
                selfEval(dialogue,evalFile,npcParser[1],npcParser[6])
                outFile.close()
                evalFile.close()
                ## Run w/ barebone promptaids (genre, NPC Type only)
                outFile = open("out\\"+outFileName+"_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_MinPrompt.txt","a")           ## Second argument of command line is output file
                evalFile = open("out\\"+outFileName+"_Eval_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_MinPrompt.txt","a")     ## Second argument of command line is output file
                #outFile = open("out/"+outFileName+"_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_MinPrompt.txt","a")          ##Linux file directory version
                #evalFile = open("out/"+outFileName+"_Eval_"+str(runNum)+"-"+str(temp/10)+"_temp_"+model[5:-4]+"_MinPrompt.txt","a")    ##Linux file directory version
                npcHeader = generateNPCHeader(None,npcParser[1],None,None,None,npcParser[5],npcParser[6])
                pHeader = generatePlayerHeader(None,npcParser[1],None,None,None,npcParser[5])
                dialogue = autochat(npcHeader[0], pHeader, npcHeader[1], npcParser[5],file=outFile,temp=temp/10,model=model)
                selfEval(dialogue,evalFile,npcParser[1],npcParser[6])
                outFile.close()
                evalFile.close()
        runNum += 1

    outFile.close()
