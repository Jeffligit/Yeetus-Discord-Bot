# bot.py
import os, os, pymongo, discord, random
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

    # get point
    if userData.count_documents({'id' : user.id}) :
        userData.update_one({'id' : user.id}, {'$inc' : {'points' : random.randint(1, 3), 'experience': 1}})
        await check_for_level_up(user, channel)
    else:
        add_new_user_to_db(user)


    # mention
    if client.user.mentioned_in(message) :
        await channel.send(mention(user) + ' please don\'t @ me. Try `!yeet` to see what you can do with me.')

    if message.content.startswith('!yeet '):
        print('command?')

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
       

@client.event
async def on_member_join(user):
    if not userData.count_documents({'id' : user.id}) :
        add_new_user_to_db(user)
        print('joined and added to db')
    else:
        userData.update_one({'id' : user.id}, {'$inc' : {'experience': -1}})

def add_new_user_to_db(user):
    userData.insert_one({'id': user.id, 'experience': 0, 'level': 1, 'points': 1})

async def check_for_level_up(user, channel):
    user_document = userData.find_one({'id' : user.id})
    user_level = user_document.get('level')
    user_experience = user_document.get('experience')
    print('before level up: {}'.format(user_experience))
    if (levels.find_one({'level' : user_level}).get('max experience') <= user_experience) :
        userData.update_one({'id' : user.id}, {'$inc' : {'level' : 1}, '$set' : {'experience' : 0}})
        print('LEVELED experience is now {}'.format(userData.find_one({'id' : user.id}).get('level')))
        level_up_embed = discord.Embed(
            title = ':arrow_up: LEVEL UP :arrow_up:',
            color = discord.Colour.green(),
            description = '{} leveled up to level {}. :tada:'.format(user.name, user_level + 1),
        )
        try:
            await channel.send(embed=level_up_embed)
        except:
            pass
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

client.run(TOKEN)