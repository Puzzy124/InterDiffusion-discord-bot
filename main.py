import aiohttp
import secrets
import re
import discord
from discord.ext import commands
from discord import app_commands
import random

proxy          = None # set proxy url here
TOKEN: str     = None # bot token to run bot on 

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
async def first_command(interaction: discord.Interaction, prompt: str, negative: str = "ugly, bad", seed: int = random.randint(1, 1000), steps: int = 15):
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

@client.event
async def on_ready():
    await client.tree.sync()
    print("Ready!")

client.run(TOKEN)