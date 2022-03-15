import discord
import pyimgur

from constants import TRIE
from tokens import IMGUR_CLIENT_ID


def validate_names(opp_names: list[str]):
    invalid_names = []
    if len(opp_names) == 1 and opp_names[0] == 'test':
        return invalid_names
    print(f'Before: {opp_names} \n{invalid_names}')
    for index, opp_name in enumerate(opp_names):
        if opp_name in TRIE:
            opp_names[index] = TRIE[opp_name]

        else:
            invalid_names.append(opp_names[index])
    print(f'After: {opp_names} {invalid_names}')
    return invalid_names


def get_image_url(message: discord.InteractionMessage):
    imgur_client = pyimgur.Imgur(IMGUR_CLIENT_ID)
    upload = imgur_client.upload_image(url=message.attachments[0].url)
    return upload.link


def get_image_url_cleanup(old_url: str):
    imgur_client = pyimgur.Imgur(IMGUR_CLIENT_ID)
    upload = imgur_client.upload_image(url=old_url)
    return upload.link
