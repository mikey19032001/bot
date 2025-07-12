from .blackjack_engine import Game
from .highrise_api_client import (
    get_bot_player_balance,
    update_bot_player_balance,
    send_message_to_player,
    execute_withdraw_to_highrise,
    get_total_bot_balance # Assuming this will be added to highrise_api_client.py
)

# In-memory store for active games. Key: player_id, Value: Game object
active_games = {}

# IMPORTANT: Set the Highrise Player IDs of the bot administrators
ADMIN_PLAYER_IDS = ["Elio98", "Mikey_2001"] # List of admin IDs who can use !admin_credit

_raw_info_message = """
**Welcome to Highrise Blackjack Bot!**

**How to Add Gold to Play:**
1. Send the amount of gold you want to use for playing directly to one of the bot admin's Highrise accounts (Elio98 or Mikey_2001).
2. After sending, please notify the admin you sent it to. The admin will then use a command to credit your bot balance.

**Account Commands:**
- `!balance`: Check your current gold balance held by the bot.
- `!withdraw <amount>`: Request to transfer gold from the bot back to your Highrise account.

**Game Commands:**
- `!play <amount>`: Start a new game with your bet amount (uses your bot balance).
- `!hit`: Take another card.
- `!stand`: Keep your current hand and end your turn.
- `!info`: Show this help message.

**Blackjack Rules:**
- The goal is to get a hand value closer to 21 than the dealer, without going over 21.
- Number cards are worth their face value. J, Q, K are worth 10. Aces can be 1 or 11.
- You'll be dealt two cards. The dealer also gets two, one face up, one face down.
- If your first two cards total 21 (Blackjack), you win 1.5x your bet (standard payout).
- 'Hit' to take more cards. If your hand exceeds 21, you 'bust' and lose your bet.
- 'Stand' to keep your hand. The dealer will then reveal their hidden card and play according to house rules (usually hits until 17 or more).
- If the dealer busts, you win. If neither busts, the closest hand to 21 wins.
- If you and the dealer have the same score, it's a 'push' (tie), and your bet is returned to your bot balance.

Good luck!
"""
INFO_MESSAGE = _raw_info_message

ADMIN_INFO_MESSAGE = """
**--- Admin Commands ---**
- `!admin_credit <target_player_id> <amount>`: Manually credit a player's bot balance after confirming a Highrise transfer.
- `!botbalance`: View the total amount of gold held in custody across all player balances.
"""


def _handle_payout_and_cleanup(player_id: str):
    """
    Handles payout after a game concludes and cleans up the game from active_games.
    Uses the game's outcome to determine payout and updates the player's internal bot balance.
    """
    if player_id not in active_games:
        # This should not happen if called correctly after a game.
        # print(f"Debug: _handle_payout_and_cleanup called for {player_id} but no active game found.")
        return

    game = active_games[player_id]

    if game.game_state != Game.GAME_STATE_GAME_OVER:
        # Should ideally not happen if game logic flow is correct
        if game.outcome: # If outcome was set (e.g. player bust), force game over
             game.game_state = Game.GAME_STATE_GAME_OVER
        else:
            send_message_to_player(player_id, "Error: Game outcome not determined before payout.")
            if player_id in active_games: # Fallback cleanup
                del active_games[player_id]
            return

    payout_multiplier = game.get_payout_multiplier()
    amount_to_credit_to_bot_balance = 0
    if payout_multiplier > 0:
        amount_to_credit_to_bot_balance = int(game.bet * payout_multiplier)

    final_outcome_text = game.get_final_outcome_message()

    payout_credited_successfully = True
    if amount_to_credit_to_bot_balance > 0:
        if not update_bot_player_balance(player_id, amount_to_credit_to_bot_balance):
            send_message_to_player(player_id, f"{final_outcome_text} CRITICAL ERROR: Could not credit your winnings of {amount_to_credit_to_bot_balance} gold to your bot balance. Please contact support.")
            payout_credited_successfully = False

    current_bot_bal = get_bot_player_balance(player_id)
    if payout_credited_successfully:
        send_message_to_player(player_id, f"{final_outcome_text} Your new bot balance: {current_bot_bal} gold.")
    else:
        # Message about critical error already sent
        send_message_to_player(player_id, f"Please check your bot balance. Current bot balance is {current_bot_bal} gold.")

    if player_id in active_games:
        del active_games[player_id]


def handle_command(player_id: str, command_text: str):
    parts = command_text.lower().strip().split()
    if not parts:
        send_message_to_player(player_id, "Please enter a command. Type `!info` for help.")
        return

    command = parts[0]
    args = parts[1:]

    # Player/Admin identification for commands
    # player_id is the ID of the user sending the command.

    if command == "!info":
        send_message_to_player(player_id, INFO_MESSAGE)
        if player_id in ADMIN_PLAYER_IDS:
            send_message_to_player(player_id, ADMIN_INFO_MESSAGE) # Send admin commands separately

    elif command == "!balance":
        balance = get_bot_player_balance(player_id)
        send_message_to_player(player_id, f"Your current bot balance is: {balance} gold.")

    elif command == "!botbalance": # New admin command
        if player_id not in ADMIN_PLAYER_IDS:
            send_message_to_player(player_id, "Error: This command is for admin use only.")
            return
        total_balance = get_total_bot_balance() # This function will be in highrise_api_client.py
        send_message_to_player(player_id, f"Total gold held by the bot across all player balances: {total_balance} gold.")

    elif command == "!admin_credit":
        # Admin command to manually credit a player's internal bot balance.
        # This is used after an admin confirms receipt of gold from a player via Highrise direct transfer.
        if player_id not in ADMIN_PLAYER_IDS: # Check if the command issuer is in the list of admins
            send_message_to_player(player_id, "Error: This command is for admin use only.")
            return

        if len(args) < 2 or not args[1].isdigit(): # Expects target player ID and amount
            send_message_to_player(player_id, "Usage: `!admin_credit <target_player_id> <amount>` (Example: !admin_credit player123 500)")
            return

        target_player_id = args[0]
        amount = int(args[1])

        if amount <= 0:
            send_message_to_player(player_id, "Credit amount must be positive.")
            return

        if update_bot_player_balance(target_player_id, amount):
            new_bal = get_bot_player_balance(target_player_id)
            send_message_to_player(player_id, f"Successfully credited {amount} gold to {target_player_id}. Their new bot balance is {new_bal} gold.")
            # Optionally, also message the target_player_id if your bot can PM them and if it's desired
            # send_message_to_player(target_player_id, f"An admin has credited your bot account with {amount} gold. Your new balance is {new_bal} gold.")
        else:
            send_message_to_player(player_id, f"Failed to credit {target_player_id}. Internal balance update error. Ensure player ID is correct.")

    elif command == "!withdraw":
        if len(args) < 1 or not args[0].isdigit():
            send_message_to_player(player_id, "Usage: `!withdraw <amount>` (e.g., `!withdraw 100`)")
            return
        amount = int(args[0])
        if amount <= 0:
            send_message_to_player(player_id, "Withdrawal amount must be positive.")
            return

        current_bot_balance = get_bot_player_balance(player_id)
        if current_bot_balance < amount:
            send_message_to_player(player_id, f"Insufficient bot balance. You have {current_bot_balance} gold, tried to withdraw {amount}.")
            return

        hr_success, hr_message = execute_withdraw_to_highrise(player_id, amount)
        if hr_success:
            if update_bot_player_balance(player_id, -amount): # Deduct from internal balance AFTER HR success
                new_bal = get_bot_player_balance(player_id)
                send_message_to_player(player_id, f"{hr_message} Your new bot balance: {new_bal} gold.")
            else:
                # This is a critical error state - HR transfer succeeded but internal deduction failed.
                send_message_to_player(player_id, f"CRITICAL ERROR: Withdrawal of {amount} gold to Highrise succeeded, but failed to update internal bot balance. Please contact an admin immediately. Your bot balance may be incorrect ({current_bot_balance} before deduction attempt).")
        else:
            send_message_to_player(player_id, f"Withdrawal failed: {hr_message}")


    elif command == "!play":
        if player_id in active_games:
            send_message_to_player(player_id, "You already have a game in progress. Use `!hit` or `!stand`.")
            return
        if len(args) < 1 or not args[0].isdigit():
            send_message_to_player(player_id, "Usage: `!play <bet_amount>` (e.g., `!play 100`)")
            return

        bet_amount = int(args[0])
        if bet_amount <= 0:
            send_message_to_player(player_id, "Bet amount must be positive.")
            return

        current_bot_balance = get_bot_player_balance(player_id)
        if current_bot_balance < bet_amount:
            send_message_to_player(player_id, f"Insufficient bot balance. You have {current_bot_balance} gold, need {bet_amount} to play. Please ask an admin to credit your account after you've sent gold.")
            return

        if not update_bot_player_balance(player_id, -bet_amount):
            send_message_to_player(player_id, "Error placing your bet from bot balance. Could not update balance. Please try again.")
            return

        send_message_to_player(player_id, f"Bet of {bet_amount} gold accepted from your bot balance. Current bot balance: {get_bot_player_balance(player_id)} gold.")

        game = Game(player_id=player_id, bet=bet_amount)
        active_games[player_id] = game

        initial_status_message = game.start_game()
        send_message_to_player(player_id, f"New Blackjack game started! Your bet: {bet_amount} gold.")
        send_message_to_player(player_id, initial_status_message)

        if game.game_state == Game.GAME_STATE_PLAYER_TURN:
            send_message_to_player(player_id, "Your turn: `!hit` or `!stand`?")
        elif game.game_state == Game.GAME_STATE_GAME_OVER:
            _handle_payout_and_cleanup(player_id)

    elif command == "!hit":
        if player_id not in active_games:
            send_message_to_player(player_id, "No active game. Start one with `!play <amount>`.")
            return
        game = active_games[player_id]

        if game.game_state != Game.GAME_STATE_PLAYER_TURN:
            send_message_to_player(player_id, f"Not your turn or game is over. Current status: {game.get_game_status_message()}")
            return

        hit_message = game.player_hit()
        send_message_to_player(player_id, hit_message)

        if game.game_state == Game.GAME_STATE_GAME_OVER:
            _handle_payout_and_cleanup(player_id)

    elif command == "!stand":
        if player_id not in active_games:
            send_message_to_player(player_id, "No active game. Start one with `!play <amount>`.")
            return
        game = active_games[player_id]

        if game.game_state != Game.GAME_STATE_PLAYER_TURN:
            send_message_to_player(player_id, f"Not your turn or game is over. Current status: {game.get_game_status_message()}")
            return

        stand_message = game.player_stand()
        send_message_to_player(player_id, stand_message)

        if game.game_state == Game.GAME_STATE_GAME_OVER:
            _handle_payout_and_cleanup(player_id)
        else:
            # This case should ideally not be reached
            send_message_to_player(player_id, f"Error: Game did not properly conclude after stand. Current status: {game.get_game_status_message()}")
            if player_id in active_games:
                 del active_games[player_id]
    else:
        send_message_to_player(player_id, f"Unknown command: `{command}`. Type `!info` for help.")

print("bot_logic.py updated with new currency management and admin command.")
