#!/bin/python3
import discord
from asyncio import sleep
from random import randint

TOKEN="abc" # Your bot token
CHANNEL_ID=123 # The channel id of the channel your bot will be running in (can be checked using dev mode on discord)
MAX_GUESSES=8 # The maximum number of guesses

with open('words.txt','r') as file: # You put your own words in the words.txt file
    words=file.read().splitlines()

isRecievingVotes=False
paused=False

class WordleBotClient(discord.Client):
    async def on_ready(self):
        global channel
        global votes
        global madeValidVote
        global isRecievingVotes
        global paused

        print(f"Discord.py version: {discord.__version__}\nLogged in as {self.user}")

        channel=self.get_channel(CHANNEL_ID)

        word=words[randint(0,len(words)-1)]
        wordleString=""

        while True:
            votes=[]
            madeValidVote=[]
            isRecievingVotes=True
            await channel.send("The voting has begun!\n30 seconds left...")
            await sleep(10)
            await channel.send("20 seconds left...")
            await sleep(10)
            await channel.send("10 seconds left...")
            await sleep(5)
            await channel.send("5 seconds left...")
            await sleep(5)
            await channel.send("End of the voting!")
            isRecievingVotes=False
            
            maxVoteCount=0
            winningVotes=[]
            for i in votes:
                count=votes.count(i)
                if count>maxVoteCount:
                    maxVoteCount=count
                    winningVotes=[i]
                try:
                    winningVotes.index(i)
                except ValueError:
                    if maxVoteCount==count:
                        winningVotes.append(i)

            if len(winningVotes)==0:
                await channel.send("No valid input recieved, pausing the game... Type anything to resume.\n====================")
                paused=True
                isRecievingVotes=False
                while paused:
                    await sleep(0.5)
                continue
            elif len(winningVotes)==1:
                choosenWord=winningVotes[0]
            else:
                candidatesString=""
                for i in winningVotes:
                    candidatesString+=i+", "
                await channel.send(f"There was a tie in the voting! Choosing randomly...\nCandidates:\n{candidatesString[:-2]}")
                choosenWord=winningVotes[randint(0,len(winningVotes)-1)]
            await channel.send(f"Next word: **{choosenWord}**")

            foundLetters={}
            for index,letter in enumerate(choosenWord): # If you manage to look at the code in that loop for the first time and understand it in an hour, I'll pay you...
                try:
                    if letter==word[index]: 
                        try:
                            foundLetters[letter]+=1
                        except KeyError:
                            foundLetters[letter]=1
                        try:
                            if wordleString[-1]=="*":
                                wordleString=wordleString[:-2]
                            else:
                                raise IndexError()
                        except IndexError:
                            wordleString+="**"
                        wordleString+=letter+"**"
                    else:
                        try:
                            word.index(letter)
                            try:
                                foundLetters[letter]
                            except KeyError:
                                foundLetters[letter]=0
                            if foundLetters[letter]<word.count(letter):
                                foundLetters[letter]+=1
                                try:
                                    if wordleString[-1]=="_":
                                        wordleString=wordleString[:-2]
                                    else:
                                        raise IndexError()
                                except IndexError:
                                    wordleString+="__"
                                wordleString+=letter+"__"
                            else:
                                raise ValueError()
                        except ValueError:
                            wordleString+=letter
                except IndexError:
                    break
            wordleString+="\n"
            await channel.send("~-~-~-~\n"+wordleString.upper()+"~-~-~-~")

            if choosenWord==word:
                await channel.send("Hoorrrayyy! You've managed to find the word!\nStarting a new game...")
                word=words[randint(0,len(words)-1)]
                wordleString=""
            else:
                guessesLeft=abs(wordleString.count('\n')-MAX_GUESSES)
                if guessesLeft > 0:
                    await channel.send(f"Guesses left: {guessesLeft}")
                else:
                    await channel.send(f"Oh no! You didn't manage to guess it! The word was **{word}**.\nStarting a new game...")
                    word=words[randint(0,len(words)-1)]
                    wordleString=""
            await channel.send("====================")

    async def on_message(self, message):
        global paused
        try:
            if message.channel != channel:
                return
        except NameError:
            return
        if message.author == self.user:
            return
        if not(isRecievingVotes):
            await message.delete()
            if paused:
                paused=False
            return
        try:
            madeValidVote.index(message.author)
            await message.delete()
            return
        except ValueError:
            pass
        lowercaseMessageContent=message.content.lower()
        try:
            words.index(lowercaseMessageContent)
        except ValueError:
            await message.add_reaction('❌')
            return
        await message.add_reaction('✅')
        votes.append(lowercaseMessageContent)
        madeValidVote.append(message.author)

intents = discord.Intents.default()
intents.message_content = True
WordleBotClient(intents=intents).run(TOKEN)
