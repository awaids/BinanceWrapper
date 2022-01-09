This is my personal wrapper for the https://python-binance.readthedocs.io/en/latest/.
I use only the asynchronous client provided here and try to wrap all calls using the `events.py:run_until_complete`.
This is only support the binance API.

## Get Binance API Keys
For your account, you need to first get the API key for Binance. To get the API key you need to follow the steps here:

https://www.binance.com/en/support/faq/360002502072

You require both these keys:
1. `API Key`
2. `Secrect Key`

**NOTE:** NEVER share these keys with anyone and/or upload them to gitlab/hub!

## Setup `.env` File
In your current working dir or a parent directory, you need to create an `env` file. You can follow these steps:
1. Create a `.env` file in your current working dir.
2. Store the binance keys as follows:
    ```
    MY_API="{Your API Key}"
    MY_SECRECT="{Your Secrect Key}"
    ````
3. Now you can use the BinanceManager and PortfolioManager

## Quick Start
1. Clone the repo.
2. Install all the pre-requsites:
    ```
    pip install -r requirements.txt
    ```