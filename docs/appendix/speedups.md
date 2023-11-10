# Speedups/Optimization

Atsume includes speedup dependencies from hikari and aiohttp, and these
can be installed to speed up execution. You can do this by installing 
Atsume with `speedups` along with your database libraries.

```shell
pip install hikari-atsume[mysql,speedups]
```

## uvloop

uvloop is automatically included with speedups on Mac and Linux platforms. It's automatically enabled if 
installed, but you can disable it by setting the `DISABLE_UVLOOP` setting in your `local.py`/`settings.py`.


## Running with Optimization

As recommended in the [hikari docs](https://github.com/hikari-py/hikari#python-optimization-flags), when running your 
bot in production, it's recommended to run with at least first level optimization. You can run an Atsume bot with 
optimization by passing a flag in the run command.

```shell
python manage.py run  # no optimization - this is the default.
python -O manage.py run  # first level optimization - features such as internal assertions will be disabled.
python -OO manage.py run  # second level optimization - more features (including all docstrings) will be removed from the loaded code at runtime.
```

