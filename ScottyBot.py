import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import math
import cmu_course_api
import random
import json 
import os
import time
import datetime
import redis

# -------------
# PREPROCESSING
# -------------

fall = cmu_course_api.get_course_data('F')
spring = cmu_course_api.get_course_data('S')

walkTime = XXX
treatTime = XXX

global messageCount
messageCount = 0

# bunch of fucking scotty messages
scottyWalks = ['*ears perk up as he hears the word \"walk\"*', '*scampers over to you eagerly, leash in his mouth*', '*scampers around the room several times, excitedly, before coming back to you*',
'*yips happily, already heading for the door*', '*runs around your feet several times, clearly ecstatic*', '*instantly perks up at the prospect of a walk*', 'bark BARK bark!!!', 
'*butts your legs several times, eager for walkies*', ':dog::heart::park:', '*tail begins to wag at maximum velocity*']

scottyGoodBoy = ['*wags tail excitedly*', '*barks in excitement*', '*sticks tongue out and pants at you*', '*barks with joy*', 
'*happily runs around in little circles*', '*ambles around your feet*', '*jumps up and down eagerly*', 
'*fetches several hundred thousand dollars of student debt for you*', '*licks your hand looking for snacks*', '*yips playfully*', 'woof WOOF!', '<3', '<3', ':dog:', 
'*snuggles up against your legs*', '*headbutts you affectionately*', '*yips happily*']

scottyWalking = ['*looks up quizzically at you*', '*nips at some leaves floating through the air*', '*runs ahead, impatiently tugging on your leash*',
'*barks a greeting to another dog being walked*', '*ambles around in a circle, causing the leash to wrap around you*', '*trots at a steady pace, looking back at you every couple of seconds*',
'*cocks his head at you, looking right into your eyes*', '*fetches a pine cone for you, looking proud*', '*chases after a nearby squirrel, barking joyfully*', '*pauses to sniff some funny-smelling thing on the ground*',
'bark bark bark!', '*barks a greeting to some nearby park-goers*', '*scampers ahead, tongue lolling out lazily*']

scottyTreats = ['*ears perk up in anticipation*', '*drools slightly, waiting for his tasty treat*', '*pads around in little circles before looking at you expectantly*',
'woof woof WOOF!', '*jumps up and down happily*', '*scampers over immediately for the tasty treat*', '*licks your hand affectionately*']

scottyPets = ['*rolls over to expose his tummy as you give him a belly rub*', '*tongue lolls out as you scritch him behind the ears*', ':dog::smile:', '*tail wags vigorously as you pet him on the side*',
'*whines happily, wiggling around on his side*', '*makes a low, happy sound from his throat*', '<3', '*nuzzles against your hand as you pet his head*', '*closes eyes contentedly, enjoying your hand on his soft fur*']

scottyMoods = ['jovial', 'happy', 'playful', 'affectionate', 'energetic', 'mischievous', 'adventurous', 'eager', 'rowdy', 'cheerful']

# preprocess the fce data
table = pd.read_csv('table.csv')
table = np.array(table)[:, :13]
table = np.array([row for row in table if row[1] != 'Summer' and row[0] > 2013])

# prepare the scottyData data
if os.path.isfile('scottyData.txt'):
	scottyData = json.load(open('scottyData.txt'))
else:
	scottyData = {}

# -------------------------------
# THE ACTUAL BOT - SCOTTY SECTION
# -------------------------------

TOKEN = 'NTk4NzI2MTU4MzE3NzgxMDIx.XSbKLQ.TNRQf1L2UyfM0oqm8uYCuJaC1Mk'

client = commands.Bot(command_prefix=';')

def save():
	"""
	Helper function run to save every 50 messages by writing to a JSON.
	"""
	global messageCount 
	if messageCount % 50 == 0:
		count = 0
		outfile = open('scottyData.txt', 'w')
		json.dump(scottyData, outfile)
		outfile.close()
		return
	messageCount = messageCount + 1

def randomPick(messageList):
	"""
	Helper function that returns a random string from a list of messages.
	"""
	return messageList[random.randint(0, len(messageList) - 1)]

@client.event
async def on_ready():
	"""
	Prints some stuff to the console so I know the bot's ready.
	"""
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

@client.event
async def on_message(message):
	"""
	Code to be run on *every* single message sent in a ScottyBot-inhabited channel.
	"""
	if message.author == client.user:
		return
	save()
	if (("good bot" in message.content.lower()) or ("good boy" in message.content.lower()) or 
		("good boye" in message.content.lower()) or ("good dog" in message.content.lower()) or
		('best boy' in message.content.lower()) or ('good boi' in message.content.lower())) and (client.user in message.mentions):
		if message.author.id in scottyData:
			scottyData[message.author.id]['love'] += XXX
		await message.channel.send(randomPick(scottyGoodBoy))
	await client.process_commands(message)

def checkExists(author):
	"""
	'Precondition' helper function that ensures there are no illegal accesses for unrecognized userIDs.
	"""
	userID = author.id
	if userID not in scottyData:
		name = author.name
		nick = author.nick
		if nick == None:
			nick = name
		scottyData[userID] = dict(name=name, nick=nick, walkStatus=False, walkStart=None, totalTime=0.0, totalWalks=0, love=0, 
			treatStart=time.time(), treatsGiven=0, numTreats=1)
		return False
	return True

@client.command(pass_context=True)
async def walk(ctx):
	"""
	Function that defines the ;walk command.
	"""
	uniqueID = ctx.author.id
	flag = checkExists(ctx.author)
	scotty = scottyData[uniqueID]
	if not flag: # if the person is not recognized
		scotty['walkStatus'] = True
		scotty['walkStart'] = time.time()
		await ctx.channel.send(randomPick(scottyWalks))
		await ctx.channel.send('{0.author.mention} (You head out to take ScottyBot on a walk. He seems particularly {1} today. Time until ' \
			'finished: **{2}**)'.format(ctx, scottyMoods[random.randint(0, len(scottyMoods) - 1)], '00:{0:02d}:00'.format(int(walkTime))))
	else: # if the person is recognized
		if not scotty['walkStatus']: # and not on a walk currently
			scotty['walkStatus'] = True
			scotty['walkStart'] = time.time()
			await ctx.channel.send(randomPick(scottyWalks))
			await ctx.channel.send('{0.author.mention} (You head out to take ScottyBot on a walk. He seems particularly {1} today. ' \
				'Time until finished: **{2}**)'.format(ctx, randomPick(scottyMoods), '00:{0:02d}:00'.format(int(walkTime))))
		else: # and on a walk currently
			timeDiff = time.time() - scotty['walkStart']
			numSecs = timeDiff % 60
			numMins = timeDiff // 60
			if numMins >= walkTime: # and the walk is over
				scotty['totalWalks'] += 1
				scotty['walkStatus'] = False
				scotty['totalTime'] += walkTime * 60
				scotty['love'] += XXX
				await ctx.channel.send('{0.author.mention} (You finish taking ScottyBot on a walk. He\'s very happy!)'.format(ctx))
			else: # and the walk is not over
				curMins = walkTime - numMins
				curSecs = 60 - numSecs
				await ctx.channel.send(randomPick(scottyWalking))
				await ctx.channel.send('{0.author.mention} (You are currently taking ScottyBot out on a walk. Time until finished: {1})'.format(ctx,
				'**00:{0:02d}:{1:02d}**'.format(int(curMins) - 1, int(curSecs))))

def updateTreats(scotty):
	"""
	Helper function that refreshes a person's treat store.
	"""
	timeDiff = time.time() - scotty['treatStart']
	numSecs = timeDiff % 60
	numMins = timeDiff // 60
	while numMins >= treatTime: #refill treats based on time since last one
		if scotty['numTreats'] < 3:
			numMins -= treatTime
			scotty['numTreats'] += 1
			scotty['treatStart'] += treatTime * 60
		else:
			break
	if scotty['numTreats'] == 3: #if we're in excess of 3 treats, move the refresh time up
		scotty['treatStart'] == time.time()

@client.command(pass_context=True)
async def treat(ctx):
	"""
	Function that defines the ;treat command.
	"""
	uniqueID = ctx.author.id
	checkExists(ctx.author)
	scotty = scottyData[uniqueID]
	updateTreats(scotty)
	timeDiff = time.time() - scotty['treatStart']
	numSecs = timeDiff % 60
	numMins = timeDiff // 60
	if scotty['numTreats'] >= 1: # if we have treats left 
		if scotty['numTreats'] == 3:
			scotty['treatStart'] = time.time()
		scotty['love'] += XXX
		scotty['treatsGiven'] += 1
		scotty['numTreats'] -= 1
		await ctx.channel.send(scottyTreats[random.randint(0, len(scottyTreats) - 1)])
		await ctx.channel.send('{0.author.mention} (You unwrap the Carnegie Mellon™ brand Tartan Treat™, ScottyBot\'s favorite snack. You have **{1}/3** treats remaining. Refreshes in: **00:{1:02d}:00**)'.format(
			ctx, scotty['numTreats'], int(treatTime)))
	else: # if we don't have treats left
		curMins = treatTime - numMins
		curSecs = 60 - numSecs
		await ctx.channel.send('{0.author.mention} (You don\'t have any treats left! Refreshes in: **00:{1:02d}:{2:02d}**)'.format(ctx, int(curMins - 1), int(curSecs)))

@client.command(pass_context=True)
async def pet(ctx):
	"""
	Function that defines the ;pet command.
	"""
	if ctx.author.id in scottyData:
		scottyData[ctx.author.id]['love'] += XXX
	await ctx.channel.send(randomPick(scottyPets))

@client.command(pass_context=True)
async def status(ctx):
	"""
	Function that defines the ;status command.
	"""
	uniqueID = ctx.author.id
	checkExists(ctx.author)
	scotty = scottyData[uniqueID]
	updateTreats(scotty)
	if scotty['nick'] == None: # updates name on the leaderboard if it is currently set to None
		scotty['nick'] = scotty['name']
	timeUntilWalkOver = ''
	newStatus = scotty['walkStatus']
	if scotty['walkStatus']: # if currently on a walk, add time until walk over to final string
		timeDiff = time.time() - scotty['walkStart']
		curMins = walkTime - timeDiff // 60
		curSecs = 60 - timeDiff % 60
		timeUntilWalkOver = 'Time until Walk Over: **00:{0:02d}:{1:02d}**\n'.format(int(curMins) - 1, int(curSecs))
		if time.time() - scotty['walkStart'] >= walkTime * 60:
			newStatus = 'Done!'
			timeUntilWalkOver = ''
	
	string = """Walk Status: **{}**
	Total Time Walked: **{}**
	Total Walks Taken: **{}**\n""".format(newStatus, str(datetime.timedelta(seconds=int(scotty['totalTime']))), scotty['totalWalks'])
	
	timeDiff = time.time() - scotty['treatStart']
	curMins = treatTime - timeDiff // 60
	curSecs = 60 - timeDiff % 60

	string2 = """Number of Treats: **{0}/3**
	Treats Given: **{1}**
	Time until Next Treat: """.format(scotty['numTreats'], scotty['treatsGiven'])
	
	final = '**00\:{0:02d}\:{1:02d}**'.format(int(curMins) - 1, int(curSecs))
	
	if scotty['numTreats'] == 3:
		final = "**Full**"
	embed = discord.Embed(title="{}'s ScottyStatus".format(scotty['nick']), colour=discord.Colour(0xA6192E), 
		description=string + timeUntilWalkOver + string2 + final)
	await ctx.channel.send(embed=embed)

@client.command(pass_context=True)
async def love(ctx):
	"""
	Function that defines the ;love command.
	"""
	uniqueID = ctx.author.id
	checkExists(ctx.author)
	string = '{0.author.mention} '.format(ctx)
	num = (scottyData[uniqueID]['love'] // XXX) + 1
	string += (':heart:' * int(num))
	await ctx.channel.send(string)

def takeSecond(thing):
	"""
	Helper function for use in sorted().
	"""
	return thing[1]

@client.command(pass_context=True)
async def leaderboard(ctx, arg):
	"""
	Function that defines the ;leaderboard command.
	"""
	if arg == 'walk':
		walkList = [(scottyData[key]['nick'], scottyData[key]['totalTime'], key) for key in scottyData.keys()]
		walkList = sorted(walkList, key=takeSecond, reverse=True)
		docstring = ''
		for i, info in enumerate(walkList[:10]):
			docstring += '**{}.** **{}** - **{}** Walks, **{}** Time Walked\n'.format(i + 1, info[0], scottyData[info[2]]['totalWalks'], 
				str(datetime.timedelta(seconds=int(scottyData[info[2]]['totalTime']))))
		embed = discord.Embed(title="Leaderboard for ScottyBot Walks", colour=discord.Colour(0xA6192E), description=docstring)
		await ctx.channel.send(embed=embed)
			
	elif arg == 'treat':
		treatList = [(scottyData[key]['nick'], scottyData[key]['treatsGiven']) for key in scottyData.keys()]
		treatList = sorted(treatList, key=takeSecond, reverse=True)
		docstring = ''
		for i, info in enumerate(treatList[:10]):
			docstring += '**{}.** **{}** - **{}** Treats\n'.format(i + 1, info[0], info[1])
		embed = discord.Embed(title="Leaderboard for ScottyBot Treats", colour=discord.Colour(0xA6192E), description=docstring)
		await ctx.channel.send(embed=embed)
	else:
		await ctx.channel.send('Argument not recognized. Try \";leaderboard walk\" or \";leaderboard treat\" instead.')

			
@client.command(pass_context=True)
async def shutdown(ctx):
	"""
	Function that defines the ;shutdown command, which does not actually shut down the bot.
	"""
	if ctx.author.id != 198654438972325888: # ensures dumbasses dont fuck with my bot
		await ctx.channel.send('(Insufficient permissions. Nice try, though.)')
	else:
		for key in scottyData.keys():
			if scottyData[key]['walkStatus']:
				scottyData[key]['totalWalks'] += 1
				scottyData[key]['walkStatus'] = False
				scottyData[key]['totalTime'] += walkTime * 60
				scottyData[key]['love'] += XXX
		outfile = open('scottyData.txt', 'w')
		json.dump(scottyData, outfile)
		await ctx.channel.send('ScottyBot shutting down. Be back soon!')
	return 

# ---------------------------------
# THE ACTUAL BOT - CMU DATA SECTION
# ---------------------------------

def isValidCourse(msg): 
	"""
	Helper function that identifies if a string is a valid course or not.
	"""
	if len(msg) == 5 and msg.isdigit():
		return True
	if len(msg) == 6 and (msg[:2] + msg[3:]).isdigit() and msg[2] == '-':
		return True
	return False

def isValidArgs(ctx, args):
	"""
	Helper function that classifies what type of parameters were passed in.
	"""
	lastArg = 0
	for i, arg in enumerate(args):
		if i == 0 and (not isValidCourse(arg)):
			return False, None, None, 1 # not valid args, display message 1 (courseID not given)
		if isValidCourse(arg): # moves up the index of the last valid course argument
			lastArg = i
	if len(args) == lastArg + 3 and args[lastArg + 1].isdigit() and args[lastArg+2].count('.') <= 1 and args[lastArg+2].replace('.', '', 1).isdigit():
		if not args[-1].isdigit():
			if float(args[-1]) >= 0 and float(args[-1]) <= 1:
				return True, True, 2, 0 # valid args, passed a float filter arg, passed both optional parameters, no early return
			else:
				return False, None, None, 2 # not valid args, display error message 2 (optional args incorrect) 
		else:
			return True, False, 2, 0 # valid args, passed an integer filter arg, passed both optional parameters, no early return
	elif len(args) == lastArg + 2 and args[lastArg + 1].isdigit():
		return True, None, 1, 0 # valid args, passed num semesters optional parameter, no early return
	elif len(args) == lastArg + 1:
		return True, None, 0, 0 # valid args, passed no optional parameters, no early return
	return False, None, None, 2 # invalid args, display error message 2 (args incorrect)


def getString(mold, row):
	"""
	Takes particular columns from an FCE data frame row and assembles them into a string.
	"""
	indices = [0, 1, 6, 10, 9, 11, 12]
	rowIndices = [row[index] for index in indices]
	string = mold.format(*rowIndices)
	return string

def toDigitString(ID):
	"""
	Turns a course ID argument into a compatible form for the FCE data frame.
	"""
	if ID.isdigit():
		if ID[0] == '0':
			return ID[1:]
		return ID
	else:
		if ID[0] == '0':
			return ID[:1] + ID[3:]
		return ID[:2] + ID[3:]

@client.command(pass_context=True)
async def fce(ctx, *args):
	"""
	Function that defines the ;fce command. Also moonlights as a giant pain in the ass.
	"""
	#check the args are valid
	indices = [0, 1, 4, 7, 6, 10, 9, 11, 12]
	valid, isFloat, condition, msg = isValidArgs(ctx, args) # sets some indicator variables that will alter the flow of the function
	if msg == 1:
		await ctx.channel.send('Invalid arguments - please specify the course ID (e.g. \";fce 21127 2\")')
	elif msg == 2:
		await ctx.channel.send('Invalid arguments - please follow the `;fce [courseIDs...] [opt: # sem] [opt: # / prop. responses]` format.')
	if not valid:
		return

	#set the courseID(s)
	lastCourse = 0
	for i, arg in enumerate(args):
		if isValidCourse(arg):
			lastCourse = i

	courseIDs = [toDigitString(args[i]) for i in range(lastCourse + 1)]

	#segments the data by year, semester
	allRows = []
	for courseID in courseIDs:
		year = 'dummy_string.jpg omegalul'
		semester = 'why are you reading this'
		courseList = []
		sameSemList = []
		for row in table:
			if row[0] != year or row[1] != semester: # if this row is not the same course/semester as the rest of the section
				if len(sameSemList) != 0:
					courseList.append(sameSemList)
				sameSemList = []
				year = row[0]
				semester = row[1]
			if row[4] == str(courseID):
				sameSemList.append(row)
		allRows.append(courseList)

	#restricts to the rows requested
	if condition == 2 and isFloat:
		newRows = [[row for i, sameSemList in enumerate(courseList) for row in sameSemList if i < int(args[-2]) and row[11] >= (100 * float(args[-1]))] 
		for courseList in allRows]
	elif condition == 2 and not isFloat:
		newRows = [[row for i, sameSemList in enumerate(courseList) for row in sameSemList if i < int(args[-2]) and row[10] >= int(args[-1])]
		for courseList in allRows]
	else:
		numSemesters = 2
		if condition == 1:
			numSemesters = int(args[-1])
		newRows = [[row for i, sameSemList in enumerate(courseList) for row in sameSemList if i < numSemesters]
		for courseList in allRows]

	# adds up the FCE's
	totalFCEs = []
	for i, rows in enumerate(newRows):
		totalFCE = 0
		count = 0
		for row in rows:
			if not math.isnan(row[12]):
				totalFCE += float(row[12])
				count += 1
		if count == 0:
			await ctx.channel.send('Course not found: {}'.format(courseIDs[i]))
			return
		totalFCEs.append(np.around(totalFCE / count, 2))

	# if only one course was requested, assemble the FCE data string
	if lastCourse == 0: 
		mold = '{0:^%d} | {1:^%d} | {2:^%d} | {3:^%d} | {4:^%d} | {5:^%d} | {6:^%d}\n' % (4, 8, 22, 7, 11, 9, 9)
		docstrings = [mold.format('Year', 'Semester', 'Instructor', '# resp.', 'Total resp.', '% resp.', 'FCE hours')]

		for row in newRows[0]:
			if not math.isnan(row[12]):
				docstrings.append(getString(mold, row))
		
		# separates the docstrings into messages
		endstrings = []
		temp = ''
		for docstring in docstrings:
			if len(temp) + len(docstring) <= 1992:
				temp += docstring
			else:
				endstrings.append(temp)
				temp = docstring
		endstrings.append(temp)

	# if there are plural semesters
	ess = ''
	if len(args) == 1 or (len(args) == 2 and args[1] != '1') or args[-2] != '1':
		ess = 's'
	
	# set up the optional string for if filtering was requested
	extraString = ''
	if condition == 2:
		filterNum = '{}'.format(args[-1])
		if isFloat:
			filterNum = '{}%'.format(args[-1])
		extraString = ', filtering for greater than {} responses'.format(filterNum)

	# set up the string containing the course names and ids
	courseStrings = ''
	listOfCourses = ['**[{} {}]**, '.format(courseIDs[i], newRows[i][0][7]) for i in range(len(newRows))]
	for course in listOfCourses:
		courseStrings += course

	# if there are multiple courses, set up the addition string
	additionString = ''
	ess2 = ''
	if lastCourse != 0:
		ess2 = 's'
		fceStrings = [' **{}** +'.format(fce) for fce in totalFCEs]
		for string in fceStrings:
			additionString += string
		additionString = additionString[:-1] + '=' 
	
	# create and send the final string
	stringFinal = 'FCE average for course{} {} within **{}** semester{}{}:{} __**{}**__'.format(
		ess2, courseStrings[:-2], numSemesters, ess, extraString, additionString, np.around(sum(totalFCEs), 2))
	await ctx.channel.send(stringFinal) 

	# if only one course was requested, also send the messages of all the query data
	if lastCourse == 0:
		for endstring in endstrings:
			await ctx.channel.send('```' + endstring + '```')


def getInstructors(lectures):
	"""
	Helper function that formats the instructors of a course in a particular way.
	"""
	output = '\n'
	for lecture in lectures:
		output += '['
		for instructor in lecture['instructors']:
			output += '({}) '.format(instructor)
		output = output[:-1] + '] '
	return output

@client.command(pass_context=True)
async def course(ctx, courseID):
	"""
	Function that defines the ;course command.
	"""
	newFall = fall['courses']
	newSpring = spring['courses']
	if isValidCourse(courseID): # if the courseID is valid, then do all the work
		# remove hyphen if it exists
		if courseID[2] != "-":
			courseID = courseID[:2] + '-' + courseID[2:]

		# set flags for if the course exists in fall or spring
		inFall = courseID in newFall.keys()
		inSpring = courseID in newSpring.keys()
		
		# if it doesn't exist in either return early
		if not (inFall or inSpring):
			await ctx.channel.send('Course not found.')
			return

		# set some strings for later use
		semesters = ''
		instructorsFall = ''
		instructorsSpring = ''
		coreqs = ''

		# get the data if the course exists in spring
		if courseID in newSpring.keys(): 
			title = newSpring[courseID]['name']
			department = newSpring[courseID]['department']
			units = newSpring[courseID]['units']
			description = newSpring[courseID]['desc']
			prereqs = newSpring[courseID]['prereqs']
			if newSpring[courseID]['coreqs'] != None:
				coreqs = '\n**Corequisites**: {}'.format(newSpring[courseID]['coreqs'])
			instructorsSpring = getInstructors(newSpring[courseID]['lectures']) + ' **(Spring)**'
			semesters = spring['semester']

		# get the data if the course exists in fall
		else: 
			title = newFall[courseID]['name']
			department = newFall[courseID]['department']
			units = newFall[courseID]['units']
			description = newFall[courseID]['desc']
			prereqs = newFall[courseID]['prereqs']
			if newFall[courseID]['coreqs'] != None:
				coreqs = '\n**Corequisites**: {}'.format(newFall[courseID]['coreqs'])
			instructorsFall = getInstructors(newFall[courseID]['lectures']) + ' **(Fall)**'
			if len(semesters) == 0:
				semesters += fall['semester']
			else:
				semesters += ', {}'.format(fall['semester'])

		# put it all together with the magic of {}
		instructors = '{}{}'.format(instructorsFall, instructorsSpring)
		embed = discord.Embed(title="__**{}**__".format(title), colour=discord.Colour(0xA6192E), description=
			'**{}**\n**{} units**\n{}\n**Prerequisites:** {}{}\n**Instructors:** {}\n**Semesters:** {}'.format(
				department, units, description, prereqs, coreqs, instructors, semesters))
		await ctx.channel.send(embed=embed)
	else:
		await ctx.channel.send('Invalid arguments - please specify the course ID (e.g. \".course 21127)\"')

client.run(TOKEN)
