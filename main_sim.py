from blackjack_bot.bot_logic import handle_command, ADMIN_PLAYER_IDS
from blackjack_bot.highrise_api_client import _player_bot_balances, get_bot_player_balance, send_message_to_player # For direct inspection/setup

# Helper function for simulation
def simulate_player_interaction(player_id, commands, description=""):
    """
    Simulates a player sending a series of commands to the bot.
    """
    if description:
        print(f"\n--- Test Scenario: {description} (Player: {player_id}) ---")
    else:
        print(f"\n--- Simulating interaction for player: {player_id} ---")

    print(f"Initial bot balance for {player_id}: {get_bot_player_balance(player_id)} gold")
    for cmd in commands:
        print(f"\n{player_id} sends: {cmd}")
        handle_command(player_id, cmd)
    print(f"Final bot balance for {player_id}: {get_bot_player_balance(player_id)} gold")
    print(f"--- End simulation for player: {player_id} ---\n")

if __name__ == "__main__":
    print("Starting Highrise Blackjack Bot Simulation (with Admin Features)...\n")

    # --- Test Setup ---
    # Ensure balances are clean at the start of a full test run
    _player_bot_balances.clear()

    test_admin_id = ADMIN_PLAYER_IDS[0] if ADMIN_PLAYER_IDS else "test_admin" # Use one of the defined admins
    player_regular_id = "player_alpha"
    player_beta_id = "player_beta"

    # --- Test Scenarios ---

    # 1. Admin Credit Command Tests
    admin_credit_tests = [
        "!admin_credit", # Wrong syntax
        "!admin_credit " + player_regular_id, # Wrong syntax
        "!admin_credit " + player_regular_id + " -50", # Invalid amount
        "!admin_credit " + player_regular_id + " 500" # Valid
    ]
    simulate_player_interaction(test_admin_id, admin_credit_tests, "Admin Credit Functionality")

    non_admin_id = "random_user"
    non_admin_credit_attempt = [
        "!admin_credit " + player_regular_id + " 100"
    ]
    simulate_player_interaction(non_admin_id, non_admin_credit_attempt, "Non-Admin Trying to Use Admin Credit")

    # 2. Player Balance and Info (Regular Player)
    player_alpha_info_balance = [
        "!balance", # Check initial (should be 500 from above)
        "!info"     # Regular player info
    ]
    simulate_player_interaction(player_regular_id, player_alpha_info_balance, "Player Checks Balance and Info")

    # Admin Info and Bot Balance checks
    admin_info_botbalance_tests = [
        "!info",        # Admin should get extended info
        "!botbalance"   # Admin checks total bot balance (should be 500 from player_alpha's credit)
    ]
    simulate_player_interaction(test_admin_id, admin_info_botbalance_tests, "Admin Info & Bot Balance Checks")

    non_admin_botbalance_attempt = [
        "!botbalance"
    ]
    simulate_player_interaction(player_regular_id, non_admin_botbalance_attempt, "Non-Admin Tries !botbalance")

    # 3. Gameplay with Bot Balance
    player_alpha_gameplay = [
        "!play 1000", # Insufficient balance
        "!play 100",  # Valid play
        "!hit",
        "!stand"      # Game should complete and affect balance
    ]
    simulate_player_interaction(player_regular_id, player_alpha_gameplay, "Player Gameplay with Bot Balance")

    # Check balance after game
    simulate_player_interaction(player_regular_id, ["!balance"], "Player Checks Balance Post-Game")

    # 4. Withdrawal Tests
    # First, credit more to test various withdrawal scenarios
    admin_adds_more_funds = [
        "!admin_credit " + player_regular_id + " 300"
    ]
    simulate_player_interaction(test_admin_id, admin_adds_more_funds, "Admin Adds More Funds for Withdrawal Tests")

    player_alpha_withdrawals = [
        "!withdraw 10000", # Withdraw more than balance
        "!withdraw -50",   # Invalid amount
        "!withdraw",       # Invalid syntax
        "!withdraw 200"    # Valid withdrawal (assuming enough balance after game and re-credit)
    ]
    simulate_player_interaction(player_regular_id, player_alpha_withdrawals, "Player Withdrawal Tests")

    # Check balance after withdrawal
    simulate_player_interaction(player_regular_id, ["!balance"], "Player Checks Balance Post-Withdrawal")

    # 5. Player trying to play without any balance (new player)
    simulate_player_interaction(player_beta_id, ["!balance"], "New Player Beta Checks Initial Balance")
    player_beta_play_attempt = [
        "!play 50"
    ]
    simulate_player_interaction(player_beta_id, player_beta_play_attempt, "New Player Beta Tries to Play")

    # 6. Admin credits Player Beta, then Player Beta plays
    admin_credits_beta = [
        "!admin_credit " + player_beta_id + " 200"
    ]
    simulate_player_interaction(test_admin_id, admin_credits_beta, "Admin Credits Player Beta")

    player_beta_plays_successfully = [
        "!balance",
        "!play 100",
        "!hit",
        "!stand"
    ]
    simulate_player_interaction(player_beta_id, player_beta_plays_successfully, "Player Beta Plays Successfully After Credit")


    print("\nHighrise Blackjack Bot Simulation Finished.")
    print("Review the output above for command responses and balance changes.")
    print("Ensure `ADMIN_PLAYER_IDS` in `bot_logic.py` is correctly set for a real environment.")
    if "YOUR_ADMIN_ID_HERE" in ADMIN_PLAYER_IDS:
        print("WARNING: `ADMIN_PLAYER_IDS` still contains placeholder 'YOUR_ADMIN_ID_HERE'. Please update in `bot_logic.py`.")

print("main_sim.py updated for comprehensive testing.")
