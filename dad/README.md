# Dad Bot

[![Documentation](https://godoc.org/github.com/AFTERWAKE/IRCBots/dad/dadbot?status.svg)](https://godoc.org/github.com/AFTERWAKE/IRCBots/dad/dadbot)

### This bot mimics the behavior of everyone's favorite person... dad.
### Bot uses [hellabot](https://github.com/whyrusleeping/hellabot) as its base.
### Credit for jokes goes to [niceonedad](http://niceonedad.com/), [r/dadJokes](https://www.reddit.com/r/dadjokes/), and [icanhazdadjoke](https://icanhazdadjoke.com)
### Original nodeJS dadbot can be found [here](https://github.com/alecwest/dadbot_old)

#### FEATURES
- Will respond to most common English forms of the word "dad"
- Succinctly answers any question addressed to him
- Gives witty responses
- Has least favorite kids
- Loves telling jokes\*


#### ADMIN FEATURES
- "Ground/Unground" users so dad won't respond to them
- The following commands accept channel/user targets, but are not required, and in some cases will only work if permissions are granted to the bot. If a channel/user is not given, an attempt will be made to send to the current channel/user.
    - `dad/mom, say <target channel>: <message>` sends a message to the specified channel.
    - `dad/mom, notice <target channel>: <message>` sends a notice to the specified channel.
    - `dad/mom, action <target channel>: <message>` sends an action to the specified channel.
    - `dad/mom, topic <target channel>: <message>` sends a topic change to the specified channel.
    - `dad/mom, chmode <target channel>: <user> +/-<mode(s)>` sends a mode change to a user in a specified channel (see [this](https://wiki.swiftirc.net/wiki/Channel_modes) list of channel modes).
- Remaining admin commands do not allow for the above format, as it is not relevant to them
    - `dad/mom, send <message>` send any command to the IRC in the form "COMMAND <params>".
    - `dad/mom, join <channel>` joins a specified channel.
    - `dad/mom, part <channel> <optional reason>` parts with a specified channel and an optional reason.
    - `dad/mom, quit <optional reason>` quits the IRC with an optional reason.

#### PLANNED
- Add dad, help for list of admin commands
- Bring back reddit joke getting scripts
- Attempt reconnect on drop
- Listen briefly before speaking to see if any other bots were triggered by the message first, and ignore if one was
- Add a list to track bots
- Track users by name and IP

#### ISSUES
- none known

#### CONFIG
- All regex is tested with the case-insensitive flag
- All responses and corresponding regex can be found in conf.json
- If text reuse is needed in a response, put the regex for the part to reuse in the Variable section of the Regex
- If text reuse is not needed, leave everything inside the Trigger regex and the Variable section blank
- Four fill-ins exist for responses:
    - #a -> adds an article "a" or "an" to the existing message
    - #c -> adds a response generated from an action handler
    - #u -> adds the name of the sender
    - #v -> adds the content caught by the Variable regex

#### ADDING COMMANDS
- For the most part, I've made adding responses as easy as possible
- Add the following block of JSON to the config file under the appropriate "Speak" or "AdminSpeak" branch
```json
{
    "Action": "<action_name_or_none>",
    "Regex": {
        "Trigger": "(?i)<regex_for_what_triggers_the_response>",
        "Variable": "<regex_for_text_you_plan_on_manipulating_or_reusing>"
    },
    "Response": [
        {
            "Message": "<your_message_with_any_necessary_fill_ins>",
            "Count": 0,
            "Type": <0-9>
        }
    ]
}
```
- That (?i) is a golang thing for case-insensitive matching (see their [regex syntax](https://golang.org/pkg/regexp/syntax/) for more)
- If no action is required, enter "none"
- If no manipulation or reuse regex is required, leave an empty string for the "Variable" value
- If an action is required, and it's not already defined, then you can pretty easily make and add your own by visiting "actions.go"
- In PerformAction, add a check for your action, and from there you can modify both the captured variable and the target of the Reply with any function you may add.
- Response Type comes from a list of predefined options (that can be expanded as needed). See "models.go" and the list of declared constant "...Type"s for each different kind of response available.

#### SETUP
- Disclaimer: Dad Bot is built and maintained using go version 1.8.1.
- ### Windows
    - Visit https://golang.org/dl/ and download your preferred version of the .msi installer
    - ???
    - Profit
    - Honestly I don't remember / care to figure it out again. It was probably pretty easy though. I mostly did this setup section to have something good on record for the Ubuntu setup
    - Continue to Both systems for the final steps once Go is set up
- ### Linux (Only tested on Ubuntu)
    - Install Go Version Manager for Ubuntu via "bash < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)"
    - Edit ~/.bashrc and source the newly install .gvm directory '[[ -s "$HOME/.gvm/scripts/gvm" ]] && source "$HOME/.gvm/scripts/gvm"'
    - Check to make sure gvm is installed via "gvm version"
    - View all available versions via "gvm listall"
    - You MUST install Go version 1.4 before installing any version above that.
    - gvm install go1.4 -B
    - gvm use go1.4
    - export GOROOT_BOOTSTRAP=$GOROOT
    - gvm install go(desired 1.5+ version)
    - gvm use go(desired 1.5+ version)
    - Continue to Both systems for the final steps once Go is set up
- ### Both systems
    - Once Go is installed, run "go get github.com/alecwest/godaddyirc" and everything should download
    - If on windows, you'll get an additional error about some code in hellabot, which should just need a modification to recon_windows.go (lowercase the HijackSession function)
    - After making sure irc_config.json is set up to point to the right server and dad/mom_config.json is pointing to the right channel, run "go run dad.go" or "go run mom.go"

\* At a limited rate. Dad can only tell so many jokes at one time.
