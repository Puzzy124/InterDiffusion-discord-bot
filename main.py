from collections import defaultdict
from discord.ext import commands
from discord import app_commands
from aiocache import cached
import discord
import aiohttp
import secrets
import random
import time
import re

proxy          = None # set proxy url here
TOKEN: str     = None # bot token to run bot on 


# custom rate limit (ik discord sdk has one but this cooler)
global last_reset, request_count
request_count = defaultdict(int)
last_reset = time.monotonic()
def check_rate_limit(user):
    global last_reset, request_count
    current_time = time.monotonic()
    elapsed_time = current_time - last_reset
    if elapsed_time >= 60:
        request_count.clear()
        last_reset = current_time
    request_count[user] += 1
    if request_count[user] > 5: # 5 requests a minute for rate limit, change as you like.
        return False
    return True
        
@cached() # cache 
async def generate_image(prompt: str, negative: str = "", seed: int = None, steps: int = 15) -> str:
    """
    Args:
        prompt (str): what to make
        negative (str, optional): what not to be in the image. Defaults to "".
        seed (int, optional): seed to use. Defaults to None.
        steps (int, optional): how many steps image is. Defaults to 15.

    Returns:
        str: url
    """
    headers      = {'accept': '*/*','accept-language': 'en-US,en;q=0.9','content-type': 'application/json','origin': 'https://creitingameplays-interdiffusion-4-0.hf.space','priority': 'u=1, i','referer': 'https://creitingameplays-interdiffusion-4-0.hf.space/?__theme=dark','sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',}
    session_hash = secrets.token_hex(11)
    url          = "https://creitingameplays-interdiffusion-4-0.hf.space/queue/join?__theme=dark"
    data = {"data": [    f"{prompt}",    f"{negative}",    '(LoRA)',    True,    steps,    1,    seed,    1024,    1024,    6,    True],"event_data": None,"fn_index": 3,"trigger_id": 6,"session_hash": session_hash}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, json=data, proxy=proxy) as response:
            if response.status == 200:
                pass
            else:
                return False
        
        async with session.get(url=f"https://creitingameplays-interdiffusion-4-0.hf.space/queue/data?session_hash={session_hash}", headers=headers, proxy=proxy) as response:
            response.raise_for_status()
            async for chunk in response.content.iter_any():
                data = chunk.decode('utf-8', 'ignore')
                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+|ftp://[^\s<>"]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>"]*)?', data)
                for obj in urls:
                    if "http" in obj:
                        return obj # url found

########################################################################
#Credits to .puzzy.                                                    #
#https://shard-ai.xyz                                                  #
#discord.gg/ligma                                                      #
#Dear skids, smd :)                                                    #
########################################################################

#setup discord bot and run it
intents        = discord.Intents.default()
intents.message_content = True
client         = commands.Bot(intents=intents, command_prefix='/')


class ImageButtons(discord.ui.View):
    def __init__(self, interaction, prompt, negative, seed, steps):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.prompt = prompt
        self.negative = negative
        self.seed = seed
        self.steps = steps
        self.regenerating = False

    @discord.ui.button(label="🗑️ Delete", style=discord.ButtonStyle.danger)
    async def delete_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.interaction.delete_original_response()

    @discord.ui.button(label="🔄 Regenerate", style=discord.ButtonStyle.primary)
    async def regenerate_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if check_rate_limit(interaction.user.id):
            if self.regenerating:
                await interaction.response.send_message("The image is already being regenerated. Please wait.", ephemeral=True)
                return

            self.regenerating = True
            await interaction.response.defer()
            new_seed = random.randint(1, 1000)
            image_url = await generate_image(self.prompt, self.negative, new_seed, self.steps)
            if image_url:
                embed = discord.Embed(title=f"Generated Image For {interaction.user.name}", color=discord.Color.random(), url=image_url, colour=discord.Color.dark_blue(), description=f"✍️ Prompt: {self.prompt}")
                embed.set_image(url=image_url)
                embed.set_footer(text='👑 Made by .puzzy. with 💖')
                await interaction.edit_original_response(embed=embed)
            else:
                await interaction.edit_original_response(embed=discord.Embed(title="Uh oh!", color=discord.Color.random(), description='Something went wrong, try again later.').set_footer(text='Made by .puzzy. with 💖'))
            self.regenerating = False
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Uh oh!", description="You have hit the rate limit of 5 generations a minute. Please wait!", color=discord.Color.red()))


@client.tree.command(
    name="imagine",
    description="Use InterDiffusion-4.0 To Create An Image!",
)
@app_commands.describe(
    prompt="What do you want to make?",
    negative="What do you not want to be in the image?",
    seed="What seed do you want to use?",
    steps="How many steps do you want to use?"
)
async def imagne_command(interaction: discord.Interaction, prompt: str, negative: str = "ugly, bad", seed: int = random.randint(1, 1000), steps: int = 15):
    try:
        if check_rate_limit(interaction.user.id):
            message = await interaction.response.send_message(embed=discord.Embed(title=f"Generating a {prompt}!", color=discord.Color.dark_blue()).set_footer(text="👑 Made by .puzzy. with 💖"))
            if steps > 60:
                steps = 60
            elif steps < 10:
                steps = 10
            if 0 > seed:
                seed = random.randint(1, 1000)
            # start image
            image_url = await generate_image(prompt, negative, seed, steps)
            if image_url:
                embed=discord.Embed(title=f"Generated Image For {interaction.user.name}",color=discord.Color.random(),url=image_url,colour=discord.Color.dark_blue(), description=f"✍️ Prompt: {prompt}")
                embed.set_image(url=image_url)
                embed.set_footer(text='👑 Made by .puzzy. with 💖')
                
                view = ImageButtons(interaction, prompt, negative, seed, steps)
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.edit_original_response(embed=discord.Embed(title="Uh oh!",color=discord.Color.random(),description='Something went wrong, try again later.').set_footer(text='Made by .puzzy. with 💖'))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Uh oh!", description="You have hit the rate limit of 5 generations a minute. Please wait!", color=discord.Color.red()))
    except discord.errors.HTTPException:
        pass
    
@client.tree.command(name="ping", description="Get the bots ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(title="My ping is...",description=f"{round(client.latency * 1000, 2)}ms!"))
    
    
@client.event
async def on_ready():
    await client.tree.sync()
    print("Ready!")

client.run(TOKEN)