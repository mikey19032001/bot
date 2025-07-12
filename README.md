# Highrise Blackjack Bot

A Python-based bot for playing Blackjack in Highrise, featuring in-bot currency management.

## Features

-   Standard Blackjack gameplay (player vs. dealer).
-   Internal bot balance system for players.
-   Manual deposit process via admin credit.
-   Player-initiated withdrawals processed by the bot (simulated Highrise API).
-   Admin commands to manage player balances.

## Setup

### 1. Administrators

You **must** configure the administrator Highrise Player IDs. Open `blackjack_bot/bot_logic.py` and modify the `ADMIN_PLAYER_IDS` list:

```python
# In blackjack_bot/bot_logic.py
ADMIN_PLAYER_IDS = ["Elio98", "Mikey_2001"] # Replace with actual admin Highrise IDs
```

These administrators are authorized to use the `!admin_credit` command.

### 2. Highrise API Integration (Crucial)

This bot code provides the game logic and command handling. To make it work in Highrise, you need to:

-   **Integrate with the Highrise API:**
    -   Modify `blackjack_bot/highrise_api_client.py` to make real API calls for:
        -   `send_message_to_player()`: Sending messages from the bot to players.
        -   `execute_withdraw_to_highrise()`: Transferring gold from the bot's Highrise account to a player's account for withdrawals.
    -   Create a main loop (e.g., by adapting `main_sim.py` or creating a new `bot_runner.py`) that:
        -   Connects to Highrise.
        -   Listens for player commands (e.g., from room chat or direct messages, depending on Highrise API capabilities).
        -   Passes these commands to `blackjack_bot.bot_logic.handle_command()`.
-   **Bot Account:** The bot will need its own Highrise account that can hold and transfer gold for the withdrawal feature to work.
-   **Authentication:** Securely manage your bot's Highrise API token/credentials.

## Currency Management

-   **Deposits:**
    1.  Players manually transfer gold directly to one of the admin's Highrise accounts (e.g., `Elio98` or `Mikey_2001`).
    2.  The player (or admin) informs the admin of the transfer.
    3.  An authorized admin then uses the `!admin_credit <target_player_id> <amount>` command to add the gold to the player's internal bot balance.
-   **Withdrawals:**
    1.  Players use the `!withdraw <amount>` command.
    2.  The bot checks if the player has sufficient internal balance.
    3.  If yes, the bot (via the `execute_withdraw_to_highrise` function you implement) attempts to transfer the gold from its Highrise account to the player's Highrise account.
    4.  If the Highrise transfer is successful, the amount is deducted from the player's internal bot balance.
-   **Bot Balance:** All bets and payouts for Blackjack games are processed using this internal bot balance.

## Commands

### Player Commands

-   `!info`: Shows the welcome message, rules, and command list.
-   `!balance`: Displays your current gold balance held by the bot.
-   `!play <bet_amount>`: Starts a new game of Blackjack with the specified bet.
-   `!hit`: Take another card during your turn in Blackjack.
-   `!stand`: Keep your current hand and end your turn in Blackjack.
-   `!withdraw <amount>`: Request to withdraw gold from your bot balance to your Highrise account.

### Admin Commands (Only for users in `ADMIN_PLAYER_IDS`)

-   `!admin_credit <target_player_id> <amount>`: Adds the specified amount of gold to the `target_player_id`'s internal bot balance. (Example: `!admin_credit player123 500`)
-   `!botbalance`: Shows the total amount of gold held in custody by the bot across all player balances.

## House Edge & Bot Fees

-   The bot uses standard Blackjack rules, which inherently provide a slight advantage to the house (the bot).
-   Currently, there are no additional commission fees (rakes) taken by the bot on bets or winnings. The bot's "earnings" would come from the natural house edge in Blackjack.

## Running the Bot (Simulation)

You can run a command-line simulation of the bot's logic using:

```bash
python main_sim.py
```
This does not connect to Highrise but tests the command handling, game logic, and balance management.

## Deployment Notes (Placeholder)

-   See the "Deployment (Placeholder)" step in the development plan for general guidance.
-   Key requirements: Python environment, Highrise API integration, a way to keep the bot script running (e.g., on a server).
-   **Data Persistence:** For a production bot, player balances (`_player_bot_balances` in `highrise_api_client.py`) should be stored in a database (e.g., SQLite, PostgreSQL) instead of an in-memory dictionary to prevent data loss on restart. Active game states could also be persisted if desired.

---
This `README.md` provides a good overview. I will now quickly review and add comments to the Python files.
