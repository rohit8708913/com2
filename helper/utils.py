import asyncio
import math, time
from . import *
from datetime import datetime as dt
import sys
import shutil
import signal
import os
import ffmpeg 
from pathlib import Path
from datetime import datetime
import psutil
from pytz import timezone
from config import Config
from script import Txt
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto


QUEUE = []



async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["⬢" for i in range(math.floor(percentage / 5))]),
            ''.join(["⬡" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + Txt.PROGRESS_BAR.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",               
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data=f"close-{message.from_user.id}")]])                                               
            )
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def ts(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]


async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        botusername = await b.get_me()
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await b.send_message(
            Config.LOG_CHANNEL,
            f"**--Nᴇᴡ Uꜱᴇʀ Sᴛᴀʀᴛᴇᴅ Tʜᴇ Bᴏᴛ--**\n\nUꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: @{u.username}\n\nDᴀᴛᴇ: {date}\nTɪᴍᴇ: {time}\n\nBy: @{botusername.username}"
        )
        

def Filename(filename, mime_type):
    if filename.split('.')[-1] in ['mkv', 'mp4', 'mp3', 'mov']:

        return filename

    else:
        if mime_type.split('/')[1] in ['pdf', 'mkv', 'mp4', 'mp3']:
            return f"{filename}.{mime_type.split('/')[1]}"
        
        elif mime_type.split('/')[0] == "audio":
            return f"{filename}.mp3"

        else:
            return f"{filename}.mkv"
            
async def CANT_CONFIG_GROUP_MSG(client, message):
    botusername = await client.get_me()
    btn = [
        [InlineKeyboardButton(text='Bᴏᴛ Pᴍ', url=f'https://t.me/{botusername.username}')]
    ]
    ms = await message.reply_text(text="Sᴏʀʀʏ Yᴏᴜ Cᴀɴ'ᴛ Cᴏɴғɪɢ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs\n\nFɪʀsᴛ sᴛᴀʀᴛ ᴍᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍʏ ғᴇᴀᴛᴜᴇʀs ɪɴ ɢʀᴏᴜᴘ", reply_to_message_id = message.id, reply_markup=InlineKeyboardMarkup(btn))

    await asyncio.sleep(10)
    await ms.delete()


async def Compress_Stats(e, userid):


    if int(userid) not in [e.from_user.id, 0]:
        return await e.answer(f"⚠️ Hᴇʏ {e.from_user.first_name}\nYᴏᴜ ᴄᴀɴ'ᴛ sᴇᴇ sᴛᴀᴛᴜs ᴀs ᴛʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ", show_alert=True)
    
    inp = f"ffmpeg/{e.from_user.id}/{os.listdir(f'ffmpeg/{e.from_user.id}')[0]}"
    outp = f"encode/{e.from_user.id}/{os.listdir(f'encode/{e.from_user.id}')[0]}"
    try:
        ot = humanbytes(int((Path(outp).stat().st_size)))
        ov = humanbytes(int(Path(inp).stat().st_size))
        processing_file_name = inp.replace(f"ffmpeg/{userid}/", "").replace(f"_", " ")
        ans = f"Processing Media: {processing_file_name}\n\nDownloaded: {ov}\n\nCompressed: {ot}"
        await e.answer(ans, cache_time=0, show_alert=True)
    except Exception as er:
        print(er)
        await e.answer(
            "Someting Went Wrong.\nSend Media Again.", cache_time=0, alert=True
        )

async def skip(e, userid):

    if int(userid) not in [e.from_user.id, 0]:
        return await e.answer(f"⚠️ Hᴇʏ {e.from_user.first_name}\nYᴏᴜ ᴄᴀɴ'ᴛ ᴄᴀɴᴄᴇʟ ᴛʜᴇ ᴘʀᴏᴄᴇss ᴀs ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛ ɪᴛ", show_alert=True)
    try:
        await e.message.delete()
        os.system(f"rm -rf ffmpeg/{userid}*")
        os.system(f"rm -rf encode/{userid}*")
        for proc in psutil.process_iter():
            processName = proc.name()
            processID = proc.pid
            print(processName , ' - ', processID)
            if(processName == "ffmpeg"):
             os.kill(processID,signal.SIGKILL)
    except Exception as e:
        pass
    try:
        shutil.rmtree(f'ffmpeg' + '/' + str(userid))
        shutil.rmtree(f'encode' + '/' + str(userid))
    except Exception as e:
        pass
    
    return

async def CompressVideo(bot, query, ffmpegcode, c_thumb):
    UID = query.from_user.id
    ms = await query.message.edit('Pʟᴇᴀsᴇ Wᴀɪᴛ...\n\n**Fᴇᴛᴄʜɪɴɢ Qᴜᴇᴜᴇ 👥**')
    ph_path = None

    try:
        # Check for existing processes
        if os.path.isdir(f'ffmpeg/{UID}') and os.path.isdir(f'encode/{UID}'):
            return await ms.edit("**⚠️ Yᴏᴜ ᴄᴀɴ ᴄᴏᴍᴘʀᴇss ᴏɴʟʏ ᴏɴᴇ ғɪʟᴇ ᴀᴛ ᴀ ᴛɪᴍᴇ\n\nAs ᴛʜɪs ʜᴇʟᴘs ʀᴇᴅᴜᴄᴇ sᴇʀᴠᴇʀ ʟᴏᴀᴅ.**")

        # Fetch video details
        media = query.message.reply_to_message
        file = getattr(media, media.media.value)
        filename = str(file.file_name or f"{UID}_video.mp4")  # Handle no filename case
        file_extension = os.path.splitext(filename)[-1] or ".mp4"
        Download_DIR = f"ffmpeg/{UID}"
        Output_DIR = f"encode/{UID}"
        File_Path = f"{Download_DIR}/{filename}"
        Output_Path = f"{Output_DIR}/{UID}{file_extension}"

        # Start download
        await ms.edit('⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....**')
        os.makedirs(Download_DIR, exist_ok=True)
        os.makedirs(Output_DIR, exist_ok=True)

        dl = await bot.download_media(
            message=file,
            file_name=File_Path,
            progress=progress_for_pyrogram,
            progress_args=("\n⚠️__**Please wait...**__\n\n☃️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
        )

        await ms.edit("🗜 **Compressing...**")
        cmd = f"""ffmpeg -i "{dl}" {ffmpegcode} -vf "scale=ceil(iw/2)*2:ceil(ih/2)*2,drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10" -crf 23 -preset medium -threads 4 -bufsize 64M -movflags +faststart "{Output_Path}" -y"""
        print(f"Running FFmpeg command: {cmd}")  # Debugging

        # Run FFmpeg with real-time output logging
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stderr.readline()
            if not line:
                break
            print(line.decode().strip())  # Log FFmpeg progress

        # Check process completion
        await process.wait()
        if process.returncode != 0:
            raise Exception("FFmpeg processing failed.")

        # Thumbnail handling
        if file.thumbs or c_thumb:
            ph_path = await bot.download_media(c_thumb or file.thumbs[0].file_id)

        # Upload compressed video
        await ms.edit("⚠️__**Please wait...**__\n**Uploading...**")

        # Check if the file is a video and send accordingly
        if file_extension.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
            await bot.send_video(
                UID,
                video=Output_Path,
                thumb=ph_path,
                caption="Your video is compressed successfully!\n\n**Done by @Javpostr**",
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n🌨️ **Upload Started....**", ms, time.time())
            )
        else:
            # If it's not a video, send it as a document
            await bot.send_document(
                UID,
                document=Output_Path,
                thumb=ph_path,
                caption="Your file has been processed successfully!\n\n**Done by @Javpostr**",
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n🌨️ **Upload Started....**", ms, time.time())
            )

        await ms.delete()

    except Exception as e:
        print(f"Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__}: {e}")
        await ms.edit(f"⚠️ An error occurred: {e}")

    finally:
        # Cleanup
        shutil.rmtree(f"ffmpeg/{UID}", ignore_errors=True)
        shutil.rmtree(f"encode/{UID}", ignore_errors=True)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

async def CompVideo(bot, query, ffmpegcode, c_thumb, subtitle_file_path):
    UID = query.from_user.id
    ms = await query.message.edit('Pʟᴇᴀsᴇ Wᴀɪᴛ...\n\n**Fᴇᴛᴄʜɪɴɢ Qᴜᴇᴜᴇ 👥**')
    ph_path = None

    try:
        # Check for existing processes
        if os.path.isdir(f'ffmpeg/{UID}') and os.path.isdir(f'encode/{UID}'):
            return await ms.edit("**⚠️ Yᴏᴜ ᴄᴀɴ ᴄᴏᴍᴘʀᴇss ᴏɴʟʏ ᴏɴᴇ ғɪʟᴇ ᴀᴛ ᴀ ᴛɪᴍᴇ\n\nAs ᴛʜɪs ʜᴇʟᴘs ʀᴇᴅᴜᴄᴇ sᴇʀᴠᴇʀ ʟᴏᴀᴅ.**")

        # Fetch video details
        media = query.message.reply_to_message
        file = getattr(media, media.media.value)
        filename = str(file.file_name or f"{UID}_video.mp4")  # Handle no filename case
        file_extension = os.path.splitext(filename)[-1] or ".mp4"
        Download_DIR = f"ffmpeg/{UID}"
        Output_DIR = f"encode/{UID}"
        File_Path = f"{Download_DIR}/{filename}"
        Output_Path = f"{Output_DIR}/{UID}{file_extension}"

        # Start download
        await ms.edit('⚠️__**Please wait...**__\n**Tʀyɪɴɢ Tᴏ Dᴏᴡɴʟᴏᴀᴅɪɴɢ....**')
        os.makedirs(Download_DIR, exist_ok=True)
        os.makedirs(Output_DIR, exist_ok=True)

        dl = await bot.download_media(
            message=file,
            file_name=File_Path,
            progress=progress_for_pyrogram,
            progress_args=("\n⚠️__**Please wait...**__\n\n☃️ **Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ....**", ms, time.time())
        )

        await ms.edit("🗜 **Compressing...**")
        
        # Fixing FFmpeg command syntax and escaping issues
        cmd = f"""ffmpeg -i "{dl}" -vf "subtitles='{subtitle_file_path}',scale=if(gte(iw\\,2)*2\\,iw\\,ceil(iw/2)*2):if(gte(ih\\,2)*2\\,ih\\,ceil(ih/2)*2)" -preset ultrafast -crf 23 -c:v libx264 {ffmpegcode} "{Output_Path}" -y"""
        print(f"Running FFmpeg command: {cmd}")  # Debugging

        # Run FFmpeg with real-time output logging
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            line = await process.stderr.readline()
            if not line:
                break
            print(line.decode().strip())  # Log FFmpeg progress

        # Check process completion
        await process.wait()
        if process.returncode != 0:
            raise Exception("FFmpeg processing failed.")

        # Thumbnail handling
        if file.thumbs or c_thumb:
            ph_path = await bot.download_media(c_thumb or file.thumbs[0].file_id)

        # Upload compressed video
        await ms.edit("⚠️__**Please wait...**__\n**Uploading...**")

        # Check if the file is a video and send accordingly
        if file_extension.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
            await bot.send_video(
                UID,
                video=Output_Path,
                thumb=ph_path,
                caption="Your video is compressed successfully!\n\n**Done by @Javpostr**",
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n🌨️ **Upload Started....**", ms, time.time())
            )
        else:
            # If it's not a video, send it as a document
            await bot.send_document(
                UID,
                document=Output_Path,
                thumb=ph_path,
                caption="Your file has been processed successfully!\n\n**Done by @Javpostr**",
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__\n🌨️ **Upload Started....**", ms, time.time())
            )

        await ms.delete()

    except Exception as e:
        print(f"Error on line {sys.exc_info()[-1].tb_lineno}: {type(e).__name__}: {e}")
        await ms.edit(f"⚠️ An error occurred: {e}")

    finally:
        # Cleanup
        shutil.rmtree(f"ffmpeg/{UID}", ignore_errors=True)
        shutil.rmtree(f"encode/{UID}", ignore_errors=True)
        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)