import os
import time
import asyncio
import ffmpeg
import sys
import humanize
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.utils import Compress_Stats, skip, CompressVideo, CompVideo
from helper.database import db
from script import Txt


@Client.on_callback_query()
async def Cb_Handle(bot: Client, query: CallbackQuery):
    data = query.data

    if data == 'help':
        btn = [
            [InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='home')]
        ]
        await query.message.edit(text=Txt.HELP_MSG, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    elif data == 'home':
        btn = [
            [InlineKeyboardButton(text='❗ Hᴇʟᴘ', callback_data='help'), InlineKeyboardButton(
                text='🌨️ Aʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton(text='📢 Uᴘᴅᴀᴛᴇs', url='https://t.me/FILE_SHARINGBOTS'), InlineKeyboardButton(
                text='💻 Dᴇᴠᴇʟᴏᴘᴇʀ', url='https://t.me/rohit_1888')]
        ]
        await query.message.edit(text=Txt.PRIVATE_START_MSG.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(btn))

    elif data == 'about':
        BUTN = [
            [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='home')]
        ]
        botuser = await bot.get_me()
        await query.message.edit(Txt.ABOUT_TXT.format(botuser.username), reply_markup=InlineKeyboardMarkup(BUTN), disable_web_page_preview=True)

    if data.startswith('stats'):
        user_id = data.split('-')[1]
        try:
            await Compress_Stats(e=query, userid=user_id)
        except Exception as e:
            print(e)

    elif data.startswith('skip'):
        user_id = data.split('-')[1]
        try:
            await skip(e=query, userid=user_id)
        except Exception as e:
            print(e)

    elif data == 'option':
        file = getattr(query.message.reply_to_message, query.message.reply_to_message.media.value)
        text = f"""**__What do you want me to do with this file.?__**\n\n**File Name** :- `{file.file_name}`\n\n**File Size** :- `{humanize.naturalsize(file.file_size)}`"""
        buttons = [[InlineKeyboardButton("Rᴇɴᴀᴍᴇ 📝", callback_data=f"rename-{query.from_user.id}")],
                   [InlineKeyboardButton("Cᴏᴍᴘʀᴇss 🗜️", callback_data=f"compress-{query.from_user.id}")]]
        await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == 'setffmpeg':
        try:
            ffmpeg_code = await bot.ask(text=Txt.SEND_FFMPEG_CODE, chat_id=query.from_user.id, filters=filters.text, timeout=60, disable_web_page_preview=True)
        except:
            return await query.message.reply_text("**Eʀʀᴏʀ!!**\n\nRᴇǫᴜᴇsᴛ ᴛɪᴍᴇᴅ ᴏᴜᴛ.\nSᴇᴛ ʙʏ ᴜsɪɴɢ /set_ffmpeg")
        SnowDev = await query.message.reply_text(text="**Setting Your FFMPEG CODE**\n\nPlease Wait...")
        await db.set_ffmpegcode(query.from_user.id, ffmpeg_code.text)
        await SnowDev.edit("✅️ __**Fғᴍᴘᴇɢ Cᴏᴅᴇ Sᴇᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ**__")

    elif data.startswith('compress'):
        user_id = data.split('-')[1]
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        else:
            BTNS = [
                [InlineKeyboardButton(text='480ᴘ', callback_data='480pc'), InlineKeyboardButton(text='720ᴘ', callback_data='720pc')],
                [InlineKeyboardButton(text='1080ᴘ', callback_data='1080pc'), InlineKeyboardButton(text='4ᴋ', callback_data='2160pc')],
                [InlineKeyboardButton(text='Aᴅᴅ Wᴀᴛᴇʀᴍᴀʀᴋ', callback_data='add_watermark')],
                [InlineKeyboardButton(text='Aᴅᴅ Sᴜʙᴛɪᴛʟᴇꜱ', callback_data='add_subtitles')],
                [InlineKeyboardButton(text='Cᴜsᴛᴏᴍ Eɴᴄᴏᴅɪɴɢ 🗜️', callback_data='custompc')],
                [InlineKeyboardButton(text='✘ Cʟᴏꜱᴇ', callback_data='close'), InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
            ]
            await query.message.edit(text='**Select the Compression Method Below 👇 **', reply_markup=InlineKeyboardMarkup(BTNS))

    elif data == '480pc':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg = (
    "-preset veryfast -c:v libx264 "
    "-x265-params \"bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1\" "
    "-pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k "
    "-vf \"scale='if(gt(iw,ih),840,-1)':'if(gt(iw,ih),-1,480)',"
    "drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10\" "
    "-map 0:v -map 0:a -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
)

            await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)
        except Exception as e:
            print(e)

    elif data == '720pc':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg = (
    "-preset veryfast -c:v libx264 "
    "-x265-params \"bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1\" "
    "-pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k "
    "-vf \"scale='if(gt(iw,ih),1280,-1)':'if(gt(iw,ih),-1,720)',"
    "drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10,"
    "scale='if(eq(mod(iw,2),1),iw-1,iw)':'if(eq(mod(ih,2),1),ih-1,ih)'\" "
    "-map 0:v -map 0:a -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
)
            await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)
        except Exception as e:
            print(e)

    elif data == '1080pc':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg = (
    "-preset ultrafast -c:v libx264 "
    "-x265-params \"bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1\" "
    "-pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k "
    "-vf \"scale='if(gt(iw,ih),1920,-1)':'if(gt(iw,ih),-1,1080)',"
    "drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10,"
    "scale='if(eq(mod(iw,2),1),iw-1,iw)':'if(eq(mod(ih,2),1),ih-1,ih)'\" "
    "-map 0:v -map 0:a -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
)
            await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)
        except Exception as e:
            print(e)

    elif data == '2160pc':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg = (
    "-preset ultrafast -c:v libx264 "
    "-x265-params \"bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1\" "
    "-pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k "
    "-vf \"scale='if(gt(iw,ih),3840,-1)':'if(gt(iw,ih),-1,2160)',"
    "drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10\" "
    "-map 0:v -map 0:a -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
)
            await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)
        except Exception as e:
            print(e)

    elif data == 'custompc':
        try:
            c_thumb = await db.get_thumbnail(query.from_user.id)
            ffmpeg_code = await db.get_ffmpegcode(query.from_user.id)
            if ffmpeg_code:
                ffmpeg_code += " -vf \"drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=24:x=10:y=h-th-10\""
                await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)

        except Exception as e:
            print(e)

    elif data == 'add_subtitles':
        try:
        # Ask the user for the subtitle file after video is sent
            await query.message.edit(
                text="Please send the subtitles file in `.srt` format. Ensure the filename and the subtitles match the video's timing.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
                ])
            )

            try:
            # Ask the user for the subtitle file
                subtitle_message = await bot.ask(
                    chat_id=query.from_user.id,
                    text="Please upload your subtitles file in `.srt` format within 30 seconds.",
                    filters=filters.document,
                    timeout=30,
                )

                if subtitle_message.document.file_name.endswith('.srt'):
                # Download the subtitle file
                    subtitle_file_path = await subtitle_message.download()

                # Get the existing video (the file that the user already sent)
                    input_video_path = query.message.reply_to_message.video.file_name
                    c_thumb = await db.get_thumbnail(query.from_user.id)

                # FFmpeg command to add both watermark and subtitles
                    ffmpeg = (
    f"-i {input_video_path} -vf \"subtitles='{subtitle_file_path}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF&',"
    "scale='if(gt(iw,ih),1920,-1)':'if(gt(iw,ih),-1,1080)',"
    "drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:"
    "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10\" "
    "-c:v libx264 -crf 30 -preset veryfast -pix_fmt yuv420p "
    "-c:a libopus -b:a 32k -ac 2 "
    "-metadata:s:s:0 language=eng "
    "-c:s mov_text -map 0:v -map 0:a -map 1:s"
)

                # Call CompVideo function to process the video
                    await CompVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb, subtitle_file_path=subtitle_file_path)

            except asyncio.TimeoutError:
                await query.message.edit(
                    text="Sorry, you took too long to send the files. Please try again.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
                    ])
                )

        except Exception as e:
            await query.message.edit(
                text=f"An error occurred: {str(e)}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
                ])
            )

    elif data == "add_watermark":
        try:
            # Retrieve the custom thumbnail
            c_thumb = await db.get_thumbnail(query.from_user.id)

            # Define FFmpeg command for adding watermark without compression
            ffmpeg = (
    "-preset ultrafast -c:v libx264 -x265-params 'bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1' "
    "-pix_fmt yuv420p -crf 30 -c:a libopus -b:a 32k "
    "-vf \"scale='if(gt(iw,ih),1920,ceil(iw/2)*2)':'if(gt(iw,ih),ceil(ih/2)*2,1080)',drawtext=text='by @Javpostr':fontcolor=white@0.8:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=10:y=h-th-10\" "
    "-map 0:v -map 0:a -ac 2 -ab 32k -vbr 2 -level 3.1 -threads 5"
)

            # Call CompressVideo function but set compress=False to avoid compression
            await CompressVideo(bot=bot, query=query, ffmpegcode=ffmpeg, c_thumb=c_thumb)

        except Exception as e:
            # Print error for debugging
            print(f"Error during add_watermark: {e}")

            await query.message.reply_text(
                "An error occurred while processing your watermark request. Please try again.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text='⟸ Bᴀᴄᴋ', callback_data='option')]
                ])
            )

    elif data == "close":
        user_id = data.split('-')[1]
        if int(user_id) not in [query.from_user.id, 0]:
            return await query.answer(f"⚠️ Hᴇʏ {query.from_user.first_name}\nTʜɪs ɪs ɴᴏᴛ ʏᴏᴜʀ ғɪʟᴇ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴅᴏ ᴀɴʏ ᴏᴘᴇʀᴀᴛɪᴏɴ", show_alert=True)
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()