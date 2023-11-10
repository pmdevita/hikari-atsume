# Debug Mode

Atsume has two main profiles for running under, a debug mode which is useful for development, 
and a production mode which is useful for production. You can set the current mode in your 
`local.py`/`settings.py` (it's in the `local.py` by default). 

Under debug mode, Atsume:
- Enables automatic reloading when code changes
- Registers commands per-guild rather than globally
- Enables Async debugging

Under production mode, Atsume:
- Registers commands globally based on your `GLOBAL_COMMANDS` setting.

