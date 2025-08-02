# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import contextlib
import traceback
from typing import Union, Optional, TYPE_CHECKING

import disnake
from disnake.ext import commands

import wavelink
from utils.db import DBModel
from utils.music.converters import time_format
from utils.music.errors import NoVoice, NoPlayer, NoSource, NotRequester, NotDJorStaff, \
    GenericError, MissingVoicePerms, DiffVoiceChannel, PoolException
from utils.others import CustomContext

if TYPE_CHECKING:
    from utils.music.models import LavalinkPlayer
    from utils.client import BotCore, BotPool


def can_send_message(
        channel: Union[disnake.TextChannel, disnake.VoiceChannel, disnake.Thread],
        bot: Union[disnake.ClientUser, disnake.Member]
):

    if isinstance(channel, disnake.Thread):
        send_message_perm = channel.parent.permissions_for(channel.guild.me).send_messages_in_threads
    else:
        send_message_perm = channel.permissions_for(channel.guild.me).send_messages

    if not send_message_perm:
        raise GenericError(f"**{bot.mention} não possui permissão de enviar mensagens no canal:** {channel.mention}")

    if not channel.permissions_for(channel.guild.me).embed_links:
        raise GenericError(f"**{bot.mention} não possui permissão de inserir links no canal: {channel.mention}**")

    return True


async def check_requester_channel(ctx: CustomContext):

    error_msg = "**No momento você só pode usar comandos de barra (/) nesse canal!**"

    guild_data = await ctx.bot.get_data(ctx.guild_id, db_name=DBModel.guilds)

    if guild_data['player_controller']["channel"] == str(ctx.channel.id):

        try:
            parent = ctx.channel.parent
        except AttributeError:
            return True

        if isinstance(parent, disnake.ForumChannel):

            if ctx.channel.owner_id == ctx.bot.user.id:

                try:
                    vc = ctx.author.voice.channel
                except AttributeError:
                    raise PoolException()
                if ctx.bot.user.id not in vc.voice_states:
                    raise PoolException()
            else:
                raise PoolException()

        raise GenericError(error_msg, self_delete=True, delete_original=15)

    for bot in ctx.bot.pool.get_guild_bots(ctx.guild_id):

        if bot == ctx.bot:
            continue

        data = await bot.get_data(ctx.guild_id, db_name=DBModel.guilds)

        if data['player_controller']["channel"] == str(ctx.channel.id):
            raise GenericError(error_msg, self_delete=True, delete_original=15)

    return True


def check_forum(inter, bot):

    if not bot.check_bot_forum_post(inter.channel, raise_error=False):

        if inter.channel.owner_id == bot.user.id:
            inter.music_bot = bot
            inter.music_guild = inter.guild
            return True
        else:
            raise PoolException()

def update_attr(inter: Union[disnake.MessageInteraction, disnake.ModalInteraction, disnake.ApplicationCommandInteraction],
                bot: BotCore, guild: disnake.Guild):

    with contextlib.suppress(AttributeError):
        inter.music_bot = bot
        inter.music_guild = guild

    return bot, guild

async def check_pool_bots(inter, only_voiced: bool = False, check_player: bool = True, return_first=False,
                          bypass_prefix=False, bypass_attribute=False):

    if not bypass_attribute:
        try:
            inter.music_bot
            return inter.music_bot, inter.music_guild
        except AttributeError:
            pass

        #if isinstance(inter, disnake.MessageInteraction):
        #    if inter.data.custom_id not in ("favmanager_play_button", "musicplayer_embed_enqueue_track", "musicplayer_embed_forceplay"):
        #        return update_attr(inter.bot, inter.guild)

        if isinstance(inter, disnake.ModalInteraction):
            return update_attr(inter, inter.bot, inter.guild)

    if len((guild_bots:=inter.bot.pool.get_guild_bots(inter.guild_id))) < 2 and inter.guild:
        return update_attr(inter, inter.bot, inter.guild)

    if not inter.guild_id:
        raise GenericError("**This command cannot be used in private messages.**")

    try:
        if inter.bot.user.id in inter.author.voice.channel.voice_states:
            return update_attr(inter, inter.bot, inter.guild)
    except AttributeError:
        pass

    mention_prefixed = False

    user_vc = False

    if isinstance(inter, CustomContext) and not bypass_prefix:

        is_forum = check_forum(inter, inter.bot)

        if is_forum:
            return update_attr(inter, inter.bot, inter.guild)

        if not (mention_prefixed:=inter.message.content.startswith(tuple(inter.bot.pool.bot_mentions))):

            msg_id = f"{inter.guild_id}-{inter.channel.id}-{inter.message.id}"

            try:
                inter.bot.pool.message_ids[msg_id]
            except KeyError:
                inter.bot.pool.message_ids[msg_id] = None
            else:
                def check(ctx, b_id):
                    try:
                        return f"{ctx.guild_id}-{ctx.channel.id}-{ctx.message.id}" == msg_id
                    except AttributeError:
                        return

                inter.bot.dispatch("pool_payload_ready", inter)

                try:
                    ctx, bot_id = await inter.bot.wait_for("pool_dispatch", check=check, timeout=10)
                except asyncio.TimeoutError:
                    raise PoolException()

                if not bot_id or bot_id != inter.bot.user.id:
                    raise PoolException()

                return update_attr(inter, inter.bot, inter.guild)

        else:

            if not check_player and not only_voiced:

                if inter.author.voice:
                    user_vc = True
                else:
                    return update_attr(inter, inter.bot, inter.guild)

            elif not inter.author.voice:

                if return_first:
                    return update_attr(inter, inter.bot, inter.guild)

                raise NoVoice()
            else:
                user_vc = True

            if inter.bot.user.id in inter.author.voice.channel.voice_states:
                return update_attr(inter, inter.bot, inter.guild)

            if only_voiced:
                pass

            elif not inter.guild.me.voice:
                return update_attr(inter, inter.bot, inter.guild)

    free_bot = []

    bot_missing_perms = []

    voice_channels = []

    extra_bots_counter = 0

    bot_in_guild = False

    for bot in sorted(guild_bots, key=lambda b: b.identifier):

        if not bot.bot_ready:
            continue

        if not (guild := bot.get_guild(inter.guild_id)):
            if bot.user.id != inter.bot.user.id:
                extra_bots_counter += 1
            continue

        bot_in_guild = True

        if bot.user.id == inter.bot.user.id and mention_prefixed:
            continue

        if not (author := guild.get_member(inter.author.id)):
            continue

        inter.author = author

        if not author.voice:

            inter.bot.dispatch("pool_dispatch", inter, None)

            if return_first:
                free_bot.append([bot, guild])
                continue

            raise NoVoice()

        else:
            user_vc = True

        if bot.user.id in author.voice.channel.voice_states:

            update_attr(inter, bot, guild)

            if isinstance(inter, CustomContext) and bot.user.id != inter.bot.user.id and not mention_prefixed:
                try:
                    await bot.wait_for(
                        "pool_payload_ready", timeout=10,
                        check=lambda ctx: f"{ctx.guild_id}-{ctx.channel.id}-{ctx.message.id}" == msg_id
                    )
                except asyncio.TimeoutError:
                    pass
                bot.dispatch("pool_dispatch", inter, bot.user.id)
                raise PoolException()

            return bot, guild

        if only_voiced:
            continue

        if not (channel := bot.get_channel(inter.channel.id)):
            continue

        if isinstance(channel, disnake.Thread):
            send_message_perm = channel.parent.permissions_for(channel.guild.me).send_messages_in_threads
        else:
            send_message_perm = channel.permissions_for(channel.guild.me).send_messages

        if not send_message_perm:

            if not guild.me.voice:
                bot_missing_perms.append(bot)

            continue

        if not guild.me.voice:
            free_bot.append([bot, guild])
        else:
            voice_channels.append(guild.me.voice.channel.mention)

    try:
        if not isinstance(inter, CustomContext) and not inter.guild.voice_client:

            if only_voiced:
                inter.bot.dispatch("pool_dispatch", None, None)
                raise NoPlayer()

            inter.bot.dispatch("pool_dispatch", inter, None)

            return update_attr(inter, inter.bot, inter.guild)
    except AttributeError:
        pass

    if free_bot:
        bot, guild = update_attr(inter, *free_bot.pop(0))

        if isinstance(inter, CustomContext) and not mention_prefixed and not bypass_prefix and inter.music_bot.user.id != inter.bot.user.id:
            try:
                await inter.music_bot.wait_for(
                    "pool_payload_ready", timeout=10,
                    check=lambda ctx: f"{ctx.guild_id}-{ctx.channel.id}-{ctx.message.id}" == msg_id
                )
            except asyncio.TimeoutError:
                pass
            bot.dispatch("pool_dispatch", inter, inter.music_bot.user.id, bot=inter.music_bot)
            raise PoolException()

        return bot, guild

    elif check_player:

        inter.bot.dispatch("pool_dispatch", inter, None)

        if return_first:
            return update_attr(inter, inter.bot, inter.guild)

        raise NoPlayer()

    components = []

    if not user_vc:
        raise NoVoice()

    if not bot_in_guild:

        msg = "**Não há bots de música compatíveis no servidor...**"

        if extra_bots_counter:
            msg += f"\n\nVocê terá que adicionar pelo menos um bot compatível clicando no botão abaixo:"
            components = [disnake.ui.Button(custom_id="bot_invite", label=f"Adicionar bot{'s'[:extra_bots_counter^1]}.")]

    else:

        if bot_missing_perms:
            msg = f"**Há bots de música disponíveis no servidor mas estão sem permissão de enviar mensagens no canal <#{inter.channel_id}>**:\n\n" + \
                ", ".join(b.user.mention for b in bot_missing_perms)
        else:
            msg = "**Todos os bots estão em uso no nomento...**\n\n**Você pode conectar em um dos canais abaixo onde há sessões ativas:**\n" + ", ".join(voice_channels)

        if extra_bots_counter:
            if inter.author.guild_permissions.manage_guild:
                msg += "\n\n**Ou se preferir, você pode adicionar mais bots de música no servidor atual clicando no botão abaixo:**"
            else:
                msg += "\n\n**Ou, se preferir, você pode pedir para um administrador/manager do servidor para clicar no botão abaixo " \
                        "para adicionar mais bots de música no servidor atual.**"
            components = [disnake.ui.Button(custom_id="bot_invite", label="Adicione mais bots de música clicando aqui")]

    inter.bot.dispatch("pool_dispatch", inter, None)

    await inter.send(embed=disnake.Embed(description=msg, color=inter.bot.get_color()), components=components)

    raise PoolException()

def has_player(check_node = True):

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player = bot.music.players[inter.guild_id]
        except KeyError:
            raise NoPlayer()

        if check_node and not player.node.is_available:
            raise wavelink.ZeroConnectedNodes()

        return True

    return commands.check(predicate)


def is_dj():

    async def predicate(inter):

        if not await has_perm(inter):
            raise NotDJorStaff()

        return True

    return commands.check(predicate)


def can_send_message_check():

    async def predicate(inter):
        # adaptar pra checkar outros bots

        if not inter.guild:

            if inter.guild_id:
                return True

            raise GenericError("**Este comando deve ser usado em um servidor...**")

        try:
            bot = inter.music_bot
        except:
            bot = inter.bot

        # TODO: tempfix para canal de forum (thread arquivada)
        if isinstance(inter.channel, disnake.PartialMessageable):
            try:
                await inter.response.defer(ephemeral=True)
                inter.channel = await bot.fetch_channel(inter.channel_id)
                thread_kw = {}
                if inter.channel.locked and inter.channel.parent.permissions_for(inter.channel.guild.me).manage_threads:
                    thread_kw.update({"locked": False, "archived": False})
                elif inter.channel.archived and inter.channel.owner_id == bot.user.id:
                    thread_kw["archived"] = False
                if thread_kw:
                    await inter.channel.edit(**thread_kw)
            except:
                pass

        can_send_message(inter.channel, inter.guild.me)
        return True

    return commands.check(predicate)


def is_requester():

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player: LavalinkPlayer = bot.music.players[inter.guild_id]
        except KeyError:
            raise NoPlayer()

        if not player.current:
            raise NoSource()

        if player.current.requester == inter.author.id:
            return True

        try:
            if await has_perm(inter):
                return True

        except NotDJorStaff:
            pass

        raise NotRequester()

    return commands.check(predicate)


def check_voice():

    async def predicate(inter):

        try:
            guild = inter.music_guild
        except AttributeError:
            guild = inter.guild

        try:
            if not inter.author.voice:
                raise NoVoice()
        except AttributeError:
            pass

        if not guild.me.voice:

            perms = inter.author.voice.channel.permissions_for(guild.me)

            if not perms.connect:
                raise MissingVoicePerms(inter.author.voice.channel)

        try:
            if inter.author.id not in guild.me.voice.channel.voice_states:
                raise DiffVoiceChannel()
        except AttributeError:
            pass

        return True

    return commands.check(predicate)


def has_source():

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player = bot.music.players[inter.guild_id]
        except KeyError:
            raise NoPlayer()

        if not player.current:
            raise NoSource()

        return True

    return commands.check(predicate)


def check_queue_loading():

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player = bot.music.players[inter.guild_id]
        except KeyError:
            raise NoPlayer()

        if player.locked:
            raise GenericError("**Não é possível executar essa ação com o processamento da música em andamento "
                               "(por favor aguarde mais alguns segundos e tente novamente).**")

        return True

    return commands.check(predicate)


def check_stage_topic():

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player: LavalinkPlayer = bot.music.players[inter.guild_id]
        except KeyError:
            raise NoPlayer()

        if not player.guild.me.voice:
            raise NoPlayer()

        time_limit = 30 if isinstance(player.guild.me.voice.channel, disnake.VoiceChannel) else 120

        if player.stage_title_event and (time_:=int((disnake.utils.utcnow() - player.start_time).total_seconds())) < time_limit and not (await bot.is_owner(inter.author)):
            raise GenericError(
                f"**Você terá que aguardar {time_format((time_limit - time_) * 1000, use_names=True)} para usar essa função "
                f"com o anúncio automático do palco ativo...**"
            )

        return True

    return commands.check(predicate)

def check_yt_cooldown():

    async def predicate(inter):

        try:
            bot = inter.music_bot
        except AttributeError:
            bot = inter.bot

        try:
            player: LavalinkPlayer = bot.music.players[inter.guild_id]
        except KeyError:
            return True

        if player.current and player.current.info["sourceName"] == "youtube" and (remaining:=(disnake.utils.utcnow() - player.start_time).total_seconds()) < bot.config["YOUTUBE_TRACK_COOLDOWN"]:
            if not await bot.is_owner(inter.author):
                raise GenericError("**{}, você só pode pular a música atual do youtube em {}**.\n"
                                   "-# Isso é uma forma de ajudar a evitar possíveis bloqueios do youtube na reprodução da música".format(inter.author.mention, time_format((bot.config["YOUTUBE_TRACK_COOLDOWN"] - int(remaining))*1000, use_names=True)))

        return True

    return commands.check(predicate)

def user_cooldown(rate: int, per: int):
    def custom_cooldown(inter: disnake.Interaction):
        # if (await inter.bot.is_owner(inter.author)):
        #   return None  # sem cooldown

        return commands.Cooldown(rate, per)

    return custom_cooldown

def get_available_bots_info(pool: BotPool, guild_id: int, member: disnake.Member):

    extra_bot_counter = 0

    available_bots = set()

    voice_channels = set()

    for b in pool.get_guild_bots(guild_id):

        if not b.bot_ready:
            continue

        try:
            p = b.music.players[guild_id]
        except KeyError:
            if not b.get_guild(guild_id):
                extra_bot_counter += 1
                continue
            available_bots.add(b.user.mention)
        else:
            if p.keep_connected or p.restrict_mode or not p.last_channel or not p.last_channel.permissions_for(member).connect:
                continue
            voice_channels.add(p.last_channel.mention)

    txts = []

    components = []

    if available_bots:
        txts.append(f"Você pode usar outro{(s:='s'[:(abcount:=len(available_bots))^1])} bot{s} de música disponíve{'is'[:abcount^1] or 'l'} no servidor para usar em outro canal de voz: " + " ".join(available_bots))
    else:
        t = ""
        if voice_channels:
            t += f"Você pode se juntar em um dos canais com sessões ativas no servidor: " + " ".join(voice_channels)
        if extra_bot_counter:
            t += "\n\n" + ("Ou se preferir, você pode" if t else "Você pode")
            if not member.guild_permissions.manage_guild:
                t += "solicitar para um administrador do server "
            t += "adicionar mais bots de música clicando no botão abaixo."

            components = [disnake.ui.Button(custom_id="bot_invite", label="Adicione mais bots de música clicando aqui")]

        if t:
            txts.append(t)

    return "\n\n".join(txts), components




#######################################################################

async def check_player_perm(inter, bot: BotCore, channel, guild_data: dict = None):

    try:
        guild_id = inter.guild_id
    except AttributeError:
        guild_id = inter.guild.id

    try:
        player: LavalinkPlayer = bot.music.players[guild_id]
    except KeyError:
        return True

    try:
        vc = player.guild.me.voice.channel
    except AttributeError:
        vc = player.last_channel

    if not isinstance(inter.guild, disnake.Guild):
        inter.author = player.guild.get_member(inter.author.id)

    if inter.author.guild_permissions.manage_channels:
        return True

    if player.keep_connected:

        txt, components = get_available_bots_info(bot.pool, player.guild_id, inter.author)

        raise GenericError("Apenas membros com a permissão de **gerenciar canais** "
                           f"podem usar esse comando/botão com o **modo 24/7 ativo** no canal <#{player.channel_id}>...\n\n" + txt, components=components)

    if inter.author.id == player.player_creator or inter.author.id in player.dj:
        return True

    try:
        if vc.permissions_for(inter.author).move_members:
            return True
    except AttributeError:
        pass

    user_roles = [r.id for r in inter.author.roles]

    if not guild_data:
        guild_data = await bot.get_data(inter.guild_id, db_name=DBModel.guilds)

    if [r for r in guild_data['djroles'] if int(r) in user_roles]:
        return True

    if player.restrict_mode:

        txt, components = get_available_bots_info(bot.pool, player.guild_id, inter.author)

        raise GenericError("Apenas DJ's ou membros com a permissão de **mover membros** "
                           "podem usar este comando/botão com o **modo restrito ativo**...\n\n" + txt, components=components)

    if not vc and inter.author.voice:
        player.dj.add(inter.author.id)

    elif not [m for m in vc.members if not m.bot and (vc.permissions_for(m).move_members or (m.id in player.dj) or m.id == player.player_creator)]:
        player.dj.add(inter.author.id)
        await channel.send(embed=disnake.Embed(
            description=f"{inter.author.mention} foi adicionado à lista de DJ's por não haver um no canal <#{vc.id}>.",
            color=player.bot.get_color()), delete_after=10)

    return True


async def has_perm(inter):

    try:
        bot = inter.music_bot
        channel = bot.get_channel(inter.channel.id)
    except AttributeError:
        bot = inter.bot
        channel = inter.channel

    await check_player_perm(inter=inter, bot=bot, channel=channel)

    return True

def check_channel_limit(member: disnake.Member, channel: Union[disnake.VoiceChannel, disnake.StageChannel]):

    if not channel.user_limit:
        return True

    if member.guild_permissions.move_members:
        return True

    if member.id in channel.voice_states:
        return True

    if (channel.user_limit - len(channel.voice_states)) > 0:
        return True

def can_connect(
        channel: Union[disnake.VoiceChannel, disnake.StageChannel],
        guild: disnake.Guild,
        check_other_bots_in_vc: bool = False,
        bot: Optional[BotCore] = None
):

    perms = channel.permissions_for(guild.me)

    if not perms.connect:
        raise GenericError(f"**Não tenho permissão para conectar no canal {channel.mention}**")

    if not isinstance(channel, disnake.StageChannel):

        if not perms.speak:
            raise GenericError(f"**Não tenho permissão para falar no canal {channel.mention}**")

        if not guild.voice_client and not check_channel_limit(guild.me, channel):
            raise GenericError(f"**O canal {channel.mention} está lotado!**")

    if bot:
        for b in bot.pool.get_guild_bots(channel.guild.id):
            if b == bot:
                continue
            if b.bot_ready and b.user.id in channel.voice_states:
                raise PoolException()
                #raise GenericError(f"**Já há um bot conectado no canal {channel.mention}\n"
                #                   f"Bot:** {b.user.mention}")

    if check_other_bots_in_vc and any(m for m in channel.members if m.bot and m.id != guild.me.id):
        raise GenericError(f"**Há outro bot conectado no canal:** <#{channel.id}>")

async def check_deafen(me: disnake.Member = None):

    if me.voice.deaf:
        return True
    elif me.guild_permissions.deafen_members:
        try:
            await me.edit(deafen=True)
            return True
        except:
            traceback.print_exc()