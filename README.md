# Shoper Order announcer for _Raspberry Pi_

_Relies on Shoper Webhooks and RestAPI_

The app uses Flask to creates an endpoint to listen for a webhook sent by Shoper when a new order is sent. At startup,
it starts ngrok tunnel (free tier) and fetches the generated public URL, which is then passed to Shoper via RestAPI.
After a webhook is received it validates the Shoper webhook secret and plays a sound.

## Software requirements:

- Shoper license
- Python >= 3.7
- PIP
- venv
- ngrok
- omxplayer

## Hardware setup :

- **RPi Zero W**
- **_Mini-HDMI_** to _**VGA + 3 mm audio jack**_ adapter
- an **external speaker** connected via a 3 mm jack to the adapter

*The app is developed to work on an RPi Zero W with a speaker connected to HDMI port.  
It should run just as well on any other machine, although some tweaks may be required*

## Shoper app preparation:

1. Set up an admin-group with webapi access and config read/write (webhook.edit) privileges
2. Create an admin account within that group
3. Add a webhook (_webhooks/add_):
    1. **URL:** a dummy url will do - it will be updated when the app starts
    2. **Secret:** will be used by the app to decrypt incoming webhook requests
    3. **Events:** `order.create`, `order.paid`
    4. **Format:** `JSON`

## Raspberry Pi preparation:

1. Set up a headless RPi image with ssh
   enabled [[how-to]](https://dev.to/vorillaz/headless-raspberry-pi-zero-w-setup-3llj)
2. Connect the mini-HDMI adapter and set the audio output to HDMI
3. SSH into the RPi and:
    1. Make sure the audio output is set to HDMI (e.g. `alsamixer`)
    2. Run:
        ```shell
        sudo apt-get update
        sudo apt-get upgrade
        sudo apt install omxplayer
        sudo apt install ngrok
        ```

## Installation:

1. Create virtual environment: `python3 -m venv venv`
2. Activate the venv: `source venv/bin/activate`
3. Install required Python packages: `pip install -r requirements.txt`
4. Create `.env` file in root dir with following variables:

   ```dotenv
   SHOPER_WEBHOOK_SECRET=[webhook secret set in Shoper]
   SHOPER_WEBHOOK_ID=[ID of the utilized webhook] 
   SHOPER_REST_URL=[base url of your shop's rest api (typically: 'https://your-domain.ex/webapi/rest/']
   SHOPER_CLIENT_ID=[Shoper user login -> webapi access with r/w privilages for config]
   SHOPER_CLIENT_SECRET=[Shoper user password]
   ```

5. Create the sound file `order_sound.mp3` to be played when order notification is received.

6. *(optional)* Create system service - autorun after system boot:
    1. create a service config file in `/etc/systemd/system/{my_project}.service`:
       ```
       [Unit]
       Description=Shoper Order Announcer
       After=network.target
    
       [Service]
       ExecStart=/home/pi/order-announce/venv/bin/python3 -u /home/pi/order-announce/app.py
       WorkingDirectory=/home/pi/order-announce
       StandardOutput=inherit
       StandardError=inherit
       Restart=always
       User=pi
    
       [Install]
       WantedBy=multi-user.target
       ```
    2. Run terminal commands:
       ```shell
       sudo systemctl start my_project    
       sudo systemctl status my_project
       ```
    3. If not OK, try tweaking config and:
       ```shell
       sudo systemctl restart my_project
       sudo systemctl status my_project
       ```
    4. If OK - enable the service:
       ```shell
       sudo systemctl enable {my_project}
       ```
    5. Reboot the RPi to verify
       ```shell
       sudo shutdown -r now
       ```

### Plans for further development:

- After the valid webhook is received, some details (e.g. clients name, total amount, etc.) can be announced with TTS
- Show order statistics from past week/month on an external display
