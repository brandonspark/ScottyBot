# Work with Python 3.6
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

fall = cmu_course_api.get_course_data('F')
spring = cmu_course_api.get_course_data('S')

walkTime = 20.0
treatTime = 5.0

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

table = pd.read_csv('table.csv')
table = np.array(table)[:, :13]
table = np.array([row for row in table if row[1] != 'Summer' and row[0] > 2013])

if os.path.isfile('scottyData.txt'):
	scottyData = json.load(open('scottyData.txt'))
else:
	scottyData = {}

TOKEN = 'NTk4NzI2MTU4MzE3NzgxMDIx.XSbKLQ.TNRQf1L2UyfM0oqm8uYCuJaC1Mk'

client = commands.Bot(command_prefix=';')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if (("good bot" in message.content.lower()) or ("good boy" in message.content.lower()) or 
    	("good boye" in message.content.lower()) or ("good dog" in message.content.lower())
    	or ('best boy' in message.content.lower()) or ('good boi' in message.content.lower())) and (client.user in message.mentions):
    	if message.author.id in scottyData:
    		scottyData[message.author.id]['love'] += 0.05
    	await message.channel.send(scottyGoodBoy[random.randint(0, len(scottyGoodBoy) - 1)])
    await client.process_commands(message)

def checkExists(author):
	userID = author.id
	if userID not in scottyData:
		name = author.name
		nick = author.nick
		if nick == None:
			nick = name
		scottyData[userID] = dict(name=name, nick=nick, walkStatus=False, walkStart=None, totalTime=0.0, totalWalks=0, love=0, treatStart=None, treatsGiven=0,
			numTreats=1, treatTime=None)
		return False
	return True

@client.command(pass_context=True)
async def walk(ctx):
	uniqueID = ctx.author.id
	if not checkExists(ctx.author):
		scottyData[uniqueID]['walkStatus'] = True
		scottyData[uniqueID]['walkStart'] = time.time()
		await ctx.channel.send(scottyWalks[random.randint(0, len(scottyWalks) - 1)])
		await ctx.channel.send('{0.author.mention} (You head out to take ScottyBot on a walk. He seems particularly {1} today. Time until finished: **{2}**)'.format(
			ctx, scottyMoods[random.randint(0, len(scottyMoods) - 1)], '00:{0:02d}:00'.format(int(walkTime))))
	else:
		if not scottyData[uniqueID]['walkStatus']:
			await ctx.channel.send(scottyWalks[random.randint(0, len(scottyWalks) - 1)])
			await ctx.channel.send('{0.author.mention} (You head out to take ScottyBot on a walk. He seems particularly {1} today. Time until finished: **{2}**)'.format(
				ctx, scottyMoods[random.randint(0, len(scottyMoods) - 1)], '00:{0:02d}:00'.format(int(walkTime))))
			scottyData[uniqueID]['walkStatus'] = True
			scottyData[uniqueID]['walkStart'] = time.time()
			return
		else:
			timeDiff = time.time() - scottyData[uniqueID]['walkStart']
			numSecs = timeDiff % 60
			numMins = timeDiff // 60
			if numMins >= walkTime:
				ctx.channel.send('{0.author.mention} (You finish taking ScottyBot on a walk. He\'s very happy!)'.format(ctx))
				scottyData[uniqueID]['totalWalks'] += 1
				scottyData[uniqueID]['walkStatus'] = False
				scottyData[uniqueID]['totalTime'] += walkTime * 60
				scottyData[uniqueID]['love'] += 4
				return
			else:
				curMins = walkTime - numMins
				curSecs = 60 - numSecs
				await ctx.channel.send(scottyWalking[random.randint(0, len(scottyWalking) - 1)])
				await ctx.channel.send('{0.author.mention} (You are currently taking ScottyBot out on a walk. Time until finished: {1})'.format(ctx, '**00:{0:02d}:{1:02d}**'.format(int(curMins) - 1, int(curSecs))))

@client.command(pass_context=True)
async def treat(ctx):
	uniqueID = ctx.author.id
	scotty = scottyData[uniqueID]
	if not checkExists(ctx.author):
		scotty['treatStart'] = time.time()
		scotty['love'] += 1.2
		scotty['treatsGiven'] += 1
		scotty['numTreats'] -= 1
		ctx.channel.send(scottyTreats[random.randint(0, len(scottyTreats) - 1)])
		ctx.channel.send('{0.author.mention} (You unwrap the Carnegie Mellon™ brand Tartan Treat™, ScottyBot\'s favorite snack. You have {1}/3 treats remaining. Refreshes in: **00:{2:02d}:00**)'.format(ctx, 
			scotty['numTreats'], int(treatTime)))
	else:
		if scotty['treatStart'] != None:
			timeDiff = time.time() - scotty['treatStart']
			numSecs = timeDiff % 60
			numMins = timeDiff // 60
			if numMins >= treatTime:
				scotty['treatStart'] = time.time()
				scotty['love'] += 1.2
				scotty['treatsGiven'] += 1
				ctx.channel.send(scottyTreats[random.randint(0, len(scottyTreats) - 1)])
				ctx.channel.send('{0.author.mention} (You unwrap the Carnegie Mellon™ brand Tartan Treat™, ScottyBot\'s favorite snack. Refreshes in: **00:{1:02d}:00**)'.format(ctx, int(treatTime)))
			else:
				curMins = treatTime - numMins
				curSecs = 60 - numSecs
				await ctx.channel.send('{0.author.mention} (You don\'t have any treats left! Refreshes in: **00:{1:02d}:{2:02d}**)'.format(ctx, int(curMins - 1), int(curSecs)))
				return
		else:
			scotty['treatStart'] = time.time()
			scotty['love'] += 1.2
			scotty['treatsGiven'] += 1
			ctx.channel.send(scottyTreats[random.randint(0, len(scottyTreats) - 1)])
			ctx.channel.send('{0.author.mention} (You unwrap the Carnegie Mellon™ brand Tartan Treat™, ScottyBot\'s favorite snack. Refreshes in: **00:{1:02d}:00**)'.format(ctx, int(treatTime)))

@client.command(pass_context=True)
async def pet(ctx):
	if ctx.author.id in scottyData:
		scottyData[ctx.author.id]['love'] += 0.1
	await ctx.channel.send(scottyPets[random.randint(0, len(scottyPets) - 1)])

@client.command(pass_context=True)
async def status(ctx):
	uniqueID = ctx.author.id
	if ctx.author.id in scottyData:
		string = 'Walk Status: **{}**\nTotal Time Walked: **{}**\nTotal Walks Taken: **{}**\nTreats Given: **{}**'.format(
			scottyData[uniqueID]['walkStatus'], str(datetime.timedelta(seconds=int(scottyData[uniqueID]['totalTime']))), scottyData[uniqueID]['totalWalks'],
			scottyData[uniqueID]['treatsGiven'])
		embed = discord.Embed(title="{}'s ScottyStatus'}".format(scottyData[uniqueID]['nick']), colour=discord.Colour(0xA6192E), description=string)
		await ctx.channel.send(embed=embed)
	else:
		await ctx.channel.send('User not recognized.')

@client.command(pass_context=True)
async def love(ctx):
	uniqueID = ctx.author.id
	checkExists(ctx.author)
	string = '{0.author.mention} '.format(ctx)
	num = (scottyData[uniqueID]['love'] // 12) + 1
	string += (':heart:' * int(num))
	await ctx.channel.send(string)

def takeTime(thing):
	return thing[1]

@client.command(pass_context=True)
async def leaderboard(ctx, arg):
	if arg == 'walk':
		walkList = [(scottyData[key]['nick'], scottyData[key]['totalTime'], key) for key in scottyData.keys()]
		walkList = sorted(walkList, key=takeTime, reverse=True)
		docstring = ''
		for i, thing in enumerate(walkList[:10]):
			docstring += '**{}.** **{}** - **{}** Walks, **{}** Time Walked\n'.format(i + 1, thing[0], scottyData[thing[2]]['totalWalks'], str(datetime.timedelta(seconds=int(scottyData[thing[2]]['totalTime']))))
		embed = discord.Embed(title="Leaderboard for ScottyBot Walks", colour=discord.Colour(0xA6192E), description=docstring)
		await ctx.channel.send(embed=embed)

			
	elif arg == 'treat':
		treatList = [(scottyData[key]['nick'], scottyData[key]['treatsGiven']) for key in scottyData.keys()]
		treatList = sorted(treatList, key=takeTime, reverse=True)
		docstring = ''
		for i, thing in enumerate(treatList[:10]):
			docstring += '**{}.** **{}** - **{}** Treats\n'.format(i + 1, thing[0], thing[1])
		embed = discord.Embed(title="Leaderboard for ScottyBot Treats", colour=discord.Colour(0xA6192E), description=docstring)
		await ctx.channel.send(embed=embed)
	else:
		await ctx.channel.send('Argument not recognized. Try \";leaderboard walk\" or \";leaderboard treat\" instead.')

			
@client.command(pass_context=True)
async def shutdown(ctx):
	if ctx.author.id != 198654438972325888:
		await ctx.channel.send('(Insufficient permissions. Nice try, though.)')
	else:
		for key in scottyData.keys():
			if scottyData[key]['walkStatus']:
				scottyData[key]['totalWalks'] += 1
				scottyData[key]['walkStatus'] = False
				scottyData[key]['totalTime'] += walkTime * 60
				scottyData[key]['love'] += 4
		outfile = open('scottyData.txt', 'w')
		json.dump(scottyData, outfile)
		await ctx.channel.send('ScottyBot shutting down. Be back soon!')
	return 

def isValidCourse(msg):
	if len(msg) == 5 and msg.isdigit():
		return True
	if len(msg) == 6 and (msg[:2] + msg[3:]).isdigit() and msg[2] == '-':
		return True
	return False

def isValidArgs(ctx, args):
	lastArg = 0
	for i, arg in enumerate(args):
		if i == 0 and (not isValidCourse(arg)):
			return False, None, None, 1
		if isValidCourse(arg):
			lastArg = i
	if len(args) == lastArg + 3 and args[lastArg + 1].isdigit() and args[lastArg+2].count('.') <= 1 and args[lastArg+2].replace('.', '', 1).isdigit():
		if not args[-1].isdigit():
			if float(args[-1]) >= 0 and float(args[-1]) <= 1:
				return True, True, 2, 0
			else:
				return False, False, 2, 2
		else:
			return True, False, 2, 0
	elif len(args) == lastArg + 2 and args[lastArg + 1].isdigit():
		return True, None, 1, 0
	elif len(args) == lastArg + 1:
		return True, None, 0, 0
	return False, None, None, 2


def getString(mold, row):
	indices = [0, 1, 6, 10, 9, 11, 12]
	string = mold.format(row[indices[0]], row[indices[1]], row[indices[2]], row[indices[3]], row[indices[4]], row[indices[5]], row[indices[6]])
	return string

def toDigitString(ID):
	if ID.isdigit():
		if ID[0] == '0':
			return ID[1:]
		return ID
	else:
		return ID[:2] + ID[3:]

def flatten(l): 
	return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]

@client.command(pass_context=True)
async def fce(ctx, *args):
	#check the args are valid
	indices = [0, 1, 4, 7, 6, 10, 9, 11, 12]
	truth, floatVal, condition, msg = isValidArgs(ctx, args)
	if msg == 1:
		await ctx.channel.send('Invalid arguments - please specify the course ID (e.g. \";fce 21127 2\")')
	elif msg == 2:
		await ctx.channel.send('Invalid arguments - please follow the `;fce [courseIDs...] [opt: # sem] [opt: # / prop. responses]` format.')
	if not truth:
		return

	#set the courseID 
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
		rows = []
		temp = []
		for row in table:
			if row[0] != year or row[1] != semester:
				if len(temp) != 0:
					rows.append(temp)
				temp = []
				year = row[0]
				semester = row[1]
			if row[4] == str(courseID):
				temp.append(row)
		allRows.append(rows)

	#restricts to the rows requested
	if condition == 2 and floatVal:
		newRows = []
		for rows in allRows:
			newRow = [row for i, bundle in enumerate(rows) for row in bundle if i < int(args[-2]) and row[11] >= (100 * float(args[-1]))]
			newRows.append(newRow)
	elif condition == 2 and not floatVal:
		newRows = []
		for rows in allRows:
			newRow = [row for i, bundle in enumerate(rows) for row in bundle if i < int(args[-2]) and row[10] >= int(args[-1])]
			newRows.append(newRow)
	elif condition == 1:
		newRows = []
		for rows in allRows:
			newRow = [row for i, bundle in enumerate(rows) for row in bundle if i < int(args[-1])]
			newRows.append(newRow)
	else:
		newRows = []
		for rows in allRows:
			newRow = [row for i, bundle in enumerate(rows) for row in bundle if i < 2]
			newRows.append(newRow)

	#adds up the FCE's and assembles the docstring
	if lastCourse == 0:
		rows = newRows[0]
		totalFCE = 0
		count = 0
		mold = mold = '{0:^%d} | {1:^%d} | {2:^%d} | {3:^%d} | {4:^%d} | {5:^%d} | {6:^%d}\n' % (4, 8, 22, 7, 11, 9, 9)
		docstrings = [mold.format('Year', 'Semester', 'Instructor', '# resp.', 'Total resp.', '% resp.', 'FCE hours')]
		for row in rows:
			if not math.isnan(row[12]):
				docstrings.append(getString(mold, row))
				totalFCE += float(row[12])
				count += 1
		
		#separates the docstrings into messages
		endstrings = []
		temp = ''
		for docstring in docstrings:
			if len(temp) + len(docstring) <= 1992:
				temp += docstring
			else:
				endstrings.append(temp)
				temp = docstring
		endstrings.append(temp)
		#if there are no valid rows
		if count == 0:
			await ctx.channel.send('Course not found.')
			return
		total = round(totalFCE / count, 2)

	else:
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

	#print to discord
	ess = ''
	if len(args) == 1 or (len(args) == 2 and args[1] != '1') or args[-2] != '1':
		ess = 's'
	if lastCourse == 0:
		rows = newRows[0]
		if condition == 2:
			currentString = 'FCE average for course {} {} within **{}** semester{}'.format(rows[0][4], rows[0][7], args[1], ess)
			end = ': __**{}**__'.format(np.around(total, 2))
			if args[-1].isdigit():
				currentString += ', filtering for greater than **{}** responses{}'.format(args[-1], end)
			else:
				currentString += ', filtering for greater than **{}%** responses{}'.format(np.around(float(args[-1]) * 100, 2), end)
			await ctx.channel.send(currentString)
		elif condition == 1:
			await ctx.channel.send('FCE average for course **{} {}** within **{}** semester{}: **{}**'.format(rows[0][4], rows[0][7], args[1], ess, total))
		else:
			await ctx.channel.send('FCE average for course **{} {}** within **2** semesters: **{}**'.format(rows[0][4], rows[0][7], total))

		for endstring in endstrings:
			await ctx.channel.send('```' + endstring + '```')
	else:
		string = 'FCE average for courses '
		l = ['**[{} {}]**, '.format(courseIDs[i], newRows[i][0][7]) for i in range(len(newRows))]
		for thing in l:
			string += thing
		l = [' **{}** +'.format(fce) for fce in totalFCEs]
		if condition == 1:
			num = args[-1]
		elif condition == 2:
			num = args[-2]
		elif condition == 0:
			num = 2
		string = string[:-2] + ' within **{}** semester{}'.format(num, ess)
		if condition == 2:
			if args[-1].isdigit():
				string += ', filtering for greater than **{}** responses'.format(args[-1])
			else:
				string += ', filtering for greater than **{}%** responses'.format(np.around(float(args[-1]) * 100, 2))
		string += ':'
		for thing in l:
			string += thing
		string = string[:-1] + '= __**{}**__'.format(np.around(sum(totalFCEs), 2))
		await ctx.channel.send(string)



@client.command(pass_context=True)
async def course(ctx, courseID):
	newFall = fall['courses']
	newSpring = spring['courses']
	if isValidCourse(courseID):
		if courseID[2] != "-":
			courseID = courseID[:2] + '-' + courseID[2:]
		
		if courseID in newFall.keys():
			output = '**{}**\n**{} units**\n{}\n**Prerequisites:** {}\n'.format(newFall[courseID]['department'], str(newFall[courseID]['units']), newFall[courseID]['desc'], newFall[courseID]['prereqs'])
			if newFall[courseID]['coreqs'] != None:
				output += '**Corequisites:** {}\n'.format(newFall[courseID]['coreqs'])
			output += '**Instructors:**\n'
			for lecture in newFall[courseID]['lectures']:
				output += '['
				for instructor in lecture['instructors']:
					output += '({}) '.format(instructor)
				output = output[:-1] + '] '
			output += '**(Fall)**\n'
			if courseID in newSpring.keys():
				for lecture in newSpring[courseID]['lectures']:
					output += '['
					for instructor in lecture['instructors']:
						output += '({}) '.format(instructor)
					output = output[:-1] + '] '
				output += '**(Spring)**\n'
			output += '**Semesters:** {}'.format(fall['semester'])
			if courseID in newSpring.keys():
				output += ', {}'.format(spring['semester'])
			embed = discord.Embed(title="__**{}**__".format(newFall[courseID]['name']), colour=discord.Colour(0xA6192E), description=output)
			await ctx.channel.send(embed=embed)
			return

		if courseID in newSpring.keys():
			output = '**{}**\n**{} units**\n{}\n**Prerequisites:** {}\n'.format(newSpring[courseID]['department'], str(newSpring[courseID]['units']), newSpring[courseID]['desc'], newSpring[courseID]['prereqs'])
			if newSpring[courseID]['coreqs'] != None:
				output += '**Corequisites:** {}\n'.format(newSpring[courseID]['coreqs'])
			output += '**Instructors:**\n '
			for lecture in newSpring[courseID]['lectures']:
				output += '['
				for instructor in lecture['instructors']:
					output += '({}) '.format(instructor)
				output = output[:-1] + '] '
			output += '**(Spring)**\n'
			output += '**Semesters:** {}'.format(spring['semester'])
			embed = discord.Embed(title="__**{}**__".format(newSpring[courseID]['name']), colour=discord.Colour(0xA6192E), description=output)
			await ctx.channel.send(embed=embed)
			return

		else:
			await ctx.channel.send('Course not found.')
	else:
		ctx.channel.send('Invalid arguments - please specify the course ID (e.g. \".course 21127)\"')

client.run(TOKEN)