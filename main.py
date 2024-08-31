import nextcord
from nextcord.ext import commands
from PIL import Image
import requests
from io import BytesIO
import os

token = os.environ.get('TOKEN')

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="!")

# Variable to store the last processed image
last_image_url = None


@bot.command()
async def pocketlint(ctx):
    global last_image_url

    # Check if an image is attached to the message
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
    elif ctx.message.reference and ctx.message.reference.cached_message:
        # Check if the message is a reply with an attachment
        reply_message = ctx.message.reference.cached_message
        if reply_message.attachments:
            image_url = reply_message.attachments[0].url
        else:
            await ctx.send("The replied message does not contain an image.")
            return
    elif last_image_url:
        # Use the last processed image as fallback
        image_url = last_image_url
    else:
        await ctx.send("No image attached or replied, and no recent image found.")
        return

    # Download the image from the URL
    response = requests.get(image_url)

    # Process the image
    await process_image(ctx, response.content)

    # Update the last processed image URL
    last_image_url = image_url


async def process_image(ctx, image_content):
    img = Image.open(BytesIO(image_content))

    # Open the Bongo Cat image (pocketlint.png)
    bongo_img = Image.open("./pocketlint.png")

    # Calculate the scaling factor based on the width of the original image
    scale_factor = min(img.width / bongo_img.width, img.height / bongo_img.height)
    print(scale_factor)

    # Resize Bongo Cat to the scaled size
    bongo_img = bongo_img.resize((int(bongo_img.width * scale_factor), int(bongo_img.height * scale_factor)))

    # Ensure both images are in RGBA mode
    img = img.convert("RGBA")
    bongo_img = bongo_img.convert("RGBA")

    # Calculate the position to place Bongo Cat on the right side of the original image
    position = ((img.width - bongo_img.width), (img.height - bongo_img.height))

    # Paste Bongo Cat onto the original image at the calculated position
    img.paste(bongo_img, position, bongo_img)

    # Save the final image
    final_path = "final.png"
    img.save(final_path)

    # Send the final image
    await ctx.send(file=nextcord.File(final_path))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


bot.run(token)
