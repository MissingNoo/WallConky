from time import localtime, strftime, sleep
import gpu_utils
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
    subprocess.Popen(['/usr/bin/swaybg', '-i', '/tmp/out.png', '-m', 'fill', '-o', 'HEADLESS-2', '-i', '/home/airgeadlamh/Imagens/wall.png', '-m', 'fill'])
    time.sleep(.2)
    r2 = subprocess.run(['kill', pid], stdout=subprocess.PIPE)

def draw_text(x, y, text, size=16, color=(255, 255, 255), bold = False, anchor = "lt"):
    # font = ImageFont.truetype(<font-file>, <font-size>)
    if bold:
        font = ImageFont.truetype("OpenSans-Bold.ttf", size)
    else:
        font = ImageFont.truetype("OpenSans-Regular.ttf", size)
    draw.text((x, y), text, color, font=font, anchor = anchor)

def draw_graph(arr):
    if len(arr) > 12:
        arr.pop(0)
        for pos in arr:
            pos[0] -= steps
    arr.append([
        sx + offset + (len(arr) * steps),
        sy + yoffset - ((sy + yoffset * percent) / 140)]
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
cputemparr = []
gpuarr = []
gputemparr = []
shelldrop(['killall', 'swaybg'])
while True:
    gamemode = shell(['gamemoded', '-s'])
    if gamemode == "gamemode is active":
        sleep(10)
    sensors = psutil.sensors_temperatures()

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
    sy += 140
    draw_spacer(sx, sy)
    sy += 20

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
    sy += 50
    draw_text(sx, sy, "CPU Temp", 10, (255, 255, 255), True)
    sy += 15
    percent = sensors["k10temp"][0][1]
    draw_text(sx + 5, sy, str(percent) + "°", 32, (255, 85, 85))
    draw_graph(cputemparr)
    sy += 50

    # GPU
    draw_text(sx, sy, "GPU", 10, (255, 255, 255), True)
    sy += 15
    percent = int(shell(['cat', '/sys/class/hwmon/hwmon0/device/gpu_busy_percent']))
    draw_text(sx + 5, sy, str(percent) + "%", 32, (255, 85, 85))
    draw_graph(gpuarr)
    sy += 50
    draw_text(sx, sy, "GPU Temp", 10, (255, 255, 255), True)
    sy += 15
    percent = sensors["amdgpu"][0][1]
    draw_text(sx + 5, sy, str(percent) + "°", 32, (255, 85, 85))
    draw_graph(gputemparr)
    sy += 15

    #Spacer
    sy += 40
    draw_spacer(sx, sy)
    sy += 40

    #Song
    stitle = "Music"
    pctl = shell(['playerctl', '-a', 'metadata', 'title'])
    pctlstatus = shell(['playerctl', '-a', 'status'])
    ssource = "mpc"
    if pctl != "" and pctlstatus != "Paused":
        stitle = "Playing"
        ssource = "playerctl"
    draw_text(sx + 120, sy, stitle, size = 32, anchor = "mm")
    sy += 30
    if ssource == "mpc":
        playing = shell(['mpc', 'current'])
        try:
            playing = playing.split("-")
            a = (playing[1])
        except:
            playing = ["", playing]
    else:
        playing = ['', pctl]

    draw_text(sx + 120, sy, str(playing[1]).strip(), 20, (255, 85, 85), anchor = "mm")
    if ssource == "mpc":
        sy += 25
        draw_text(sx + 120, sy, str(playing[0]).strip(), 12, (178, 71, 81), anchor = "mm")
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

    #font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 128)
    #draw.text((1920 / 2, 1080 - 100), shell(['tail', '-1', '/tmp/cava.log']), purple, font=font, anchor="mm")

    img.save('/tmp/out.png')
    set_wallpaper("/tmp/out.png", output)
    time.sleep(.5)
    #exit()
