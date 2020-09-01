# bot.py
import os, os, pymongo, discord, random, datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URL = os.getenv('MONGO_CLIENT_URL')

client = discord.Client()
clientDB = pymongo.MongoClient(MONGODB_URL)
db = clientDB.Yeetus
userData = db.data
levels = db.level


@client.event
async def on_ready():
    print('i am ready')

@client.event
async def on_message(message):
    user = message.author
    channel = message.channel
    gained_points = random.randint(1, 3)
    # get point
    if userData.count_documents({'id' : user.id}) :
        userData.update_one({'id' : user.id}, {'$inc' : {'points' : gained_points, 'experience': 1}})
        await check_for_level_up(user, channel)
    else:
        add_new_user_to_db(user)
        userData.update_one({'id' : user.id}, {'$inc' : {'points' : gained_points, 'experience': 1}})


    # mentions bot
    if client.user.mentioned_in(message) :
        if message.content == '@everyone' :
            return
        else:
            try:
                await channel.send(mention(user) + ' please don\'t @ me. Try `!yeet` to see what you can do with me.')
            except:
                return

    if message.content.startswith('!yeet '):
        await parse_command(message)

    elif message.content == '!yeet':
        #send instructions
        try:
            await message.delete()
        except:
            pass
        finally:
            try:
                print('send instructions')
                await send_instruction(user, 1)
            except:
                pass
       

#decrease experience by 1 to offset the welcome message
@client.event
async def on_member_join(user):
    if not userData.count_documents({'id' : user.id}) :
        add_new_user_to_db(user)
        userData.update_one({'id' : user.id}, {'$inc' : {'experience': -1}})
    else:
        userData.update_one({'id' : user.id}, {'$inc' : {'experience': -1}})

def add_new_user_to_db(user):
    userData.insert_one({'id': user.id, 'experience': 0, 'level': 1, 'points': 0, 'last claim': None})

async def check_for_level_up(user, channel):
    user_document = userData.find_one({'id' : user.id})
    user_level = user_document.get('level')
    user_experience = user_document.get('experience')
    if (levels.find_one({'level' : user_level}).get('max experience') <= user_experience) :
        new_level = user_level + 1
        userData.update_one({'id' : user.id}, {'$set' : {'experience' : 0, 'level' : new_level}})
        level_up_embed = discord.Embed(
            title = ':arrow_up: LEVEL UP :arrow_up:',
            color = discord.Colour.green(),
            description = '{} leveled up to level {}. :tada:'.format(user.name, new_level),
        )
        try:
            await channel.send(embed=level_up_embed)
        except:
            pass
        if levels.count_documents({'level' : user_level + 1}) :
            return
        else:
            multiplier = 1
            if 1 < new_level <= 50 :
                multiplier = 5
            elif 50 < new_level <= 100 :
                multiplier = 4
            elif 100 < new_level <= 150 :
                multiplier = 3
            elif 150 < new_level <= 200 :
                multiplier = 2
            levels.insert_one({'level' : new_level, 'max experience' : new_level * multiplier})
    else:
        return


def mention(user):
    return '<@'+str(user.id)+'>'

async def send_instruction(user, page):
    instruction = discord.Embed(
        title = 'Yeetus Commands page {}'.format(page),
        color = discord.Colour.default(),
        description = 'instructions go here',
    )
    await user.create_dm()
    await user.dm_channel.send(embed=instruction)


async def parse_command(message):
    channel = message.channel
    entire_message = message.content.split()
    command = entire_message[1]
    if command == 'claim' :
        print('claim')
        user = message.author
        last_claim = userData.find_one({'id' : user.id}).get('last claim')
        if (last_claim == None or datetime.datetime.now() - last_claim >= datetime.timedelta(seconds=79200)) :
            userData.update_one({'id' : user.id}, {'$inc' : {'points' : 200}, '$set' : {'last claim' : datetime.datetime.now()}})
            await channel.send('Here are your daily **200** points.')
        else:
            try:
                next_claim_time = str(datetime.timedelta(seconds=79200) - (datetime.datetime.now() - last_claim)).split(':')
                await channel.send(':x: You already claimed your daily points within the last 22 hours. \n Try again in **{} hours** and **{} minutes**.'.format(next_claim_time[0], next_claim_time[1]))
            except:
                return

    elif command == 'about' :
        print('about')
    elif command == 'gamble' :
        print('gamble')
    else: 
        try:
            error = discord.Embed(
                title = ':x: Unkown Command :x:',
                color = discord.Colour.red(),
                description = 'Try `!yeet` to see what I can do.',
            )
            await channel.send(embed=error)
        except:
            pass

    

client.run(TOKEN)