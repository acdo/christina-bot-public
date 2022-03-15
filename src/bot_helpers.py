import functools
from enum import Enum

import discord
from discord import HTTPException
from discord.ext import commands, pages

from constants import *
from mongo_calls import *
import pyimgur


class UserEmbedCommand(Enum):
    ADD = "add"
    GET = "get"
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    REMOVE_VOTE = "removevote"
    REMOVE_COUNTER = "removecounter"
    ALIASES = "aliases"


class PerformCommandStatus(Enum):
    # Happy cases
    DONE = 1
    UPVOTE = 2
    DOWNVOTE = 3
    REMOVE_VOTE = 4
    REMOVE_COUNTER = 5

    # Unhappy cases
    REPEAT_VOTE = -1
    INVALID_NUMBER = -2
    REMOVE_NONEXISTENT_VOTE = -3


def check_function_factory(user: str, command: UserEmbedCommand, msgs_to_delete: [] = None, num_counters: int = 0):
    def add_check(message: discord.InteractionMessage):
        print('Checking response for add command')
        return message.author == user and len(message.attachments) == 1 and message.attachments[0].content_type.startswith('image')

    def get_remove_check(message: discord.InteractionMessage):
        print('Checking response for remove command')
        msgs_to_delete.append(message)
        return message.author.name == user

    def get_check(message: discord.InteractionMessage):
        print('Checking response for get command')
        return message.author == user and get_ba_counter_message_format_check(message.content, num_counters)

    def aliases_check(message: discord.InteractionMessage):
        print('Checking response for aliases command')
        return message.author == user and message.content.strip().lower() == 'done'

    return get_remove_check if command == UserEmbedCommand.REMOVE_COUNTER \
        else get_check if command == UserEmbedCommand.GET \
        else add_check if command == UserEmbedCommand.ADD \
        else aliases_check


async def perform_command(
        message: discord.InteractionMessage,
        ctx: discord.ApplicationContext,
        messages_to_delete: [],
        user_name: str,
        embed: discord.ext.pages.Paginator,
        counters,
        opponent: str):
    msg = message_tidy(message.content)
    if msg[0] == 'done':
        print('Done command issued, clean up.')
        await delete_counter_messages(ctx, messages_to_delete)
        return PerformCommandStatus.DONE
    else:
        command_enum = UserEmbedCommand(msg[0])
        comp_num = int(msg[1]) - 1  # Need to zero-index this
        if not 0 <= comp_num < len(counters):
            error_interaction = ctx.respond('Please enter a valid comp number (use the page number in the embed)!')
            await append_interactions(messages_to_delete, [error_interaction])
            return PerformCommandStatus.INVALID_NUMBER
        if command_enum == UserEmbedCommand.REMOVE_COUNTER:
            await remove_comp(ctx, comp_num, user_name, embed, counters, messages_to_delete, opponent)
        else:
            await modify_score(ctx, comp_num, command_enum, user_name, embed, counters, messages_to_delete, opponent)


async def remove_comp(
        ctx: discord.ApplicationContext,
        comp_num: int,
        user_name: str,
        embed: discord.ext.pages.Paginator,
        counters,
        messages_to_delete: [],
        opponent: str):
    confirm_interaction = await ctx.respond(
        f'Are you sure you want to delete the counter on page {comp_num + 1}? '
        f'This cannot be undone. Enter \'y\' to confirm or anything else to cancel.')

    confirm_msg = await ctx.bot.wait_for('message',
                                         check=check_function_factory(user_name, UserEmbedCommand.REMOVE_COUNTER,
                                                                      messages_to_delete, len(counters)))
    if confirm_msg.content != 'y':
        cancel_interaction = await ctx.respond(f'Delete command has been cancelled.')
        await append_interactions(messages_to_delete, [confirm_interaction, confirm_msg, cancel_interaction])
        return PerformCommandStatus.REMOVE_COUNTER

    print(f'Removing comp {comp_num}.')
    counter = counters[comp_num]
    is_empty = await modify_database_and_embed(opponent, counter, counters, embed, UserEmbedCommand.REMOVE_COUNTER)
    complete_interaction = await ctx.respond('The specified counter has been deleted!')
    if is_empty:
        empty_interaction = await ctx.respond('You have deleted the last counter! Starting done process now.')
        await append_interactions(messages_to_delete, [empty_interaction])
        await delete_counter_messages(ctx, messages_to_delete)
        return PerformCommandStatus.DONE
    await append_interactions(messages_to_delete, [confirm_interaction, confirm_msg, complete_interaction])
    return PerformCommandStatus.REMOVE_COUNTER


def create_pages(opp: str, counters):
    counter_pages = []
    for counter in counters:
        desc = f"Rating: {counter['Upvotes'] - counter['Downvotes']} (+{counter['Upvotes']} / -{counter['Downvotes']})"
        embed = discord.Embed(title=f'Counters for {opp}', description=desc)
        embed.set_image(url=counter['Image URL'])
        embed.set_footer(text=counter['Timestamp'])
        counter_pages.append(embed)

    return counter_pages


def sort_counters_cmp(item_one, item_two):
    score_one = item_one['Upvotes'] - item_one['Downvotes']
    score_two = item_two['Upvotes'] - item_two['Downvotes']
    if score_one < score_two:
        return -1
    if score_one > score_two:
        return 1

    if item_one['Timestamp'] < item_two['Timestamp']:
        return -1
    if item_one['Timestamp'] > item_two['Timestamp']:
        return 1

    return 0


sort_counters = functools.cmp_to_key(sort_counters_cmp)


def create_ba_embed(opp: str, counters):
    counters.sort(reverse=True, key=sort_counters)
    counter_pages = create_pages(opp, counters)
    return discord.ext.pages.Paginator(pages=counter_pages, loop_pages=True)


def get_author(ctx: discord.ApplicationContext):
    return ctx.interaction.user


def message_tidy(message: str):
    return message.strip().lower().split()


def get_ba_counter_message_format_check(message: str, num_counters: int):
    message_split = message_tidy(message)
    done_check = len(message_split) == 1 and message_split[0] == 'done'
    command_check = (len(message_split) == 2 and any(command.value == message_split[0] for command in UserEmbedCommand)
                     and message_split[1].isdigit()) and num_counters >= int(message_split[1]) > 0
    return done_check or command_check


async def append_interactions(messages_to_delete: [], interactions: []):
    for interaction in interactions:
        # Although we name this interactions, there's a possibility it could be a WebhookMessage
        if type(interaction) == discord.Interaction:
            msg = await interaction.original_message()
            print(f'Adding \"{msg.content}\" to delete list.')
            messages_to_delete.append(msg)
        else:
            print(f'Adding \"{interaction.content}\" to delete list.')
            messages_to_delete.append(interaction)


async def delete_counter_messages(ctx: discord.ApplicationContext, messages: [], successful_run=True, delete_delay=DELETE_DELAY):
    if successful_run:
        # A little less efficient, but easier on the eyes from a coding perspective
        final_interaction = await ctx.respond(
            f'Done! Messages relating to your initial command will now be deleted after {delete_delay} seconds to '
            f'prevent clutter.')
        await append_interactions(messages, [final_interaction])

    print(f'Starting deletes of {[message.content for message in messages]}')
    for msg in messages:
        print(f'Starting delete of \"{msg.content}\"')
        await msg.delete(delay=delete_delay)
        print(f'Delete of \"{msg.content}\" complete!')


def clear_previous_vote(counter, user_name: str, was_upvoted: bool, was_downvoted: bool):
    if was_upvoted:
        counter['Upvoters'].remove(user_name)
        counter['Upvotes'] -= 1
        return True
    elif was_downvoted:
        counter['Downvoters'].remove(user_name)
        counter['Downvotes'] -= 1
        return True

    return False


async def modify_database_and_embed(opponent: str, counter, counters, embed, command_enum):
    print('Score modified, updating database and reordering embed')
    collection = get_opponent_collection(opponent)
    print(f'Collection {collection.name} has been found!')

    if command_enum == UserEmbedCommand.REMOVE_COUNTER:
        result = collection.delete_one({'Image URL': counter['Image URL']})
        counters.remove(counter)
    else:
        result = collection.update_one({'Image URL': counter['Image URL']}, {'$set': counter})

    print(f'Result of database update: {result.raw_result}')
    counters.sort(reverse=True, key=sort_counters)
    resorted_pages = create_pages(opponent, counters)
    if len(resorted_pages) == 0:
        return True
    await embed.update(pages=resorted_pages)
    return False


async def modify_score(
        ctx: discord.ApplicationContext,
        comp_num: int,
        command_enum: UserEmbedCommand,
        user_name: str,
        embed: discord.ext.pages.Paginator,
        counters,
        messages_to_delete: [],
        opponent: str):
    print(f'Order of counters: {counters}')
    counter = counters[comp_num]
    was_already_upvoted = user_name in counter['Upvoters']
    was_already_downvoted = user_name in counter['Downvoters']
    interactions = []

    if command_enum == UserEmbedCommand.REMOVE_VOTE:
        print(f'Removing vote for {counter}')
        if not was_already_upvoted and not was_already_downvoted:
            no_vote_interaction = await ctx.respond('You have no vote on this comp to remove!')
            interactions.append(no_vote_interaction)
            await append_interactions(messages_to_delete, interactions)
            return PerformCommandStatus.REMOVE_NONEXISTENT_VOTE

        modified = clear_previous_vote(counter, user_name, was_already_upvoted, was_already_downvoted)
        if modified:
            await modify_database_and_embed(opponent, counter, counters, embed, command_enum)
        remove_vote_interaction = await ctx.respond('Your vote (if you had one) for this comp has been removed!')
        interactions.append(remove_vote_interaction)
        await append_interactions(messages_to_delete, interactions)
        return PerformCommandStatus.REMOVE_VOTE

    elif command_enum == UserEmbedCommand.UPVOTE and not was_already_upvoted:
        print(f'Upvoting {counter}')
        clear_previous_vote(counter, user_name, was_already_upvoted, was_already_downvoted)
        counter['Upvoters'].append(user_name)
        counter['Upvotes'] += 1
        await modify_database_and_embed(opponent, counter, counters, embed, command_enum)
        upvote_interaction = await ctx.respond('You have upvoted the specified comp!')
        interactions.append(upvote_interaction)
        await append_interactions(messages_to_delete, interactions)
        return PerformCommandStatus.UPVOTE

    elif command_enum == UserEmbedCommand.DOWNVOTE and not was_already_downvoted:
        print(f'Downvoting {counter}')
        clear_previous_vote(counter, user_name, was_already_upvoted, was_already_downvoted)
        counter['Downvoters'].append(user_name)
        counter['Downvotes'] += 1
        await modify_database_and_embed(opponent, counter, counters, embed, command_enum)
        downvote_interaction = await ctx.respond('You have downvoted the specified comp!')
        interactions.append(downvote_interaction)
        await append_interactions(messages_to_delete, interactions)
        return PerformCommandStatus.DOWNVOTE

    else:
        print(f'Duplicate vote for {counter}')
        previous_vote = "upvoted" if command_enum == UserEmbedCommand.UPVOTE else "downvoted"
        already_interaction = await ctx.respond(f'You have already {previous_vote} this comp!')
        interactions.append(already_interaction)
        await append_interactions(messages_to_delete, interactions)
        return PerformCommandStatus.REPEAT_VOTE
