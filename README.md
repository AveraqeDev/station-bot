# Station Bot

You will need Python 3.10 or higher to run Station Bot.

## Running the bot

### Installing dependencies

```sh
# To run the bot:
pip install -r requirements/base.txt
python -m station_bot
```

Use CTRL+C to shut the bot down.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

### Setting up

```sh
pip install -r requirements/dev.txt
```

Copy the `.env.sample` file to `.env` and fill in the values

### Checks

- Run `nox` to run various checks to make sure everything is okay. If all pipelines pass, push the changes up. If not, you'll need to make changes until they all pass.
- If you're unsure how to make a test pass, push the changes, and ask another contributor for help.
- If the `safety` check fails, raise a separate issue.

### Using the database

If you need to create a new table for the database, follow the naming convention set out in the data/static/build.sql file.

The database utility is very simple. Examples below:

```py
# Inserting data (from plugin)
await plugin.bot.d.db.execute("INSERT INTO ... VALUES ...", ...)

# Selecting data (from plugin)
row = await plugin.bot.d.db.try_fetch_record("SELECT user_id, points FROM experience WHERE user_id = ?", ...)
print(row.user_id)
print(row.points)
```

Datetime objects are automatically converted both ways, so fetching a field with a time in it will return a datetime object, and passing a datetime object to `execute` will insert a string timestamp.

```py
import datetime as dt

expires = await plugin.bot.d.db.try_fetch_field("SELECT expires FROM warnings WHERE user_id = ?")
isinstance(expires, dt.datetime) == True
```

Note that any method prefixed with `try_` could return `None`.
