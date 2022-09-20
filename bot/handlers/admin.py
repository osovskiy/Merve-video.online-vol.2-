import os
from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards import start_kb
from loader import ADMIN
from loader import dp, bot
from states import StoragePlaylist, StorageLink, VideoStorage, BillStorage
from functions import get_videos, get_playlist, summary, bill, chek_bill, get_read_video, delete_videos
from keyboards import start_kb_admin, back_kb, yes_no
from client_bot.main import main
# Ответ на команду админ


@dp.message_handler(commands=["admin"], state=None)
async def admin_start(message: types.Message):
    if str(message.from_user.id) in ADMIN:  # проверка на админа
        await bot.send_message(message.from_user.id, "Hi admin!", reply_markup=start_kb_admin())
    else:
        await bot.send_message(message.from_user.id, "I don't understand what you mean, use the command /start",
                               reply_markup=start_kb())


@dp.message_handler(text="Merge playlist[Admin]", state=None)
async def playlist(message: types.Message):
    if str(message.from_user.id) in ADMIN:
        await bot.send_message(message.from_user.id, "Send me links to playlists that need to be merge.\n\
Each link must be on a new line", reply_markup=back_kb())
        await StoragePlaylist.playlist.set()


@dp.message_handler(state=[StoragePlaylist.playlist, VideoStorage])
async def input_playlist(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMIN:
        async with state.proxy() as data:
            data["playlist"] = message.text.split('\n')
            pl = data["playlist"]
        try:
            await bot.send_message(message.chat.id, "Playlist received.\nStarting processing...")
            video = await get_playlist(pl)
            len_v = len(video["videos"])
            size_v = video["size"]
            await state.finish()
            await VideoStorage.price.set()
            await VideoStorage.user_id.set()
            await VideoStorage.videos.set()
            async with state.proxy() as data:
                data["user_id"] = message.chat.id
                data["videos"] = video["videos"]
            await bot.send_message(message.chat.id, f"""
You want to edit <b>{len_v} video.</b>\n\
Total weight: <b>{int(size_v)} MB.</b>\n\
Want to pay and continue?""", reply_markup=yes_no())
        except Exception as ex:
            await bot.send_message(message.chat.id, "You didn't send a playlist.", reply_markup=start_kb())
            print(ex)
            await state.finish()


@dp.message_handler(text="Merge links[Admin]", state=None)
async def links_read(message: types.Message):
    if str(message.from_user.id) in ADMIN:
        await bot.send_message(message.chat.id, "Send me links to videos that need to be merge.\n\
Each link must be on a new line\nFor example:\nhttps://youtube.com/video1\nhttps://youtube.com/video2",
                               reply_markup=back_kb())
        await StorageLink.links.set()

# Download and process video


@dp.message_handler(state=[StorageLink.links, VideoStorage])
async def input_links(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMIN:
        async with state.proxy() as data:
            data['links'] = message.text.split('\n')
            links = data["links"]
        if len(links) < 2:
            await bot.send_message(message.chat.id, "You can merge at least two videos.", reply_markup=start_kb())
            await state.finish()
        else:
            try:
                await bot.send_message(message.chat.id, "Videos received.\nStarting processing...", reply_markup=start_kb())
                videos = await get_videos(links)
                video = videos["videos"]

                len_v = len(video)
                size_v = videos["size"]
                await VideoStorage.price.set()
                await VideoStorage.user_id.set()
                await VideoStorage.videos.set()
                async with state.proxy() as data:
                    data["user_id"] = message.chat.id
                    data["videos"] = video
                await bot.send_message(message.chat.id, f"""
You want to edit <b>{len_v} video.</b>\n\
Total weight: <b>{int(size_v)} MB.</b>\n\
Want to pay and continue?""", reply_markup=yes_no())
            except Exception as ex:
                await bot.send_message(message.chat.id, "Video processing error", reply_markup=start_kb())
                print(ex)
                await state.finish()


@dp.callback_query_handler(text=["yes", "no"], state=[VideoStorage, BillStorage])
async def pay(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) in ADMIN:
        if callback.data == "no":
            await bot.delete_message(callback.from_user.id, callback.message.message_id - 1)
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            async with state.proxy() as data:
                videos = data["videos"]
            await callback.message.answer("Okey!", reply_markup=start_kb())
            await delete_videos(videos)
            await state.finish()
        else:
            async with state.proxy() as data:
                videos = data["videos"]
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await bot.send_message(callback.from_user.id, "Video paid for!\nStarting processing...\n\
When it's ready, I'll send the video as a reply message\n\
You can write your questions @merge_video_support_bot")
            name = randint(1, 5000)
            await state.finish()
            video = await get_read_video(videos, name)
            await main(video, str(callback.from_user.id))
            os.remove(video)
