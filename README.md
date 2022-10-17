# instant-checkin-cli
##### Written by [Amado Tejada](https://www.linkedin.com/in/amadotejada/)
##

*instant-checkin-cli* is a companion CLI tool for [instant-checkin](https://github.com/amadotejada/instant-checkin) 

*instant-checkin-cli* allows you to force remote computers to check-in to Jamf MDM via the terminal

<br/>
 <img src="./screenshots/1080_4.gif" width="100%">

## Requirements
-  python 3.6+
- `pip install -r requirements.txt`
- [unopass](https://github.com/amadotejada/unopass) configured with your API credentials
- [instant-checkin](https://github.com/amadotejada/instant-checkin) configured

## Jamf API
*instant-checkin-cli* uses [unopass](https://github.com/amadotejada/unopass) to retrieve your Jamf API credentials at runtime. Set them up in your 1Password account.

Create a Jamf standard user with the minimum permissions to use *instant-checkin-cli*

- Permissions
    * Computers: Read, Update
    * Users: Update

Upload your API credentials to 1Password to use it with unopass

<img src="./screenshots/jamfapi.png" width="100%">

## Usage

1. add an alias shortcut to your shell:
    - E.g `alias ici="python3 instant-checkin-cli.py"`

2. use the shortcut:
    - `ici`

3. [unopass](https://github.com/amadotejada/unopass) will retrieve your Jamf API credentials

<img src="./screenshots/unopass.png" width="100%">

4. Enter the username of the user you want to check-in

<img src="./screenshots/prompt.png" width="100%">


5. A list of computers for that  user will be displayed - Select one

<img src="./screenshots/results.png" width="100%">

6. Profit - Profile will be sent to computer instantly for immediate check-in

<img src="./screenshots/done.png" width="100%">

## Other
When users are not found in Jamf

<img src="./screenshots/notfound.png" width="100%">

When users are not ready for Instant Check-in

<img src="./screenshots/notready.png" width="100%">

Workflow

<img src="./screenshots/workflow.svg" width="100%">

##
### License

*instant-checkin-cli* is released under the [MIT License](https://github.com/amadotejada/instant-checkin-cli/blob/main/LICENSE)
