# Telegram Epson Printer Bot

This is a Telegram bot that allows you to print PDF files on your Epson printer remotely. It uses the [Epson Connect SDK](https://www.epsondevelopers.com/api/epson-connect/) and the amazing [API wrapper](https://github.com/logston/epson-connect) made by [Logston](https://github.com/logston), as well as the [python-telegram-bot](https://python-telegram-bot.org/) library.

## Installation

1. Clone this repository
2. Ensure you have [poetry](https://python-poetry.org/) installed
3. Install the dependencies with `poetry install`
4. Customize the `start.sh.example` script with your bot token, chat ID(s, comma separated) and Epson Connect data
5. *Optional:* create a `./keys.txt` file with the PDF access key(s), to be able to open and print password-protected PDFs, one per line; alternatively, users can send the access key as a caption with the PDF file