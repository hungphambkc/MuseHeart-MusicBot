# MuseHeart-MusicBot
## Music bot programmed in Python with an interactive player, slash and forward commands, integration with [last.fm](https://www.last.fm/), and much more.

## Page with invites and some information/screenshots about Muse Heart and how this source works: [click here](https://gist.github.com/zRitsu/4875008554a00c3c372b2df6dcdf437f#file-muse_heart_invites-md).

[![](https://discordapp.com/api/guilds/911370624507707483/embed.png?style=banner2)](https://discord.gg/KM3NS7D6Zj)

### Some Previews:

- Player controller: normal/mini-player mode (skin: default) and RPC (Rich Presence) support](https://github.com/zRitsu/MuseHeart-MusicBot-RPC-app)

[![](https://i.ibb.co/6tVbfFH/image.png)](https://i.ibb.co/6tVbfFH/image.png)

<details>
<summary>
More previews:
</summary>
<br>

- Slash commands Commands

[![](https://i.ibb.co/nmhYWrK/muse-heart-slashcommands.png)](https://i.ibb.co/nmhYWrK/muse-heart-slashcommands.png)

- Integration with [last.fm](https://www.last.fm/) for scrobbles (other features coming soon).

[![](https://i.ibb.co/SXm608z/muse-heart-lastfm.png)](https://i.ibb.co/SXm608z/muse-heart-lastfm.png)

- Player controller: Fixed/extended mode with song request channel and conversation (skin: default), configurable with the command: /setup

[![](https://i.ibb.co/5cZ7JGs/image.png)](https://i.ibb.co/5cZ7JGs/image.png)

- Player controller: Fixed/extended mode with song request channel in forum with support for automatic status in the voice channel and Stage

[![](https://i.ibb.co/9Hm5cyG/playercontrollerforum.png)](https://i.ibb.co/9Hm5cyG/playercontrollerforum.png)

* There are several other skins; see them all using the /change_skin command (you can also create your own. Use the default templates in the [skins](utils/music/skins/) folder as a reference, create a copy with a different name, and modify it to your liking).

</details>

## Test it right now by creating/reusing your own bot with this source by deploying it to one of the services below:

---

<details>
<summary>
Repl.it
</summary>

Link to the guide with images: https://gist.github.com/zRitsu/70737984cbe163f890dae05a80a3ddbe
</details>

---

<details>
<summary>
Render.com
</summary>
<br>

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/zRitsu/MuseHeart-MusicBot/tree/main)

* **[ 1 ]** - In the field **TOKEN_BOT_1** enter the bot token **( [tutorial on how to obtain](https://www.youtube.com/watch?v=lfdmZQySTXE) )**. `Note: If you wish, in the TOKEN field you can include tokens from more bots to have additional bots to activate multi-voice support by including more tokens in the value (separating with spaces).`

* **[ 2 ]** - In the **DEFAULT_PREFIX** field, enter a prefix for the bot.

* **[ 3 ]** - In the **SPOTIFY_CLIENT_ID** and **SPOTIFY_CLIENT_SECRET** fields, enter your Spotify keys **( [tutorial on how to obtain](https://www.youtube.com/watch?v=ceKQjWiCyWE) )**.

* **[ 4 ]** - In the **MONGO** field, enter the link to your MongoDB database **( [tutorial on how to obtain](https://www.youtube.com/watch?v=x1Gq5beRx9k) )**.

* **[ 5 ]** - Click Apply and wait for the build process until the bot starts (this can take a long time, at least 13 minutes or more for the deployment to complete + the bot to start + the lavalink server to start). </details>

---

<details>
<summary>
Gitpod
</summary>
<br>

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/zRitsu/MuseHeart-MusicBot)

* **[ 1 ]** - Open the .env file and enter the bot's token in the appropriate field (if you don't have it, see how to get it with this tutorial [tutorial](https://www.youtube.com/watch?v=lfdmZQySTXE) on how to get it). I also highly recommend using MongoDB. Look for MONGO= in the .env file and insert the link to your MongoDB database (if you don't have it, see how to get it in this tutorial) (https://www.youtube.com/watch?v=x1Gq5beRx9k).

* **[ 2 ]** - Right-click on the main.py file and then click: Run Python File in Terminal.

* **Note 1:** Requires account verification by cell phone number.
* **Note 2:** Don't forget to go to the [workspaces](https://gitpod.io/workspaces) list and click on the 3 dots for the project, then click **pin**. (This will prevent the workspace from being deleted after 14 days of inactivity.)
* **Note 3:** Do not use GitPod to host/maintain the bot online, as it has significant limitations on the free plan (more information [at this link](https://www.gitpod.io/pricing)).
</details>

---

<details>
<summary>
Hosting on your own PC/VPS (Windows/Linux)
</summary>
<br>

### Requirements:

* Python 3.9, 3.10, or 3.11<br/>
[Download from the Microsoft Store](https://apps.microsoft.com/store/detail/9PJPW5LDXLZ5?hl=pt-br&gl=BR) (Recommended for Windows 10/11 users).<br/>
[Download directly from the official website](https://www.python.org/downloads/release/python-3117/) (Check this option when installing: **Add python to the PATH**)
* [Git](https://git-scm.com/downloads) (Do not choose the portable version)</br>

* [JDK 17](https://www.azul.com/downloads) or higher (Windows and Linux do not need to be installed; it is downloaded automatically)</br>

`Note: This source code requires at least 512MB of RAM AND 1GHz CPU to run normally (if you run Lavalink in the same instance as the bot, assuming the bot is private).

### Start the bot (quick guide):

* Download this source as a zip file (https://github.com/zRitsu/MuseHeart-MusicBot/archive/refs/heads/main.zip) and extract it (or use the command below in the terminal/cmd and then open the folder):
```shell
git clone https://github.com/zRitsu/MuseHeart-MusicBot.git
```
* Double-click the source_setup.sh file (or just setup if your Windows isn't displaying file extensions) and wait.
```If you're using Linux, use the command in the terminal:`
```shell
bash source_setup.sh
```
* A file named **.env** will appear. Edit it and enter the bot's token in the field. appropriate (you can also edit other things in this same file if you want to make specific adjustments to the bot).</br>
`Note: If you haven't created a bot account,` [see this tutorial](https://www.youtube.com/watch?v=lfdmZQySTXE) `to create your bot and obtain the necessary token.`</br>`I also highly recommend using mongodb, look for MONGO= in the .env file and place the link to your mongodb database there (if you don't have it, see how to obtain it in this` [tutorial](https://www.youtube.com/watch?v=x1Gq5beRx9k)`). `
* Now, just open the source_start_win.bat file to start the bot if your system is Windows. If it's Linux, double-click start.sh (or, if you prefer, run the bot using the command below):
```shell
bash source_start.sh
```

### Notes:

* To update your bot, double-click update.sh (Windows). For Linux, use the command in the shell/terminal:
```shell
bash source_update.sh
```
`When updating, there's a chance that any manual changes you made will be lost (if it's not a fork of this source)...`<br/>

`Note: If you're running the source directly from a Windows machine (and have Git installed), just double-click the source_update.sh file.`
</details>

---

Note: There are some more guides in [wiki](https://github.com/zRitsu/MuseHeart-MusicBot/wiki).

### Important Notes:

* You can use this source as an alternative to self-hosting my main bot (Muse Heart) to host/run your own music bot for private use or on public servers you manage (provided you have permission to add your own bot to the server). However, I do not recommend distributing the bot using this source publicly as it is not optimized enough to handle high server demand. However, if you still decide to do so, the bot must be under the [license](/LICENSE) of the original source, and depending on where the bot is being promoted (e.g., botlists), your bot may be flagged for using this source.

* I recommend using the current source without any changes to the code. If you want to make modifications (and especially add new features), it is highly recommended that you have knowledge of Python, Disney, Lavalink, etc. And if you want to keep your modified source updated regularly using the base source, I also recommend having knowledge of Git (at least enough to perform a merge without errors).

* Support will not be provided if you modify the current source (except for custom skins), as I update it frequently, and modified versions tend to become outdated, making it difficult to provide support. Furthermore, depending on the modification or implementation, it may generate unknown errors that make it difficult to resolve the issue, and I may require you to use methods to update the code, which usually undoes these changes.

* If you want to post a video/tutorial using this source, you are completely free to use it for that purpose as long as you comply with the terms mentioned in the paragraphs above.

---

### If you have any problems, please post an [issue](https://github.com/zRitsu/MuseHeart-MusicBot/issues) detailing the problem.

## Special thanks and credits:

* [DisnakeDev](https://github.com/DisnakeDev) (disnake) and Rapptz for the original [discord.py](https://github.com/Rapptz/discord.py)
* [Pythonista Guild](https://github.com/PythonistaGuild) (wavelink)
* [Lavalink-Devs](https://github.com/lavalink-devs) (lavalink and lavaplayer)
* [DarrenOfficial](https://lavalink-list.darrennathanael.com/) Lavalink serverlist (Users who have published their lavalink servers are listed in the about command along with website/link).
* And to all the members who helped me a lot with bug reports (both in [issues](https://github.com/zRitsu/MuseHeart-MusicBot/issues) and on the discord server).
* Other attributions can be found in the [dependency graph](https://github.com/zRitsu/MuseHeart-MusicBot/network/dependencies)