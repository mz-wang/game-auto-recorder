# game-auto-recorder
Requests op.gg to record games for tracked players when they start a game.

## Getting Started
You will need python3, guaranteed to work with 3.5 but may work with other versions.
Install any required dependencies with pip if you do not have them already (requests, selenium etc.)
Also, download [PhantomJS](http://phantomjs.org/download.html) for your environment and drop the executable into the 'resources' folder of the project. You will have to create this yourself, but just put it inside the root of the project.

## Configuration
1. Create a file with player igns each on its own line. These are the players that the script will look for to start recording. Drop this file in the resources folder.
2. Grab an API key from Riot Games

## Usage
`python3 recorder.py -p <NAME_OF_PLAYERS_LIST_FILE> -k <RIOT_API_KEY>`

## Suggestions
To make the most use of this script, I recommend using it in conjunction with a scheduler like cron or rundeck. Do some simple math and make sure you don't exceed rate limits for Riot's API for a given time period. This script makes 2 requests per player for a single execution.

### Errors
If you run into any errors and can't fix them, make an issue and I will take a look into it. If the error is associated with op.gg or attempting to start the recording, you will see an associated screenshot in the errors folder of the project for the player you were tracking.
