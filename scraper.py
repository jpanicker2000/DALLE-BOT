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
import io

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

prompt_str = input("Enter prompt:" )

options = Options()
options.headless = True

driver =webdriver.Firefox(options=options,service=Service(GeckoDriverManager().install()))
driver.get("https://www.craiyon.com/")

prompt = driver.find_element(By.ID, "prompt")
prompt.send_keys(prompt_str)
prompt.send_keys(Keys.ENTER)

try:
    wait = WebDriverWait(driver, 65,poll_frequency=2)
    found_grid = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='grid grid-cols-3 gap-2']")))
    if found_grid:

        x_path ="//img[@alt='"+prompt_str+"<br>']"
        images = driver.find_elements(By.XPATH,x_path)
        src_list = [image.get_attribute('src') for image in images]

        collage = Image.new("RGB", (750,750))
        count = 0

        for i in range(0,750,250):
            for j in range(0,750,250):
                urllib.request.urlretrieve(src_list[count], "temp.jpg")
                temp = Image.open("temp.jpg")
                temp.resize((250,250))
                collage.paste(temp,(j,i))
                count+=1

        width = 750
        height = 100

        font_name = 'C:\\Windows\\Fonts\\ARLRDBD.TTF'
        phdr = Image.new("RGB",(width,height),(255, 108, 0))

        width_ratio = 0.7  # Portion of the image the text width should be (between 0 and 1)
        draw = ImageDraw.Draw(phdr)
        prompt_str=">"+prompt_str
        font_size = find_font_size(prompt_str, font_name, phdr, width_ratio)
        font = ImageFont.truetype(font_name, font_size)
        draw.text((width/2, height/2), prompt_str, font=font,anchor="mm")

        finalimg =  Image.new("RGB",(750,850))
        finalimg.paste(collage,(0,0))
        finalimg.paste(phdr,(0,750))
        with io.BytesIO() as image_binary:
            finalimg.save(image_binary, 'PNG')
            image_binary.seek(0)

except TimeoutException:
    print("Service Timed Out....try again later")
finally:
    driver.close()
    driver.quit()