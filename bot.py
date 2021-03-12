import discord
import os
import requests
import config
import datetime
import calendar
import json
import re
import sys
import getopt

client = discord.Client()

DISCORD_LISTEN_CHANNEL = int(os.environ['DISCORD_LISTEN_CHANNEL'])
DISCORD_VOTE_CHANNEL = int(os.environ['DISCORD_VOTE_CHANNEL'])
DISCORD_EMOJI_UPVOTE = int(os.environ['DISCORD_EMOJI_UPVOTE'])
DISCORD_EMOJI_DOWNVOTE = int(os.environ['DISCORD_EMOJI_DOWNVOTE'])
DISCORD_BOT_USER_ID = int(os.environ['DISCORD_BOT_USER_ID'])
UPVOTES_NEEDED = 4
DOWNVOTES_NEEDED = 2
USE_QUEUE = True
SPOTIFY_PLAYLIST = os.environ['SPOTIFY_PLAYLIST']
SPOTIFY_PLAYLIST_NAME = os.environ['SPOTIFY_PLAYLIST_NAME']
SPOTIFY_VOTE_PLAYLIST = os.environ['SPOTIFY_VOTE_PLAYLIST']
SPOTIFY_QUEUE_PLAYLIST = os.environ['SPOTIFY_QUEUE_PLAYLIST']
VERBOSE = False
TRACK_REGEX = re.compile(r"https://open\.spotify\.com/track/(\w+)")

print(sys.argv[1:])

try:
    opts, args = getopt.getopt(
        sys.argv[1:], "", ['testing', 'verbose', 'noqueue', 'upvotes=', 'downvotes='])
    print(opts, args)
except getopt.GetoptError:
    print(
        'Use --testing for testing mode, --verbose for verbose output, --noqueue to use without queue playlist, --upvotes [num] to set upvotes, --downvotes [num] to set downvotes')
    sys.exit(2)
for opt, arg in opts:
    if opt == '--testing':
        print('Testing!')
        DISCORD_LISTEN_CHANNEL = int(os.environ['DISCORD_TEST_LISTEN_CHANNEL'])
        DISCORD_VOTE_CHANNEL = int(os.environ['DISCORD_TEST_VOTE_CHANNEL'])
        SPOTIFY_PLAYLIST = os.environ['SPOTIFY_TEST_PLAYLIST']
        SPOTIFY_VOTE_PLAYLIST = os.environ['SPOTIFY_TEST_VOTE_PLAYLIST']
        SPOTIFY_QUEUE_PLAYLIST = os.environ['SPOTIFY_TEST_QUEUE_PLAYLIST']
        print(DISCORD_LISTEN_CHANNEL, DISCORD_VOTE_CHANNEL,
              SPOTIFY_PLAYLIST, SPOTIFY_VOTE_PLAYLIST, SPOTIFY_QUEUE_PLAYLIST)
    elif opt == '--verbose':
        print('Verbose mode active')
        VERBOSE = True
    elif opt == '--noqueue':
        print('Disabling Queue')
        USE_QUEUE = False
    elif opt == '--upvotes':
        print(opt, arg)
        UPVOTES_NEEDED = int(arg)
    elif opt == '--downvotes':
        print(opt, arg)
        DOWNVOTES_NEEDED = int(arg)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # message must be in correct channel
    if not message.channel.id == DISCORD_LISTEN_CHANNEL:
        verbose_log('Message not processed, wrong channel')
        return
    # message must not be sent by the bot
    if message.author == client.user:
        verbose_log('Message not processed, bot is sender')
        return
    # ping test
    if message.content.startswith('$hello'):
        verbose_log('Message processed as hello')
        await message.channel.send('Hello!')
        return

    verbose_log('Processing message', message)
    track_id = check_for_track(message.content)

    if not track_id:
        verbose_log('No song link detected')
        return

    if not check_track_in_playlist(track_id, SPOTIFY_PLAYLIST):
        await add_song_to_playlist(track_id, SPOTIFY_PLAYLIST)
        await message.channel.send('Added to %s!' % SPOTIFY_PLAYLIST_NAME)

    track_in_db = find_track_in_db(track_id)
    if track_in_db:
        if track_in_db['inPlaylist']:
            verbose_log('Song already a banger')
            return
        elif datetime.datetime.strptime(track_in_db['voteAgain'], '%Y-%m-%d %H:%M:%S.%f') > datetime.datetime.now():
            verbose_log('Song posted too recently')
            return

    verbose_log('Song can be voted on')
    await reset_or_add_track(track_id, track_in_db)
    await send_vote_message(track_id, message)


@client.event
async def on_raw_reaction_add(payload):
    verbose_log('on_raw_reaction_add', payload)
    if payload.channel_id != DISCORD_VOTE_CHANNEL:
        verbose_log('Reaction in wrong channel')
        return

    try:
        message = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        channel = client.get_guild(
            payload.guild_id).get_channel(payload.channel_id)
        user = client.get_user(payload.user_id)
        emoji = payload.emoji.id
        verbose_log(message)
        verbose_log(channel)
        verbose_log(user)
        verbose_log(emoji)
    except:
        verbose_log('Couldn\'t get message')
        return

    track_id = check_for_track(message.content)
    if not track_id:
        verbose_log('No song link detected')
        return

    track_in_db = find_track_in_db(track_id)
    if not track_in_db:
        verbose_log('Song not in database')
        return
    # track must not be in playlist
    if track_in_db['inPlaylist']:
        verbose_log('Song in playlist')
        return
    # track must be votable
    if track_in_db['voteFailed']:
        verbose_log('Song already failed')
        return

    track_in_db = await process_add_vote_for_track(
        track_in_db, emoji, user, payload.user_id, message)

    track_in_db = await handle_threshold_reached(
        track_in_db, channel, message)

    update_track_in_db(track_in_db)


@client.event
async def on_raw_reaction_remove(payload):
    verbose_log('on_raw_reaction_remove', payload)
    if payload.channel_id != DISCORD_VOTE_CHANNEL:
        verbose_log('Reaction in wrong channel')
        return

    try:
        message = await client.get_guild(payload.guild_id).get_channel(payload.channel_id).fetch_message(payload.message_id)
        user = client.get_user(payload.user_id)
        emoji = payload.emoji.id
        verbose_log(message)
        verbose_log(user)
        verbose_log(emoji)
    except:
        verbose_log('Couldn\'t get message')
        return

    track_id = check_for_track(message.content)
    if not track_id:
        verbose_log('No song link detected')
        return

    track_in_db = find_track_in_db(track_id)
    if not track_in_db:
        verbose_log('Song not in database')
        return
    # track must not be in playlist
    if track_in_db['inPlaylist']:
        verbose_log('Song in playlist')
        return
    # track must be votable
    if track_in_db['voteFailed']:
        verbose_log('Song already failed')
        return

    track_in_db = await process_remove_vote_for_track(
        track_in_db, emoji, user, payload.user_id, message)

    update_track_in_db(track_in_db)


def get_access_token():
    verbose_log('Getting token')
    return requests.post('https://accounts.spotify.com/api/token',
                         data={'grant_type': 'refresh_token',
                               'refresh_token': os.environ['SPOTIFY_REFRESH_TOKEN'],
                               'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                               'client_secret': os.environ['SPOTIFY_CLIENT_SECRET']}).json()['access_token']


def check_for_track(message):
    verbose_log('Checking for track in message', message)
    match = TRACK_REGEX.findall(message)
    verbose_log(match)
    try:
        verbose_log(match[0])
        return match[0]
    except IndexError:
        return None


def check_track_in_playlist(track_id, playlist, offset = 0):
    verbose_log('Checking for track in playlist', track_id, playlist)
    access_token = get_access_token()
    track_list_res = requests.get('https://api.spotify.com/v1/playlists/%s/tracks' % playlist,
                                  headers={
                                      'Authorization': 'Bearer ' + access_token},
                                  params={'market': 'US', 'fields': 'items(track(id))', 'offset': offset})
    try:
        track_list = track_list_res.json()['items']
        verbose_log('Song List', track_list)
        if len(track_list) == 0:
            verbose_log('Track list end reached')
            return False
        if len([True for x in track_list if x['track']['id'] == track_id]) > 0:
            verbose_log('Track in playlist already')
            return True
        verbose_log('Track not in playlist, checking next 100')
        return check_track_in_playlist(track_id, playlist, offset + 100)
    except:
        verbose_log('Error checking playlist for track')
        return True


def find_track_index_in_db(track_id):
    verbose_log('Getting index if track already submitted')
    db = get_db()
    try:
        track_index_in_db = next(
            i for i, x in enumerate(db) if x['id'] == track_id)
        verbose_log('Track found', track_index_in_db)
        return track_index_in_db
    except StopIteration:
        verbose_log('Track not found')
        return -1


def find_track_in_db(track_id):
    verbose_log('Checking if track already submitted')
    db = get_db()
    track_index_in_db = find_track_index_in_db(track_id)
    if track_index_in_db == -1:
        return None
    return db[track_index_in_db]


async def reset_or_add_track(track_id, track):
    verbose_log('Reset or Add Track', track)
    db = get_db()
    vote_again = datetime.datetime.now() + datetime.timedelta(days=calendar.monthrange(
        datetime.datetime.now().year, datetime.datetime.now().month)[1])
    if not track:
        verbose_log('Track not found, adding')
        try:
            access_token = get_access_token()
            tempCall = requests.get('https://api.spotify.com/v1/tracks/%s' % track_id,
                                    headers={'Authorization': 'Bearer ' + access_token})
            track_name = tempCall.json()['name']
        except:
            track_name = 'ERROR - Name not found'
            verbose_log('Error getting song name')
        db.append({'id': track_id, 'inPlaylist': False, 'voteFailed': False, 'hasUpvoted': [],
                   'hasDownvoted': [], 'voteAgain': vote_again, 'name': track_name})
        dump_to_db(db)
    else:
        verbose_log('Track found, modifying')
        track['voteAgain'] = vote_again
        track['voteFailed'] = False
        track['hasUpvoted'] = []
        track['hasDownvoted'] = []
        update_track_in_db(track)
    await add_song_to_playlist(track_id, SPOTIFY_QUEUE_PLAYLIST)


async def send_vote_message(track_id, message):
    verbose_log('Sending Vote Message')
    upvote = await message.guild.fetch_emoji(DISCORD_EMOJI_UPVOTE)
    downvote = await message.guild.fetch_emoji(DISCORD_EMOJI_DOWNVOTE)
    verbose_log(upvote, downvote)
    voteMessage = await message.guild.get_channel(DISCORD_VOTE_CHANNEL).send('@here A new song has been added to vote on! Posted is a link to the song. Give it a listen and react to this message with %s if you approve and %s if you disapprove https://open.spotify.com/track/%s' % (upvote, downvote, track_id))
    await voteMessage.add_reaction(upvote)
    await voteMessage.add_reaction(downvote)


async def process_add_vote_for_track(track, emoji, user, user_id, message):
    verbose_log('Processing add vote', emoji, track, user)
    if emoji == DISCORD_EMOJI_UPVOTE:
        verbose_log('Is upvote')
        if user_id != DISCORD_BOT_USER_ID:
            track['hasUpvoted'].append(user_id)
        if user_id in track['hasDownvoted']:
            verbose_log('User had downvoted, removing')
            await remove_reaction(user, DISCORD_EMOJI_DOWNVOTE, message)
    elif emoji == DISCORD_EMOJI_DOWNVOTE:
        verbose_log('Is downvote')
        if user_id != DISCORD_BOT_USER_ID:
            track['hasDownvoted'].append(user_id)
        if user_id in track['hasUpvoted']:
            verbose_log('User had upvoted, removing')
            await remove_reaction(user, DISCORD_EMOJI_UPVOTE, message)
    else:
        await remove_reaction(user, emoji, message)
    return track


async def process_remove_vote_for_track(track, emoji, user, user_id, message):
    verbose_log('Processing remove vote', emoji, track)
    if emoji == DISCORD_EMOJI_UPVOTE:
        verbose_log('Is upvote')
        track['hasUpvoted'].remove(user_id)
    elif emoji == DISCORD_EMOJI_DOWNVOTE:
        verbose_log('Is downvote')
        track['hasDownvoted'].remove(user_id)
    else:
        await remove_reaction(user, emoji, message)
    return track


async def remove_reaction(user, emoji, message):
    verbose_log('Removing reaction', user, emoji, message)
    for reaction in message.reactions:
        if reaction.emoji.id == emoji:
            await reaction.remove(user)


async def handle_threshold_reached(track, channel, message):
    verbose_log('Checking thresholds', track)
    if len(track['hasUpvoted']) >= UPVOTES_NEEDED:
        verbose_log('Upvote threshold reached')
        track['inPlaylist'] = True
        if USE_QUEUE:
            await remove_song_from_playlist(track['id'], SPOTIFY_QUEUE_PLAYLIST)
        add_song = await add_song_to_playlist(track['id'], SPOTIFY_VOTE_PLAYLIST)
        if add_song.status_code == 201:
            await channel.send("{} is a certified banger!".format(track['name']))
        else:
            await channel.send("Couldn't add {} to playlist, sorry...".format(track['name']))
        await message.delete()
    elif len(track['hasDownvoted']) >= DOWNVOTES_NEEDED:
        verbose_log('Downvote threshold reached')
        track['voteFailed'] = True
        if USE_QUEUE:
            await remove_song_from_playlist(track['id'], SPOTIFY_QUEUE_PLAYLIST)
        await channel.send("{} didn't make the cut".format(track['name']))
        await message.delete()
    return track


async def add_song_to_playlist(track_id, playlist):
    verbose_log("Adding song %s to %s" % (track_id, playlist))
    access_token = get_access_token()
    tempcall = requests.post('https://api.spotify.com/v1/playlists/%s/tracks' % playlist,
                                   headers={'Authorization': 'Bearer ' + access_token,
                                            'Content-Type': 'application/json',
                                            'Accept': 'application/json'},
                                   params={'uris': track_uri(track_id)})
    verbose_log(tempcall)
    return tempcall


async def remove_song_from_playlist(track_id, playlist):
    verbose_log("Removing song %s to %s" % (track_id, playlist))
    access_token = get_access_token()
    tempcall = requests.delete('https://api.spotify.com/v1/playlists/%s/tracks' % playlist,
                                     headers={'Authorization': 'Bearer ' + access_token,
                                              'Content-Type': 'application/json',
                                              'Accept': 'application/json'},
                                     json={'tracks': [{'uri': track_uri(track_id)}]})
    verbose_log(tempcall)
    return tempcall


def track_uri(track_id):
    return 'spotify:track:%s' % track_id


def update_track_in_db(track):
    verbose_log('Updating track in DB', track)
    db = get_db()
    track_index_in_db = find_track_index_in_db(track['id'])
    db[track_index_in_db] = track
    dump_to_db(db)


def get_db():
    verbose_log('Getting DB')
    input = open('database.json', 'r')
    db = json.load(input)
    input.close()
    return db


def dump_to_db(db):
    output = json.dumps(db, indent=4, default=str)
    f = open('database.json', 'w')
    f.write(output)
    f.close()


def verbose_log(*str):
    if VERBOSE:
        print(*str)


client.run(os.environ['DISCORD_BOT_TOKEN'])
