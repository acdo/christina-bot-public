import asyncio
import logging

import discord
import requests.exceptions
from discord.commands import Option
from discord.ext.pages import Paginator

import mongo_calls
from bot_helpers import *
from cross_package_helpers import *
from tokens import DISCORD_TOKEN, GUILD_IDS

# INITIALIZE
logging.basicConfig(level=logging.INFO)
christina_bot = discord.Bot()


# BOT COMMANDS (must be set up before running bot)
@christina_bot.event
async def on_ready():
    print(f'We have logged in as {christina_bot.user}')


@christina_bot.slash_command(guild_ids=GUILD_IDS, description=DESC_ALIASES)
async def aliases(ctx: discord.ApplicationContext):
    msgs_to_delete = []
    alias_embeds = []
    for alias_list in ALIASES:
        desc = alias_list
        title = alias_list[0]
        embed = discord.Embed(description=desc, title=title)
        embed.set_footer(text='This list will auto-delete in 3 minutes, or you can type \'done\' to manually delete.')
        alias_embeds.append(embed)

    paginator = discord.ext.pages.Paginator(pages=alias_embeds, loop_pages=True)
    paginator_msg = await paginator.respond(ctx.interaction)
    await append_interactions(msgs_to_delete, [paginator_msg])
    author = get_author(ctx)
    done = False
    try:
        msg = await christina_bot.wait_for('message',
                                     check=check_function_factory(author, UserEmbedCommand.ALIASES, msgs_to_delete),
                                     timeout=180)
        await append_interactions(msgs_to_delete, [msg])
        done = True
    except asyncio.TimeoutError:
        time_out = await ctx.respond(f'The aliases command has reached 3 minutes. Related messages will  '
                                     f'be deleted in {DELETE_DELAY} seconds.')
        await append_interactions(msgs_to_delete, [time_out])
    finally:
        await delete_counter_messages(ctx, msgs_to_delete, done)


@christina_bot.slash_command(guild_ids=GUILD_IDS, description=DESC_ADD_BA)
async def add_ba_counter(
        ctx: discord.ApplicationContext,
        opposing_team_comp: Option(str, description=PROMPT_BA_OPP)):
    msgs_to_delete = []
    author = get_author(ctx)

    print(f'Checking if {opposing_team_comp} is valid')
    opp_formatted = opposing_team_comp.strip().lower()
    opp_names = opp_formatted.split()
    invalid_names = validate_names(opp_names)
    if len(invalid_names) > 0:
        await ctx.interaction.user.send(f'For your most recently proposed enemy comp \'{opposing_team_comp}\',\n\n'
                                      f'the following unit name(s) are not supported: \n\n {invalid_names}.\n\n'
                                      f' Please refer to the /aliases command in the Ambition discord if a unit'
                                      f' has multiple possible nicknames.')
        empty_response = await ctx.respond('Sent DM, will delete messages now.')
        await append_interactions(msgs_to_delete, [ctx.interaction, empty_response])
        return await delete_counter_messages(ctx, msgs_to_delete, False, delete_delay=0)

    attach_prompt = await ctx.respond('Please attach the image of the counter comp in your next message.')
    await append_interactions(msgs_to_delete, [ctx.interaction, attach_prompt])
    try:
        comp_to_add = await christina_bot.wait_for('message', check=check_function_factory(author, UserEmbedCommand.ADD,
                                                                                           msgs_to_delete), timeout=60)
        await append_interactions(msgs_to_delete, [comp_to_add])
        img_url = get_image_url(comp_to_add)
        mongo_calls.add_ba_counter(' '.join(opp_names), img_url)
        return await delete_counter_messages(ctx, msgs_to_delete, True)
    except asyncio.TimeoutError:
        time_out = await ctx.respond(f'Timed out waiting for a comp picture. Deleting in {DELETE_DELAY} seconds.')
        await append_interactions(msgs_to_delete, [time_out])
        await delete_counter_messages(ctx, msgs_to_delete, False)
    except requests.exceptions.HTTPError:
        await ctx.interaction.user.send(f'Unfortunately, our image uploads have been rate limited so we cannot complete'
                                        f'your request to add this comp. Please try again in an hour!')
        empty_response = await ctx.respond('Sent DM, will delete messages now.')
        await append_interactions(msgs_to_delete, [empty_response])
        return await delete_counter_messages(ctx, msgs_to_delete, False, delete_delay=0)


@christina_bot.slash_command(guild_ids=GUILD_IDS, description=DESC_GET_BA)
async def get_ba_counters(
        ctx: discord.ApplicationContext,
        opposing_team_comp: Option(str, description=PROMPT_BA_OPP)):
    author = get_author(ctx)
    invalid, counters_or_invalid_names = mongo_calls.get_ba_counters(opposing_team_comp)
    msgs_to_delete = []
    if invalid:
        await ctx.interaction.user.send(f'For your most recently requested enemy comp \'{opposing_team_comp}\',\n\n'
                                        f'the following unit name(s) are not supported: \n\n {counters_or_invalid_names}.\n\n'
                                        f' Please refer to the /aliases command in the Ambition discord if a unit'
                                        f' has multiple possible nicknames.')
        empty_response = await ctx.respond('Sent DM, will delete messages now.')
        await append_interactions(msgs_to_delete, [ctx.interaction, empty_response])
        return await delete_counter_messages(ctx, msgs_to_delete, False, delete_delay=0)

    if len(counters_or_invalid_names) == 0:
        no_counters_interaction = await ctx.respond('There are no counters yet for this comp... '
                                                    '<:pecocry:889942411508342854>')
        await append_interactions(msgs_to_delete, [no_counters_interaction])
        return await delete_counter_messages(ctx, msgs_to_delete)

    embed = create_ba_embed(opposing_team_comp, counters_or_invalid_names)
    embed_msg = await embed.respond(ctx.interaction, ephemeral=False)
    msgs_to_delete.append(embed_msg)

    done = False
    commands_embed = discord.Embed.from_dict(DICT_COMMAND_EMBED)
    while not done:
        try:
            prompt_interaction = await ctx.send(embed=commands_embed)
            await append_interactions(msgs_to_delete, [prompt_interaction])
            msg = await christina_bot.wait_for('message', check=check_function_factory(author, UserEmbedCommand.GET,
                                                                                       msgs_to_delete,
                                                                                       len(counters_or_invalid_names)),
                                               timeout=180)
            await append_interactions(msgs_to_delete, [msg])

            status = await perform_command(msg, ctx, msgs_to_delete, author.name, embed, counters_or_invalid_names,
                                           opposing_team_comp)
            done = status == PerformCommandStatus.DONE
        except asyncio.TimeoutError:
            time_out = await ctx.respond(f'One of the previously sent get commands has timed out. '
                                         f'Timed-out messages will delete in {DELETE_DELAY} seconds.')
            await append_interactions(msgs_to_delete, [time_out])
            await delete_counter_messages(ctx, msgs_to_delete, False)
            done = True


# RUN BOT
christina_bot.run(DISCORD_TOKEN)
