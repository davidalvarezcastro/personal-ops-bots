START_REPLY = (
    "This bot is ready. Send /help for the list of commands and their syntax."
)

HELP_REPLY = """\
Commands:

/start
  Welcome and confirm the bot is ready.

/help
  Show this command list.

/expense <amount> [<category>] <merchant...>
  Record an expense. Example: /expense 12,50 Mercadona

/income <amount> [<category>] <source...>
  Record income. Example: /income 1800 Salary Company

/balance [<start_date>] [<end_date>]
  Show net and totals by category. Dates are YYYY-MM-DD.
  No dates: current calendar month (Europe/Madrid).
"""
