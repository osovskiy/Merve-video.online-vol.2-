from aiogram.dispatcher.filters.state import State, StatesGroup

class StoragePlaylist(StatesGroup):
    playlist = State()

class StorageLink(StatesGroup):
    links = State()