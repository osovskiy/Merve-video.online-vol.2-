import os
from random import randint


from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from states import StoragePlaylist, StorageLink, VideoStorage, BillStorage
from keyboards import start_kb, back_kb, pay_kb, chek_kb
from functions import get_videos, get_playlist, summary, bill, chek_bill, get_read_video, delete_videos
from client_bot.main import main
from loader import bot, dp


# Response to start command
@dp.message_handler(CommandStart())
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, "Hello!\nI'm a bot for merging videos from YouTube.com\n\
Choose what you would like to do by clicking the button below", reply_markup=start_kb())

# Exiting the state machine


@dp.message_handler(Text(equals='Back', ignore_case=True), state="*")
async def cancel_handlers(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Okey!", reply_markup=start_kb())

# Get a playlist


@dp.message_handler(text="Merge playlist", state=None)
async def playlist(message: types.Message):
    await bot.send_message(message.from_user.id, "Send me links to playlists that need to be merge.\n\
Each link must be on a new line", reply_markup=back_kb())
    await StoragePlaylist.playlist.set()

# Playlist processing


@dp.message_handler(state=[StoragePlaylist.playlist, VideoStorage])
async def input_playlist(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["playlist"] = message.text.split('\n')
        pl = data["playlist"]
    try:
        await bot.send_message(message.chat.id, "Playlist received.\nStarting processing...")
        video = await get_playlist(pl)
        price = await summary(video["size"])
        if price >= 10:  # Protection against spam payments
            len_v = len(video["videos"])
            size_v = video["size"]
            await state.finish()
            await VideoStorage.price.set()
            await VideoStorage.user_id.set()
            await VideoStorage.videos.set()
            async with state.proxy() as data:
                data["price"] = price
                data["user_id"] = message.chat.id
                data["videos"] = video["videos"]
            await bot.send_message(message.chat.id, f"""
You want to edit <b>{len_v} video.</b>\n\
Total weight: <b>{int(size_v)} MB.</b>\n\
Installation cost: <b>{price} RUB</b>\n\
Want to pay and continue?""", reply_markup=pay_kb())
        else:
            await bot.send_message(message.chat.id, "The price of the video is too low", reply_markup=start_kb())
            await delete_videos(video["videos"])
            await state.finish()
    except Exception as ex:
        await bot.send_message(message.chat.id, "You didn't send a playlist.", reply_markup=start_kb())
        print(ex)
        await state.finish()


# Get a link


@dp.message_handler(text="Merge links", state=None)
async def links_read(message: types.Message):
    await bot.send_message(message.chat.id, "Send me links to videos that need to be merge.\n\
Each link must be on a new line\nFor example:\nhttps://youtube.com/video1\nhttps://youtube.com/video2",
                           reply_markup=back_kb())
    await StorageLink.links.set()

# Download and process video


@dp.message_handler(state=[StorageLink.links, VideoStorage])
async def input_links(message: types.Message, state: FSMContext):
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
            price = await summary(videos["size"])
            if price >= 1:  # Spam payment protection
                len_v = len(video)
                size_v = videos["size"]
                await VideoStorage.price.set()
                await VideoStorage.user_id.set()
                await VideoStorage.videos.set()
                async with state.proxy() as data:
                    data["price"] = price
                    data["user_id"] = message.chat.id
                    data["videos"] = video
                await bot.send_message(message.chat.id, f"""
You want to edit <b>{len_v} video.</b>\n\
Total weight: <b>{int(size_v)} MB.</b>\n\
Installation cost: <b>{price} RUB</b>\n\
Want to pay and continue?""", reply_markup=pay_kb())
            else:
                await bot.send_message(message.chat.id, "The price of the video is too low", reply_markup=start_kb())
                await delete_videos(video)
                await state.finish()
        except Exception as ex:
            await bot.send_message(message.chat.id, "Video processing error", reply_markup=start_kb())
            print(ex)
            await state.finish()

# Proof of payment


@dp.callback_query_handler(text=["pay", "no_pay"], state=[VideoStorage, BillStorage])
async def pay(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "no_pay":
        await bot.delete_message(callback.from_user.id, callback.message.message_id - 1)
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        async with state.proxy() as data:
            videos = data["videos"]
        await callback.message.answer("Okey!", reply_markup=start_kb())
        await delete_videos(videos)
        await state.finish()
    else:
        await bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        async with state.proxy() as data:
            price = data["price"]
            id = data["user_id"]
        chek = bill(price, id)
        await BillStorage.bill.set()
        async with state.proxy() as data:
            data["bill"] = chek
        await bot.send_message(callback.from_user.id, f"Your payment link:\n{chek.pay_url}\
\nLink expires: <b>30 minutes.</b>", reply_markup=chek_kb(url=chek.pay_url, bill=chek.bill_id))


# Checking payment status
@dp.callback_query_handler(text_contains="chek_", state=[BillStorage, VideoStorage])
async def chek_pay(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bill = data["bill"]
    chek = chek_bill(bill.bill_id)
    if chek == "PAID":
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

    else:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await bot.send_message(callback.from_user.id, f"Video not paid for!\nYour payment link:\n \
        {bill.pay_url}", reply_markup=chek_kb(False, bill=bill.bill_id))

# Exit and cancel payment


@dp.callback_query_handler(text="quit", state="*")
async def quit(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id, "Okey!", reply_markup=start_kb())
    async with state.proxy() as data:
        videos = data["videos"]
        await delete_videos(videos)

    await state.finish()
