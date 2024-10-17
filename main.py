from time import localtime, strftime
import os
import wand
import subprocess
import time
import psutil
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
purple = (198, 160, 246)
wall = "wall.png"
output = "HDMI-A-1"
offset = 120
yoffset = 40
steps = 10
pid = -1

subprocess.run(['cp', wall, '/tmp/wall.png'], stdout=subprocess.PIPE).stdout.decode('utf-8')
wall = "/tmp/wall.png"

def shell(command):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
def shelldrop(command):
    return subprocess.run(command)

def get_path():
    return subprocess.run(['pwd'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

def set_wallpaper(path, output):
    #result = subprocess.run(['swaymsg', 'output', output, 'bg ', path, 'fill'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    subprocess.Popen(['/usr/bin/swaybg', '-i', '/tmp/out.png', '-m', 'fill'])
    time.sleep(.1)
    r2 = subprocess.run(['kill', pid], stdout=subprocess.PIPE)

def draw_text(x, y, text, size=16, color=(255, 255, 255), bold = False):
    # font = ImageFont.truetype(<font-file>, <font-size>)
    if bold:
        font = ImageFont.truetype("OpenSans-Bold.ttf", size)
    else:
        font = ImageFont.truetype("OpenSans-Regular.ttf", size)
    draw.text((x, y), text, color, font=font)

def draw_graph(arr):
    if len(arr) > 12:
        arr.pop(0)
        for pos in arr:
            pos[0] -= steps
    arr.append([
        sx + offset + (len(arr) * steps),
        sy + yoffset - ((sy + yoffset * percent) / 100)]
    )
    points = []
    for info in arr:
        points.append((info[0], info[1]))
    if len(arr) > 2:
        points.append((arr[len(arr) - 1][0], sy + 40))
        points.insert(0, (arr[0][0], sy + 40))
        draw.polygon(points, width=2, fill=purple)
    draw.rectangle((sx + offset, sy, sx + offset * 2, sy + 40), fill=None, outline=purple)

def draw_spacer(sx, sy):
    draw_text(sx - 5, sy, "-------------------------", 32, "white")

ramarr = []
cpuarr = []
while True:
    pid = subprocess.run(['pidof', 'swaybg'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    img = Image.open(wall)
    draw = ImageDraw.Draw(img)
    sx = 10
    sy = 0

    #Clock
    clock = Image.new("RGBA", (246, 128), color= (40, 42, 54))
    c1 = ImageDraw.Draw(clock)
    myFont = ImageFont.truetype("OpenSans-Bold.ttf", 75)
    myFont2 = ImageFont.truetype("OpenSans-Bold.ttf", 16)
    text_x = (clock.width) // 2
    text_y = (clock.height) // 2
    c1.text((text_x, text_y), str(strftime("%H:%M", localtime())), font=myFont, fill=(255, 255, 255), anchor="mm")
    c1.text((text_x, text_y + 45), str(strftime("%d/%m/%Y", localtime())), font=myFont2, fill=(255, 255, 255), anchor="mm")
    img.paste(clock, (sx, sy))

    #Spacer
    sy += 100
    draw_spacer(sx, sy)
    sy += 50

    #RAM
    draw_text(sx, sy, "RAM", 10, (255, 255, 255), True)
    sy += 15
    draw_text(sx + 5, sy, str(psutil.virtual_memory().percent) + "%", 32, (255, 85, 85))
    percent = psutil.virtual_memory().percent
    draw_graph(ramarr)

    #CPU
    sy += 50
    draw_text(sx, sy, "CPU", 10, (255, 255, 255), True)
    sy += 15
    percent = psutil.cpu_percent()
    draw_text(sx + 5, sy, str(percent) + "%", 32, (255, 85, 85))
    draw_graph(cpuarr)

    #Spacer
    sy += 40
    draw_spacer(sx, sy)
    sy += 40

    #Song
    draw_text(sx + 100, sy, "Music", 22)
    sy += 30
    playing = shell(['mpc', 'current'])
    try:
        playing = playing.split("-")
        a = (playing[1])
    except:
        playing = ["", playing]
    #namelen = len(playing[1])
    #sx += namelen
    draw_text(sx, sy, str(playing[1]), 16, (255, 85, 85))
    #sx -= namelen
    #singerlen = len(playing[0])
    sx += 4
    sy += 20
    draw_text(sx, sy, str(playing[0]), 12, (178, 71, 81))
    #sx -= singerlen
    #Get thumb
    filep = shell(['mpc', 'current' ,'-f', "%file%"])
    thumbname = playing[1]
    thumbcache = os.path.isfile('/tmp/' + thumbname + '.png')

    if not thumbcache:
        shelldrop(['ffmpeg', '-y', '-i', '/home/airgeadlamh/Music/' + filep, '-an', '-c:v', 'copy', '/tmp/' + thumbname + '.png'])
    sy += 20
    sx -= 5
    try:
        thumb = Image.open('/tmp/' + thumbname + '.png')
        thumb.thumbnail((256, 256))
        img.paste(thumb, (sx, sy))
    except:
        print("No Thumbnail")
    draw.rectangle((sx, sy, sx + 256, sy + 256), outline=(255, 85, 85))
    sx += 5
    sy += 256

    img.save('/tmp/out.png')
    set_wallpaper("/tmp/out.png", output)
    time.sleep(1)
    #exit()