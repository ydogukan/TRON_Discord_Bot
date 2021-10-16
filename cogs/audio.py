import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio
from pathlib import Path
import datetime as dt
from embeds import get_embed_with_title, get_command_error_embed, main_color

import config
from config import queues
from secrets import AZURE_SPEECH_KEY, AZURE_SPEECH_ENDPOINT
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
import xml.etree.ElementTree as ET


class Audio(commands.Cog):
    global queues

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="list")
    async def _list(self, ctx):
        list_of_filenames = [f"`{file.stem}`" for file in Path(
            r"./audio_files").glob("**/*.mp3")]

        embed = get_embed_with_title(
            ctx, "List of sounds", ", ".join(list_of_filenames))
        await ctx.send(embed=embed)

    async def path_from_filename(self, filename):
        for file in Path(r"./audio_files").glob("**/*.mp3"):
            if filename == file.stem:
                return file.absolute()

    async def add_to_queue(self, ctx, audio_type, path):
        guild_id = ctx.message.guild.id

        if guild_id in queues:
            queues[guild_id].append([audio_type, path])

        else:
            queues[guild_id] = [[audio_type, path]]

        if ctx.guild.voice_client:
            embed = get_embed_with_title(
                ctx, "Audio Queue", f"Added **{audio_type}{' ' + path.stem if audio_type != 'TTS' else ''} **:notes: to the queue.", True)
            await ctx.send(embed=embed)

    async def play_queue(self, ctx):
        global now_playing
        channel = ctx.message.author.voice.channel
        guild_id = ctx.message.guild.id

        embed = get_embed_with_title(
            ctx, "Audio Playback", f"Joining channel `{ctx.message.author.voice.channel}`.")
        await ctx.send(embed=embed)
        voice = await channel.connect()

        while queues[guild_id] != [] and voice.is_connected():
            now_playing = queues[guild_id].pop(0)
            config.now_playing = now_playing

            embed = get_embed_with_title(
                ctx, "Audio Playback", f"Now playing **{now_playing[0]}{' ' +now_playing[1].stem if now_playing[0] != 'TTS' else ''}** :notes:.", True)
            await ctx.send(embed=embed)

            voice.play(FFmpegPCMAudio(now_playing[1]))

            while voice.is_playing() or voice.is_paused():
                await asyncio.sleep(0.2)

            if now_playing[0] == "TTS":
                Path(now_playing[1]).unlink()

        config.now_playing.clear()
        await voice.disconnect()

    @commands.command(pass_context=True)
    async def play(self, ctx, filename):
        if (ctx.author.voice):
            path = await self.path_from_filename(filename)

            if path:
                await self.add_to_queue(ctx, "Audio File", path)

                try:
                    if ctx.guild.voice_client == None:
                        await self.play_queue(ctx)

                except Exception as e:
                    print(e)
                    embed = get_command_error_embed(
                        ctx, "Audio Playback", f"An error occured while trying to play audio.")
                    await ctx.send(embed=embed)

            else:
                embed = get_command_error_embed(
                    ctx, "Audio Playback", f"**{filename}** does not exist in local directory.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Audio Playback", f"You are not in a voice channel.")
            await ctx.send(embed=embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = get_command_error_embed(
                ctx, "Play", f"Please enter an audio file name.\nExample usage: **$play XP**")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def tts(self, ctx, *, arg):
        speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY,
                                     endpoint=AZURE_SPEECH_ENDPOINT)
        speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat["Riff24Khz16BitMonoPcm"])
        synthesizer = SpeechSynthesizer(
            speech_config=speech_config, audio_config=None)

        tree = ET.parse('ssml.xml')
        root = tree.getroot()
        root[0][0].text = arg
        ssml_string = ET.tostring(root, encoding='unicode', method='xml')

        result = synthesizer.speak_ssml_async(ssml_string).get()
        stream = AudioDataStream(result)

        i = 0
        while Path(fr"./azure_{i}.mp3").exists():
            i += 1

        path = Path(fr"./azure_{i}.mp3")
        stream.save_to_wav_file(f"azure_{i}.mp3")

        if (ctx.author.voice):
            await self.add_to_queue(ctx, "TTS", path)

            try:
                if ctx.guild.voice_client == None:
                    await self.play_queue(ctx)

            except Exception as e:
                print(e)
                embed = get_command_error_embed(
                    ctx, "Audio Playback", f"An error occured while trying to play audio.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Audio Playback", f"You are not in a voice channel.")
            await ctx.send(embed=embed)

    @tts.error
    async def tts_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = get_command_error_embed(
                ctx, "TTS", f"Please enter text that you want to be converted into speech.\nExample usage: **$tts Selam, ben Doğukan!**")
            await ctx.send(embed=embed)

    @commands.command(name="queue")
    async def _queue(self, ctx, count=5):
        guild_id = ctx.message.guild.id

        embed = discord.Embed(
            title="Audio Queue",
            color=main_color,
            timestamp=dt.datetime.utcnow()
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        if ctx.voice_client == None:
            embed.add_field(
                name="Now playing :notes:",
                value="No audio files are in the queue.",
                inline=False
            )

        else:
            embed.add_field(
                name="Now playing :notes:",
                value=f"`1-` {now_playing[0]} {'**' + now_playing[1].stem + '**' if now_playing[0] != 'TTS' else ''}",
                inline=False
            )

            if len(queues[guild_id]) >= 1:
                embed.add_field(
                    name="Up next  :track_next:",
                    value="\n".join(
                        f"`{no + 2}-` {audio[0]} {'**' + audio[1].stem + '**' if audio[0] != 'TTS' else ''}" for no, audio in enumerate(queues[guild_id][:count])),
                    inline=False
                )

        await ctx.send(embed=embed)

    @_queue.error
    async def _queue_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = get_command_error_embed(
                ctx, "Queue", f"Please enter the amount of audio files that you want to see in the queue.\nExample usage: **$queue 10**")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        if ctx.voice_client:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice.stop()

        else:
            embed = get_command_error_embed(
                ctx, "Skip", f"No audio file is playing right now.")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        if ctx.voice_client:
            for audio in queues[ctx.message.guild.id]:
                if audio[0] == "TTS":
                    Path(audio[1]).unlink()
            queues[ctx.message.guild.id].clear()
            await ctx.guild.voice_client.disconnect()

        else:
            embed = get_command_error_embed(
                ctx, "Leave", f"No audio file is playing right now.")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        if ctx.guild.voice_client:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

            if voice.is_playing():
                voice.pause()

                embed = get_embed_with_title(
                    ctx, "Audio Playback", f"Audio playback paused.")
                await ctx.send(embed=embed)

            else:
                embed = get_command_error_embed(
                    ctx, "Pause", f"No audio file is playing right now.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Pause", f"No audio file exists in the queue.")
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        if ctx.guild.voice_client:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

            if voice.is_paused():
                voice.resume()

                embed = get_embed_with_title(
                    ctx, "Audio Playback", f"Audio playback resumed.")
                await ctx.send(embed=embed)

            else:
                embed = get_command_error_embed(
                    ctx, "Resume", f"No audio file is playing right now.")
                await ctx.send(embed=embed)

        else:
            embed = get_command_error_embed(
                ctx, "Resume", f"No audio file exists in the queue.")
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Audio(bot))
