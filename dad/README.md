# Dad Bot

[![Documentation](https://godoc.org/github.com/alecwest/godaddyirc/dadbot?status.svg)](https://godoc.org/github.com/alecwest/godaddyirc/dadbot)

### This bot mimics the behavior of everyone's favorite person... dad.
### Bot uses [hellabot](https://github.com/whyrusleeping/hellabot) as its base.
### Credit for jokes goes to [niceonedad](http://niceonedad.com/) and [r/dadJokes](https://www.reddit.com/r/dadjokes/)

#### FEATURES
- Will respond to most common english forms of the word "dad"
- Succinctly answers any question addressed to him
- Gives witty responses
- Has least favorite kids
- Loves telling jokes\*

#### ADMIN FEATURES
- Dad will say what you want it to, who you want it to
  - Just say "dad, say <target user/channel>: <message>"
  - Without location specified, it speaks to the channel it's connected to
- "Ground/Unground" users so dad won't respond to them

#### PLANNED
- Command to change channels
- Cleanup of dadbot.go overall
- Add dad, help for list of admin commands
- Better way to save config?
- Bring back joke getting scripts
- Respond to "?!" questions
- Attempt reconnect on drop
- Make mom more cynical. ex: "I love mom" -> "Ok"
- Use more \\b in regex
- Listen briefly before speaking to see if any other bots were triggered by the message first, and ignore if one was
- Add a list to track bots
- Track users by name and IP

#### ISSUES
- Ungrounding leaves an empty string behind
- I'm panicking returns 'mmmmmmmmmm no'

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
    - After making sure Dad Bot conf.json is set up to point to the right server and channel, run "go run dad.go" or "go run mom.go"

\* At a limited rate. Dad can only tell so many jokes at one time.
