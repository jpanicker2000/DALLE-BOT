import asyncio
import io

import discord
from discord import app_commands


import urllib.request
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from PIL import Image, ImageDraw,ImageFont


def imgurls(webprompt: str):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, service=Service(GeckoDriverManager().install()))
    driver.get("https://www.craiyon.com/")
    try:
        promptbox = driver.find_element(By.ID, "prompt")
        promptbox.send_keys(webprompt)
        promptbox.send_keys(Keys.ENTER)

        wait = WebDriverWait(driver, 65, poll_frequency=2)
        found_grid = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='grid grid-cols-3 gap-2']")))
        if found_grid:

            x_path = "//img[@alt='" + webprompt + "<br>']"
            images = driver.find_elements(By.XPATH, x_path)
            src_list = [image.get_attribute('src') for image in images]
    except TimeoutException or TimeoutError:
        src_list = "Service is busy, please try later"
    finally:
        driver.close()
        driver.quit()
        return src_list

def imgcollage(srcs):
    collage = Image.new("RGB", (750, 750))
    count = 0

    for i in range(0, 750, 250):
        for j in range(0, 750, 250):
            urllib.request.urlretrieve(srcs[count], "temp.jpg")
            temp = Image.open("temp.jpg")
            temp.resize((250, 250))
            collage.paste(temp, (j, i))
            count += 1
    return collage

def find_font_size(text, font, image, target_width_ratio):
    tested_font_size = 100
    tested_font = ImageFont.truetype(font, tested_font_size)
    observed_width, observed_height = get_text_size(text, image, tested_font)
    estimated_font_size = tested_font_size / (observed_width / image.width) * target_width_ratio
    return round(estimated_font_size)

def get_text_size(text, image, font):
    im = Image.new('RGB', (image.width, image.height))
    draw = ImageDraw.Draw(im)
    box  = draw.textbbox((0, 0), text, font)
    w = int(box[2]-box[0])
    h = int(box[3]-box[1])
    return (w,h)

class botclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
            await self.wait_until_ready()

            if not self.synced:
                await tree.sync(guild=discord.Object(id=1013805327499661353))
                self.synced = True
            print(f"Logged in as {self.user}. ")


client = botclient()
tree =app_commands.CommandTree(client)

@tree.command(name="dalle",description="Enter Prompt to generate dalle images",guild=discord.Object(id=1013805327499661353))
async def self(interaction: discord.Interaction,prompt: str):
    await interaction.response.defer(thinking=True)
    resp = imgurls(prompt)
    if type(resp) == list:
        collage =  imgcollage(resp)
        font_name = 'C:\\Windows\\Fonts\\ARLRDBD.TTF'

        phdr = Image.new("RGB", (750, 100), (255, 108, 0))

        width_ratio = 0.5  # Portion of the image the text width should be (between 0 and 1)
        draw = ImageDraw.Draw(phdr)
        prompt = ">" + prompt
        font_size = find_font_size(prompt, font_name, phdr, width_ratio)
        font = ImageFont.truetype(font_name, font_size)
        draw.text((375, 50), prompt, font=font, anchor="mm")

        finalimg = Image.new("RGB", (750, 850))
        finalimg.paste(collage, (0, 0))
        finalimg.paste(phdr, (0, 750))
        with io.BytesIO() as image_binary:
            finalimg.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(fp=image_binary, filename='image.png'))
    else:
        await interaction.followup.send(resp)


client.run('MTAxMzgwMzU1ODc1NzQ4MjQ5Nw.G5XQ_X.82YYRDB4zD87V5w90q7YVvv5QnDbDOeHZMMmTE')