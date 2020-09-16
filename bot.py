import discord
import os
import requests
import config
import datetime
import calendar
import json

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$add'):
        songID = message.content[5:]
        playlistID = os.environ['PLAYLIST_ID']
        new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                         data={'grant_type': 'refresh_token', 'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                        'client_id': os.environ['SPOTIFY_CLIENT_ID'], 'client_secret': os.environ['SPOTIFY_SECRET_ID']})
        access_token = new_access_token.json()['access_token']
        tempCall = requests.post('https://api.spotify.com/v1/playlists/%s/tracks' % playlistID,
                                 headers={'Authorization': 'Bearer ' + access_token,
                                          'Content-Type': 'application/json'},
                                 params={'uris': songID})
        await message.channel.send(tempCall.status_code)

    if message.content.startswith('$vote'):
        moveOn = False
        input = open('database.json', 'r')
        db = json.load(input)
        input.close()
        try:
            songID = message.content.split()[1]
        except:
            await message.channel.send('My dude, you forgot to paste in the spotify URI. Nimrod')
            await message.delete()
            return
        if len(songID) != 36:
            await message.channel.send('Thats a malformed URI, my dude. check to make sure you got the right thing and try again')
            await message.delete()
            return
        new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                         data={'grant_type': 'refresh_token',
                                               'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                               'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                               'client_secret': os.environ['SPOTIFY_SECRET_ID']})
        access_token = new_access_token.json()['access_token']
        tempCall = requests.get('https://api.spotify.com/v1/tracks/%s' % songID[14:],
                                headers={'Authorization': 'Bearer ' + access_token})
        songName = tempCall.json()['name']
        songLength = tempCall.json()['duration_ms']
        new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                         data={'grant_type': 'refresh_token',
                                               'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                               'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                               'client_secret': os.environ['SPOTIFY_SECRET_ID']})
        access_token = new_access_token.json()['access_token']
        tempCall = requests.get('https://api.spotify.com/v1/playlists/%s/tracks' % os.environ['MOOSEN_MIX'],
                                headers={'Authorization': 'Bearer ' + access_token},
                                params={'market': 'US'})
        data = tempCall.json()
        if data['next'] == None:
            for i in data['items']:
                if i['track']['name'] == songName and i['track']['duration_ms'] == songLength:
                    moveOn = True
                    if i['added_by']['id'] == 1246216463 and message.author == 'skwid23': #skwid
                        await message.channel.send('Connor just tried to banger his own song. Shame him')
                        await message.delete()
                        return
                    elif i['added_by']['id'] == 1221299653 and message.author == 'Tater_Hater': #Tater
                        await message.channel.send('Nick just tried to banger his own song. Shame him')
                        await message.delete()
                        return
                    elif i['added_by']['id'] == 1260641918 and message.author == 'huntinator7': #Hunt
                        await message.channel.send('Hunter just tried to banger his own song. Shame him')
                        await message.delete()
                        return
                    elif i['added_by']['id'] == 1242077712 and message.author == 'DerKO': #DrKO
                        await message.channel.send('Lane just tried to banger his own song. Shame him')
                        await message.delete()
                        return
                    elif i['added_by']['id'] == 1256538054 and message.author == 'ZTagger1911': #Tag
                        await message.channel.send('Kyle just tried to banger his own song. Shame him')
                        await message.delete()
                        return
                    elif i['added_by']['id'] == 'splatterdodge98' and message.author == 'splatterdodge': #me
                        await message.channel.send('Noah just tried to banger his own song. Shame him')
                        await message.delete()
                        return

        else:
            while True:
                for i in data['items']:
                    if i['track']['name'] == songName and i['track']['duration_ms'] == songLength:
                        moveOn = True
                        if i['added_by']['id'] == 1246216463 and message.author.name == 'skwid23':  # skwid
                            await message.channel.send('Connor just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                        elif i['added_by']['id'] == 1221299653 and message.author.name == 'Tater_Hater':  # Tater
                            await message.channel.send('Nick just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                        elif i['added_by']['id'] == 1260641918 and message.author.name == 'huntinator7':  # hunt
                            await message.channel.send('Hunter just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                        elif i['added_by']['id'] == 1242077712 and message.author.name == 'DerKO':  # DrKO
                            await message.channel.send('Lane just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                        elif i['added_by']['id'] == 1256538054 and message.author.name == 'ZTagger1911':  # Tag
                            await message.channel.send('Kyle just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                        elif i['added_by']['id'] == 'splatterdodge98' and message.author.name == 'splatterdodge':  #me
                            await message.channel.send('Noah just tried to banger his own song. Shame him')
                            await message.delete()
                            return
                if moveOn == True:
                    break
                if data['next'] == None:
                    break
                new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                                 data={'grant_type': 'refresh_token',
                                                       'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                                       'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                                       'client_secret': os.environ['SPOTIFY_SECRET_ID']})
                access_token = new_access_token.json()['access_token']
                tempCall = requests.get(data['next'],
                                        headers={'Authorization': 'Bearer ' + access_token},
                                        )
                data = tempCall.json()
        if moveOn == False:
            await message.channel.send('My dude, that song isnt in Moosen Mix. Add it then try again, punk')
            await message.delete()
            return
        for i in db:
            if i['songID'] == songID:
                    if i['voteAgain'] > datetime.datetime.now():
                        await message.channel.send('I am sorry, but this song has already been nominated recently and needs more time to be nominated again. Thanks for trying!')
                        return
                    elif i['voteAgain'] < datetime.datetime.now():
                        i['voteAgain'] = datetime.datetime.now() + datetime.timedelta(days=calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1])
                        i['upvotes'] = 0
                        i['downvotes'] = 0
                        i['hasUpvoted'] = ""
                        i['hasDownvoted'] = ""
                        new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                                         data={'grant_type': 'refresh_token',
                                                               'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                                               'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                                               'client_secret': os.environ['SPOTIFY_SECRET_ID']})
                        access_token = new_access_token.json()['access_token']
                        tempCall = requests.get('https://api.spotify.com/v1/tracks/%s' % songID[14:],
                                                headers={'Authorization': 'Bearer ' + access_token})
                        link = tempCall.json()['external_urls']['spotify']
                        await message.channel.send('@here A new song has been added to vote on! Posted is a link to the song. Give it a listen and react to this message with :upvote: if you approve and :downvote: if you disapprove ' + link)
                        output = json.dumps(db)
                        f = open('database.json', 'w')
                        f.write(output)
                        f.close()
                        await message.delete()
                        return
                    elif i['inPlaylist'] == True:
                        await message.channel.send('I am sorry, but this song has already been added to the playlist. Thanks for trying!')
                        await message.delete()
                        return
        db.append({'songID': songID, 'upvotes':0, 'downvotes':0, 'inPlaylist': False, 'hasUpvoted':[], 'hasDownvoted':[]})
        new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                         data={'grant_type': 'refresh_token',
                                               'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                               'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                               'client_secret': os.environ['SPOTIFY_SECRET_ID']})
        access_token = new_access_token.json()['access_token']
        tempCall = requests.get('https://api.spotify.com/v1/tracks/%s' % songID[14:],
                                headers={'Authorization': 'Bearer ' + access_token})
        link = tempCall.json()['external_urls']['spotify']
        await message.channel.send('@here A new song has been added to vote on! Posted is a link to the song. Give it a listen and react to this message with :upvote: if you approve and :downvote: if you disapprove ' + link)
        output = json.dumps(db)
        f = open('database.json', 'w')
        f.write(output)
        f.close()
        await message.delete()
        return

@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == 466453653084176384:
        if payload.emoji.id == os.environ['UPVOTE']:
            getGuild = client.get_guild(payload.guild_id)
            getChannel = getGuild.get_channel(payload.channel_id)
            getMessage = await getChannel.fetch_message(payload.message_id)
            votedSong = getMessage.content.split()[36][-22:]
            votedSong = 'spotify:track:' + votedSong
            input = open('database.json', 'r')
            db = json.load(input)
            input.close()
            for i in db:
                if votedSong != i['songID']:
                    continue
                elif i['inPlaylist'] == True:
                    continue
                elif i['downvotes'] > 2:
                    continue
                elif payload.user_id in i['hasDownvoted']:
                    user = getGuild.get_member(payload.user_id)
                    for i in getMessage.reactions:
                        if payload.emoji.id == i.emoji.id:
                            await i.remove(user)
                    continue
                i['upvotes'] = i['upvotes'] + 1
                i['hasUpvoted'].append(payload.user_id)
                if (i['upvotes'] > 3) == True:
                    i['inPlaylist'] = True
                    new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                                     data={'grant_type': 'refresh_token',
                                                           'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                                           'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                                           'client_secret': os.environ['SPOTIFY_SECRET_ID']})
                    access_token = new_access_token.json()['access_token']
                    tempCall = requests.post('https://api.spotify.com/v1/playlists/%s/tracks' % os.environ['BANGERS'],
                                             headers={'Authorization': 'Bearer ' + access_token,
                                                      'Content-Type': 'application/json'},
                                             params={'uris': votedSong})
                    tempCall2 = requests.get('https://api.spotify.com/v1/tracks/%s' % votedSong[14:],
                                            headers={'Authorization': 'Bearer ' + access_token})
                    name = tempCall2.json()['name']
                    if tempCall.status_code == 201:
                        await client.get_guild(payload.guild_id).get_channel(payload.channel_id).send("Woot Woot! " + name + " has been decreed a banger and has been added to the playlist")
                    else:
                        await client.get_guild(payload.guild_id).get_channel(payload.channel_id).send("Well, fuck. " + name + " was supposed to become a banger but spotify borked. Talk to Noah")
                    await getMessage.delete()
                output = json.dumps(db)
                f = open('database.json', 'w')
                f.write(output)
                f.close()
        if payload.emoji.id == os.environ['DOWNVOTE']:
            getGuild = client.get_guild(payload.guild_id)
            getChannel = getGuild.get_channel(payload.channel_id)
            getMessage = await getChannel.fetch_message(payload.message_id)
            votedSong = getMessage.content.split()[36][-22:]
            votedSong = 'spotify:track:' + votedSong
            input = open('database.json', 'r')
            db = json.load(input)
            input.close()
            for i in db:
                if votedSong != i['songID']:
                    continue
                elif i['inPlaylist'] == True:
                    continue
                elif i['downvotes'] > 2:
                    continue
                elif payload.user_id in i['hasUpvoted']:
                    user = getGuild.get_member(payload.user_id)
                    for i in getMessage.reactions:
                        if payload.emoji.id == i.emoji.id:
                            await i.remove(user)
                    continue
                i['downvotes'] = i['downvotes'] + 1
                i['hasDownvoted'].append(payload.user_id)
                if (i['downvotes'] > 2) == True:
                    new_access_token = requests.post('https://accounts.spotify.com/api/token',
                                                     data={'grant_type': 'refresh_token',
                                                           'refresh_token': os.environ['SPOTIFY_REFRESH_ID'],
                                                           'client_id': os.environ['SPOTIFY_CLIENT_ID'],
                                                           'client_secret': os.environ['SPOTIFY_SECRET_ID']})
                    access_token = new_access_token.json()['access_token']
                    tempCall2 = requests.get('https://api.spotify.com/v1/tracks/%s' % votedSong[14:],
                                             headers={'Authorization': 'Bearer ' + access_token})
                    name = tempCall2.json()['name']
                    await getMessage.delete()
                    await client.get_guild(payload.guild_id).get_channel(payload.channel_id).send("Well, poop. The song " + name + " didn't quite make the cut to be a banger. Try again in a month!")
                output = json.dumps(db)
                f = open('database.json', 'w')
                f.write(output)
                f.close()

@client.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id == 466453653084176384:
        if payload.emoji.id == os.environ['UPVOTE']:
            getGuild = client.get_guild(payload.guild_id)
            getChannel = getGuild.get_channel(payload.channel_id)
            getMessage = await getChannel.fetch_message(payload.message_id)
            votedSong = getMessage.content.split()[36][-22:]
            votedSong = 'spotify:track:' + votedSong
            input = open('database.json', 'r')
            db = json.load(input)
            input.close()
            for i in db:
                if votedSong != i['songID']:
                    continue
                elif i['inPlaylist'] == True:
                    continue
                elif i['downvotes'] > 2 == True:
                    continue
                if payload.user_id in i['hasUpvoted']:
                    i['upvotes'] = i['upvotes'] - 1
                    i['hasUpvoted'].remove(payload.user_id)
                output = json.dumps(db)
                f = open('database.json', 'w')
                f.write(output)
                f.close()
        if payload.emoji.id == os.environ['DOWNVOTE']:
            getGuild = client.get_guild(payload.guild_id)
            getChannel = getGuild.get_channel(payload.channel_id)
            getMessage = await getChannel.fetch_message(payload.message_id)
            votedSong = getMessage.content.split()[36][-22:]
            votedSong = 'spotify:track:' + votedSong
            input = open('database.json', 'r')
            db = json.load(input)
            input.close()
            for i in db:
                if votedSong != i['songID']:
                    continue
                elif i['inPlaylist'] == True:
                    continue
                elif i['downvotes'] > 2:
                    continue
                if payload.user_id in i['hasDownvoted']:
                    i['downvotes'] = i['downvotes'] - 1
                    i['hasDownvoted'].remove(payload.user_id)
            output = json.dumps(db)
            f = open('database.json', 'w')
            f.write(output)
            f.close()

client.run(os.environ['BOT_TOKEN'])