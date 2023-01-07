Pynux
=====

pynux is a discord bot for connecting pythonanywhere console and use [Bash](https://en.wikipedia.org/wiki/Bash_(Unix_shell)) on discord.

You may have seen bots similar to this one on the Telegram platform. I also decided to make an example similar to them but for the Discord platform.

Due to not having a free VPS, I faced a hosting problem, but the idea came to my mind to use [replit](https://replit.com/) for hosting my bot and to use the [PythonAnyWhere](https://pythonanywhere.com/) terminal service for the terminals of each Discord server.

Another thing that was problematic was that for pythonanywhere free accounts there is a time limit for processing, which means that you can only have 100 seconds of processing in 24 hours, but this problem can be solved by building a server on it. And the processes can be executed as a subprocess, and the problem that it creates is that you cannot use the web socket to communicate between the bot and the host, and in addition, when the requests are handled, the server processing stops, and it is necessary to always send requests to hosts. Requests should be sent so that its processes are executed without interruption.

Despite these problems, I intend to reach my goal and solve the problems on my way.