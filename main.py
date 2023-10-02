import discord
from discord.embeds import Embed
from discord.ext import commands
from discord import utils
import json
import os
import random
import requests
from hentai import Hentai, Format, Sort

from PIL import Image,ImageFont,ImageDraw
from io import BytesIO

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json", "r") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": ""}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]

client = commands.Bot(command_prefix=">")
client.remove_command("help")

f = open("FortuneResponses.txt","r") #responses for fortune command
FortuneResponses = f.readlines()
f = open("Punchgifs.txt","r") #gifs for punch command
PunchGifs = f.readlines()
f = open("Killgifs.txt","r") #gifs for kill command
KillGifs = f.readlines()
f = open("Stabgifs.txt","r") #gifs for stab command
StabGifs = f.readlines()
f = open("Slapgifs.txt","r") #gifs for slap command
SlapGifs = f.readlines()
logging_channel = 892076435999690772

mainshop = [{"name":"padlock","price":300, "description": "Keeps your wallet safe (ONE TIME USE ITEM)" },
            {"name":"laptop","price":1000, "description": "Watch nyaa videos on twitch and get paid for it (convinent isn't it?)" },
            {"name":"invis","price":30000, "description": "You get <@&881525262779576330> for 3 days" }]

@client.event
async def on_ready(): #startup
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f"kittens on {len(client.guilds)} servers"))
    print("Bot is ready")

@client.event
async def on_message(message):
    mention = f'<@!882881947024650250>'
    if message.author.bot:
        return
    elif mention in message.content:
        await message.channel.send("My prefix is `>`")

    await client.process_commands(message)

@client.event
async def on_message_delete(message):
    global logging_channel
    embed = discord.Embed(title="{} deleted a message".format(message.author.name),
                          description="", color=0xFF0000)
    embed.add_field(name=message.content, value="This is the message that he has deleted",
                    inline=True)
    channel = client.get_channel(892076435999690772)
    await channel.send(channel, embed=embed)

@client.command()
async def inv(ctx):
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=882881947024650250&permissions=0&scope=bot%20applications.commands")

@client.command(aliases=['bal'])
async def balance(ctx, member:discord.Member = None):
    
    if not member:
        member = ctx.author
    await open_account(member)

    users = await get_bank_data()
    user = member

    wallet_amount = users[str(user.id)]["wallet"]
    bank_amount = users[str(user.id)]["bank"]

    balEmbed = discord.Embed(title = f"{member.name}'s balance", color= ctx.author.color)
    balEmbed.add_field(name="**Wallet**", value= wallet_amount)
    balEmbed.add_field(name="**Bank**", value= bank_amount)
    await ctx.send(embed=balEmbed)
    print("test")

@client.command()
@commands.cooldown(1,300,commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    user = ctx.author

    tempvar = random.randrange(5)

    if tempvar == 2:
        tempEmbed = discord.Embed(title = f"Beg",description = f"You went out begging but everyone ignored you :pensive:", color= ctx.author.color)
        tempEmbed.set_footer(text = f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed= tempEmbed)
    else:

        earnings = random.randrange(50)

        begEmbed = discord.Embed(title = f"Beg",description = f"You went out begging and some kind soul gave you **{earnings}** :peach: ", color= ctx.author.color)
        begEmbed.set_footer(text = f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed= begEmbed)

        users[str(user.id)]["wallet"] += earnings
        
        with open("mainbank.json", "w") as f:
            json.dump(users, f, indent=4)

@client.command(aliases=['with'])
async def withdraw(ctx,amount = None):

    bal = await update_bank(ctx.author)

    await open_account(ctx.author)
    if amount == None:
        amount = bal[1]

    amount = int(amount)
    if amount>bal[1]:
        tempEmbed = discord.Embed(description = f"You don't have that much money in your bank", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    if amount<0:
        tempEmbed = discord.Embed(description = f"The amount must be positive bruh ._.", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount, "bank")
    withEmbed = discord.Embed(description = f"You withdrew {amount} :peach: from your bank", color= ctx.author.color)
    await ctx.send(embed = withEmbed)

@client.command(aliases=['dep'])
async def deposit(ctx,amount = None):

    bal = await update_bank(ctx.author)

    await open_account(ctx.author)
    if amount == None:
        amount = bal[0]

    amount = int(amount)
    if amount>bal[0]:
        tempEmbed = discord.Embed(description = f"You don't have that much money in your wallet", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    if amount<0:
        tempEmbed = discord.Embed(description = f"The amount must be positive bruh ._.", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount, "bank")
    depEmbed = discord.Embed(description = f"You depositted {amount} :peach: in your bank", color= ctx.author.color)
    await ctx.send(embed = depEmbed)

@client.command()
async def rob(ctx,member:discord.Member = None):
    await open_account(ctx.author)
    await open_account(member)

    ahabal = await update_bank(ctx.author)
    bal = await update_bank(member)

    if member == None:
        depEmbed = discord.Embed(description = f"Whom will you steal tho *nyaa*", color= ctx.author.color)
        await ctx.send(embed = depEmbed)

    if bal[0] <= 250:
        tempEmbed = discord.Embed(description = f"{member} is not worth the risk lmao. That guy doesn't even have more than **250** :peach:", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    if ahabal[0] < 100:
        tempEmbed = discord.Embed(description = f"Stop being cheap, you need atleast **100** :peach: in your wallet to steal someone", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    chances = random.randrange(1,6)
    earnings = random.randrange(0,bal[0])

    if chances == 1 or 2 or 3:

        await update_bank(ctx.author,1*earnings)
        await update_bank(member,-1*earnings)

        depEmbed = discord.Embed(description = f"You stole **{earnings}** :peach: from {member}", color= ctx.author.color)
        await ctx.send(embed = depEmbed)

    else:
        depEmbed = discord.Embed(description = f"You got caught and gave 100 :peach: as a bribe", color= ctx.author.color)
        await ctx.send(embed = depEmbed)

        await update_bank(ctx.author,-100)

@client.command()
async def send(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)


    if amount == None:
        tempEmbed = discord.Embed(description = f"You need to enter the amount first", color= ctx.author.color,)
        await ctx.send(embed = tempEmbed)
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount>bal[0]:
        tempEmbed = discord.Embed(description = f"You don't have that much money in your wallet", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    if amount<0:
        tempEmbed = discord.Embed(description = f"The amount must be positive bruh ._.", color= ctx.author.color)
        await ctx.send(embed = tempEmbed)
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(member,amount)

    depEmbed = discord.Embed(description = f"You gifted **{amount}** :peach: to {member}", color= ctx.author.color)
    await ctx.send(embed = depEmbed)

@client.command(aliases=['rl'])
async def roulette(ctx, choice = None, amount = None):
    amount = int(amount)
    if choice == None:
        em = discord.Embed(title="Command error", description= "You did not enter what do you wanna gamble on", color = ctx.author.color, timestamp=ctx.message.created_at)
        em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
        await ctx.send(embed=em)
    elif amount == None:
        em = discord.Embed(title="Command error", description= "You did not enter amount to be gambled", color = ctx.author.color)
        em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
        await ctx.send(embed=em)
    elif amount < 20:
        em = discord.Embed(title="Insufficient money", description= "Bet atleast 20 :peach:", color = ctx.author.color)
        em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
        await ctx.send(embed=em)
    else:
        bal = await update_bank(ctx.author)
        if amount>bal[0]:
            await ctx.send("You don't have enough money in your wallet ._.")
        elif choice == "red" or "Red" or "RED" :
            result =  random.randrange(7)
            if result == 2 or 3 or 1:
                await update_bank(ctx.author,amount)
                bal = await update_bank(ctx.author,1*amount)
                em = discord.Embed(title="Congratulations you've won the gamble", description= f"You've won {2*amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

            else:
                await update_bank(ctx.author,-1*amount)
                em = discord.Embed(title="F you lost the gamble", description= f"You've lost {amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                bal = await update_bank(ctx.author,1*amount)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

        elif choice == "black" or "Black" or "Black":
            result =  random.randrange(1,11)
            if result == 2 or 4 or 6 or 8 or 10:
                await update_bank(ctx.author,1*amount)
                bal = await update_bank(ctx.author,amount)
                em = discord.Embed(title="Congratulations you've won the gamble", description= f"You've won {2*amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)
            else:
                await update_bank(ctx.author,-1*amount)
                em = discord.Embed(title="F you lost the gamble", description= f"You've lost {amount} :peach:", color = ctx.author.color)
                em.add_field(name=f"dice landed on",value=result)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                bal = await update_bank(ctx.author,amount)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

        elif choice == "even" or "Even" or "EVEN":
            result =  random.randrange(36)
            if result == 2 or 4 or 6 or 8 or 10 or 12 or 14 or 16 or 18 or 20 or 22 or 24 or 26 or 28 or 30 or 32 or 34 or 36:
                bal = await update_bank(ctx.author,amount)
                em = discord.Embed(title="Congratulations you've won the gamble", description= f"You've won {2*amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url="https://i.imgur.com/Qq3xF6S.png")
                em.add_field(name=f"dice landed on",value=result)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)
            else:
                await update_bank(ctx.author,-1*amount)
                em = discord.Embed(title="F you lost the gamble", description= f"You've lost {amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                bal = await update_bank(ctx.author,amount)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

        elif choice == "odd" or "Odd" or "ODD":
            result =  random.randrange(36)
            if result == 2 or 4 or 6 or 8 or 10 or 12 or 14 or 16 or 18 or 20 or 22 or 24 or 26 or 28 or 30 or 32 or 34 or 36:
                await update_bank(ctx.author,-1*amount)
                em = discord.Embed(title="F you lost the gamble", description= f"You've lost {amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                bal = await update_bank(ctx.author,amount)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

            else:
                await update_bank(ctx.author,2*amount)
                bal = await update_bank(ctx.author)
                em = discord.Embed(title="Congratulations you've won the gamble", description= f"You've won {2*amount} :peach:", color = ctx.author.color)
                em.set_thumbnail(url='https://i.imgur.com/Qq3xF6S.png')
                em.add_field(name=f"dice landed on",value=result)
                em.add_field(name="New Balance",value= bal[0])
                await ctx.send(embed = em)

@client.command(aliases=["s"])
async def shop(ctx):
    em = discord.Embed(title = "Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        Desc = item["description"]
        em.add_field(name=name, value=f":peach: {price} \n {Desc}")

    await ctx.send(embed = em)

@client.command()
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return


    await ctx.send(f"You just bought {amount} {item}")

@client.command(pass_context=True)
@commands.cooldown(1, 60*60*24, commands.BucketType.user)
async def daily(ctx):
    
    await update_bank(ctx.author, 160)

    embed = discord.Embed(title="Daily claimed", description="Depositted :peach:160 in your account *nyaa* come back in 24 hours to claim again",  color = ctx.author.color)
    await ctx.send(embed = embed)

@client.command()
async def use(ctx, item_name,*, nick = None):
    users = await get_bank_data()
    guild = ctx.guild
    member = ctx.author
    user = member
    item_name2 = str(item_name)                      #if use invis
    item_name3 = item_name2.lower()
    
    item_name4 = "invis"
    item_name5 = str(item_name4)
    if item_name3 == item_name5:
        InvisRole = discord.utils.get(guild.roles, name="Invisible")
        await member.add_roles(InvisRole)

        embed = discord.Embed(title="Successful", description="Gave you <@&881525262779576330> role *nyaa* You will have this role only for 3 days :D")
        await ctx.send(embed = embed)
        await ctx.send(f"||<@&879936318413623297> pls remove {member}'s Invisble role after 3 days||")

@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await ctx.send(embed = em) 

@client.command()
async def delete(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    delete = Image.open("delete.png")

    asset = user.avatar
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((194,194))

    delete.paste(pfp, (120,135))
    delete.save("profile.png")

    await ctx.send(file = discord.File("profile.png"))

@client.command()
async def toilet(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    delete = Image.open("toilet.jpg")

    asset = user.avatar
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((205,205))

    delete.paste(pfp, (134,349))
    delete.save("toilet_2.png")

    await ctx.send(file = discord.File("toilet_2.png"))

@client.command()
async def fu(ctx, Member = None):
    if Member == None:
        await ctx.send(f"Fuck you. You useless piece of shit. You absolute waste of space and air. You uneducated, ignorant, idiotic dumb swine, you’re an absolute embarrassment to humanity and all life as a whole. The magnitude of your failure just now is so indescribably massive that one hundred years into the future your name will be used as moniker of evil for heretics. Even if all of humanity put together their collective intelligence there is no conceivable way they could have thought up a way to fuck up on the unimaginable scale you just did. When Jesus died for our sins, he must not have seen the sacrilegious act we just witnessed you performing, because if he did he would have forsaken humanity long ago so that your birth may have never become reality. After you die, your skeleton will be displayed in a museum after being scientifically researched so that all future generations may learn not to generate your bone structure, because every tiny detail anyone may have in common with you degrades them to a useless piece of trash and a burden to society. No wonder your father questioned whether or not your were truly his son, for you'd have to not be a waste of carbon matter for anyone to love you like a family member. Your birth made it so that mankind is worse of in every way you can possibly imagine, and you have made it so that society can never really recover into a state of organization. Everything has forever fallen into a bewildering chaos \n -{ctx.author} ")
        await ctx.delete()
        return
    
    await ctx.send(f"Fuck you {Member}. You useless piece of shit. You absolute waste of space and air. You uneducated, ignorant, idiotic dumb swine, you’re an absolute embarrassment to humanity and all life as a whole. The magnitude of your failure just now is so indescribably massive that one hundred years into the future your name will be used as moniker of evil for heretics. Even if all of humanity put together their collective intelligence there is no conceivable way they could have thought up a way to fuck up on the unimaginable scale you just did. When Jesus died for our sins, he must not have seen the sacrilegious act we just witnessed you performing, because if he did he would have forsaken humanity long ago so that your birth may have never become reality. After you die, your skeleton will be displayed in a museum after being scientifically researched so that all future generations may learn not to generate your bone structure, because every tiny detail anyone may have in common with you degrades them to a useless piece of trash and a burden to society. No wonder your father questioned whether or not your were truly his son, for you'd have to not be a waste of carbon matter for anyone to love you like a family member. Your birth made it so that mankind is worse of in every way you can possibly imagine, and you have made it so that society can never really recover into a state of organization. Everything has forever fallen into a bewildering chaos \n -{ctx.author} ")
    await ctx.delete()
@client.command()

async def bulton(ctx, Member = None):
    if Member == None:
        await ctx.send(f"Dekh bhaia aisa hai ke mene tere jaise bhaut randve dekhe hai discord pe jinke life khali anime hote hai aur uske aalava kuch nhi. Aaise logo ke koye dost nhi hote, bas apne so called \"online friends\" (jinke inhone shakal bhi nahi dekhe aaj tak) ko asli dost maan lete hai. Yeh log anonymity ke gaane gaate hai aur din bhar akele rehte hai apne room me. Yeh log bhaut insecure hote hai apne life me esleye apne \"online frnds\" ko bhi kuch nhi batate apne real life ke baare me coz they have already given up on their real life and think that this online bullshit is their life. Aaise log akele he rehta hai aur akele he marte hai. Aur ha inke batane se phat te hai kyuki anime ne inka dimag kharab kar diya hota hai ke inke saath kuch bhura ho jaega agar inhone online kisi ko kuch bhi bol diya. En logo ne duniya bhar ke saare anime forums padh rakhe hote hai aur esleye inke anime knowledge khatarnak hote hai. Par en chutiyo ko yeh nhi pata ke anime knowledge real world me kaam nahi aaege aur \"online friends\" real world me help karne nhi aaenge. Aaise log bade hote hote depression me aa jate hai. BTW tu aaisa hai \n -{ctx.author} ")
        await ctx.delete()
        return
    
    await ctx.send(f"Dekh {Member} aaisa hai ke mene tere jaise bhaut randve dekhe hai discord pe jinke life khali anime hote hai aur uske aalava kuch nhi. Aaise logo ke koye dost nhi hote, bas apne so called \"online friends\" (jinke inhone shakal bhi nahi dekhe aaj tak) ko asli dost maan lete hai. Yeh log anonymity ke gaane gaate hai aur din bhar akele rehte hai apne room me. Yeh log bhaut insecure hote hai apne life me esleye apne \"online frnds\" ko bhi kuch nhi batate apne real life ke baare me coz they have already given up on their real life and think that this online bullshit is their life. Aaise log akele he rehta hai aur akele he marte hai. Aur ha inke batane se phat te hai kyuki anime ne inka dimag kharab kar diya hota hai ke inke saath kuch bhura ho jaega agar inhone online kisi ko kuch bhi bol diya. En logo ne duniya bhar ke saare anime forums padh rakhe hote hai aur esleye inke anime knowledge khatarnak hote hai. Par en chutiyo ko yeh nhi pata ke anime knowledge real world me kaam nahi aaege aur \"online friends\" real world me help karne nhi aaenge. Aaise log bade hote hote depression me aa jate hai. BTW tu aaisa hai \n -{ctx.author} ")
    await ctx.delete()
    
@client.command()
async def widepfp(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    asset = user.avatar
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((4000,650))

    pfp.save("widepfp_2.png")

    await ctx.send(file = discord.File("widepfp_2.png"))

@client.command()
async def clyde(ctx,*,msg = None):
    if msg == None:
        await ctx.send("Please enter the message you want to send *nyaa*")
        return
    img = Image.open("clyde.png")
    font = ImageFont.truetype("whitneymedium.otf",15)
    
    draw = ImageDraw.Draw(img)

    draw.text((74,33), msg, (255,255,255), font= font)
    img.save("clyde_2.png")

    await ctx.send(file = discord.File("clyde_2.png"))
    
@client.command()
async def punch(ctx, *, member:discord.Member=None): #punch
    if(member == None):
        em = discord.Embed(title = ":punch: **Punch**", description = f"**{ctx.author.name}** is punching", colour = ctx.author.colour)
        em.set_image(url=random.choice(PunchGifs))
        await ctx.send(embed = em)
    else:
        em = discord.Embed(title = "**Punch**", description = f"**{member}** you are getting punched by **{ctx.author.name}**", colour = ctx.author.colour)
        em.set_image(url=random.choice(PunchGifs))
        await ctx.send(embed = em)

@client.command()
async def stab(ctx, *, member:discord.Member=None): #stab
    if(member == None):
        em = discord.Embed(title = ":knife: **Stab**", description = f"**{ctx.author.name}** is Stabbing", colour = ctx.author.colour)
        em.set_image(url=random.choice(StabGifs))
        await ctx.send(embed = em)
    else:
        em = discord.Embed(title = ":knife: **Stab**", description = f"**{member}** you are getting stabbed by **{ctx.author.name}**", colour = ctx.author.colour)
        em.set_image(url=random.choice(StabGifs))
        await ctx.send(embed = em)

@client.command()
async def kill(ctx, *, member:discord.Member=None): #kill
    if(member == None):
        em = discord.Embed(title = ":skull_crossbones: **Kill**", description = f"**{ctx.author.name}** is killing", colour = ctx.author.colour)
        em.set_image(url=random.choice(KillGifs))
        await ctx.send(embed = em)
    else:
        em = discord.Embed(title = ":skull_crossbones: **Kill**", description = f"**{member}** you are getting killed by **{ctx.author.name}**", colour = ctx.author.colour)
        em.set_image(url=random.choice(KillGifs))
        await ctx.send(embed = em)

@client.command()
async def slap(ctx, *, member:discord.Member=None): #slap
    if(member == None):
        em = discord.Embed(title = "**Slap**", description = f"**{ctx.author.name}** is Slapping", colour = ctx.author.colour)
        em.set_image(url=random.choice(SlapGifs))
        await ctx.send(embed = em)
    else:
        em = discord.Embed(title = "**Slap**", description = f"**{member}** you are getting slapped by **{ctx.author.name}**", colour = ctx.author.colour)
        em.set_image(url=random.choice(SlapGifs))
        await ctx.send(embed = em)

@client.command(aliases=['Fortune'])
async def fortune(ctx, *, question):
    
    em = discord.Embed(title = "**Question**", description = f"**{question}**", colour = ctx.author.colour)
    em.add_field(name = "**Answer**", value = f"**{random.choice(FortuneResponses)}**")
    em.set_footer(text = f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    
    await ctx.send(embed = em)

NickPerm = False
@client.command(aliases=['NickPerm'])
@commands.has_permissions(ban_members = True)
async def NickPerms(ctx):
    global NickPerm

    if NickPerm == False:
        NickPerm = True
        await ctx.send("Nick perms were **not** allowed before, Now they are. GG")

    elif NickPerm == True:
        NickPerm = False
        await ctx.send("Nickname perms were allowed now they are not, F for members")

@client.command()
async def doujin(ctx,id = None):
    if ctx.channel.id == 879957789005459457:
        if id == None:
            await ctx.send("Enter an ID")
            return
        else:
            doujin = Hentai(id)
            Boolean = Hentai.exists(doujin.id)
            if Boolean == False:
                await ctx.send("Doujin doesn\'t exist")
                return
            await ctx.send("**Name**- ")
            await ctx.send(doujin.title(Format.Pretty))
            await ctx.send("**Artist Details**- ")
            await ctx.send(doujin.artist)
            await ctx.send("**Tags**- ")
            await ctx.send(f"|| {[tag.name for tag in doujin.tag]}||")
            await ctx.send("**Uploaded at**- ")
            await ctx.send(doujin.upload_date)
            await ctx.send("**Read now**- ")
            await ctx.send(f"|| {doujin.image_urls}||")

            title = doujin.title(Format.Pretty)
            tags = [tag.name for tag in doujin.tag]
            thumb = doujin.image_urls
            artist = doujin.artist
            Date = doujin.upload_date


            em = discord.Embed(title= f"{title}", description=f"{tags}", color= ctx.author.color)
            em.set_thumbnail(url=thumb)
            em.add_field(title= "Artist", value = f"{artist}")
            em.add_field(title= "Uploaded at", value = f"{Date}")
            em.set_footer(text = f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed = em)
    else:
        embed = discord.Embed(description=":x: This command can only be used in <@%879957789005459457>")
        await ctx.send(embed = embed)


@client.command(aliases=['nickname'])
async def nick(ctx,*,Nickname = None):
    member = ctx.author
    global NickPerm

    if NickPerm == True:
        if Nickname == None:
            embed = discord.Embed(title="Enter the nickname you want to use", description="Syntax- \n >pip install --upgrade NHentai-APInickname \"Your Nickname\"")
            await ctx.send(embed = embed)
        else:
            await member.edit(nick=Nickname)
            embed = discord.Embed(title="Nickname Changed succesfully", description=f"Changed your nickname to {Nickname} \n Note that Staff is **NOT** responsible if any of the demi-gods change your nickname")
            await ctx.send(embed = embed)

    elif NickPerm == False:
            embed = discord.Embed(title="COMMAND NOT TURNED ON", description="Ask the Server admin to use `>NickPerms` to enable this command")
            await ctx.send(embed = embed)

async def open_account(user):
    users = await get_bank_data()
        
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 250
        
    
    with open("mainbank.json","w") as f:
        json.dump(users, f, indent=4)
    return True

async def get_bank_data():
    with open("mainbank.json","r") as f:
        users = json.load(f)

        return users

async def update_bank(user, change = 0, mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json","w") as f:
        json.dump(users, f, indent=4)

    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal

async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'Chill *nyaa*, Command on cooldown, try again in {:.1f}s'.format(error.retry_after)
        await ctx.send(msg)

# @client.command(aliases = ["lb"])
# async def leaderboard(ctx,x = 1):
#     users = await get_bank_data()
#     leader_board = {}
#     total = []
#     for user in users:
#         name = int(user)
#         total_amount = users[user]["wallet"] + users[user]["bank"]
#         leader_board[total_amount] = name
#         total.append(total_amount)

#     total = sorted(total,reverse=True)    

#     em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
#     index = 1
#     for amt in total:
#         id_ = leader_board[amt]
#         member = client.get_user(id_)
#         name = member.name
#         em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
#         if index == x:
#             break
#         else:
#             index += 1

#     await ctx.send(embed = em)


@client.command()
async def spam(ctx):
    number = 0
    if ctx.author.id == 697069015079583774:
        while True:
            number += 1
            await ctx.send(f"<@717965481906143333> Happy borthday bro... :partying_face: May you have a good year||ab valo aa :gun||", delete_after=1)
            print(f"loop {number}")

            if number >= 1000:
                break
    else:
        await ctx.send("Sorry man chad-only command")


@client.command()
async def Kruwush(ctx):
    channel = client.get_channel(879929576933969934)
    message = await channel.fetch_message(922693536061730886)
    while True:

        await message.edit(content="Krish Paplu")
        await message.edit(content="Lurku Chad")
        await message.edit(content="nice logs tho")
        await message.edit(content="Lurku OP")
        await message.edit(content="Get Rekt")
        await message.edit(content="fUwUck ho gaya")
        await message.edit(content="hahahahahaha")
        await message.edit(content="<@717965481906143333> lmfao :kekw:")
        await message.edit(content="tera cache lmfao")
        await message.edit(content="UwU")


client.run(token)