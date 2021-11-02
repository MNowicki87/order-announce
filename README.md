# **New order announcer** for *Raspberry Pi*
Relying on Shoper Webhooks and RestAPI

The app uses Flask to creates an endpoint to listen for a webhook sent by Shoper when a new order is sent.
At startup it starts ngrok tunnel (free tier) and fetches the generated public URL, which is then passed to Shoper via RestAPI.
After a webhook is received it validates the Shoper webhook secret and plays a sound.

## General requirements:
- Python 3.x
- venv
- ngrok

## Instalation:
1. Create virtual enviroment: `python3 -m venv venv`
2. Activate the venv: `source venv/bin/activate`
3. Install required Python packages: `pip install -r requirements.txt`
4. Create system service for the script to run at boot:  
  a) create a service config file in `LOCATION`:  
  ```
  
  ```
  
## Plans for further development:
- Play different sound for *order received* and *order paid*
- After the valid webhook is received, some details (e.g. clients name, total amount, etc.) can be announced with TTS
- Show order statistics from past week/month on an external display
