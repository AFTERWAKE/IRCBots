# New Config Layout

## General changes
- Any config file can be 'imported' using a top-level `"from": [ { "file": "path/to/file" }, ...]`
- Each bot will refer to one json file as the root
- State data will not be stored in the config files, but in a separate location local to where they are run.

## Admin commands
- A common list of admin commands will be created that can be used by all golang bots

## Permissions
- Permissions are a generic list of states that the bot will use to deliberate who can do what
- Permissions will have a `isPermitted` method
- Responses can have a list of permissionsns associated with them, and all must pass.