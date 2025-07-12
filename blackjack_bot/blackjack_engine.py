import random

# Placeholder for card values and suits
SUITS = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
CARD_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = CARD_VALUES[rank]

    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in SUITS for r in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None # Should not happen in a standard game

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0 # To handle Ace value (1 or 11)

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces > 0:
            self.value -= 10
            self.aces -= 1

    def __str__(self):
        return ", ".join(str(card) for card in self.cards) + f" (Value: {self.value})"

# More game logic will be added in the "Implement Blackjack Game Logic" step.

class Game:
    GAME_STATE_NOT_STARTED = "NOT_STARTED"
    GAME_STATE_PLAYER_TURN = "PLAYER_TURN"
    GAME_STATE_DEALER_TURN = "DEALER_TURN"
    GAME_STATE_GAME_OVER = "GAME_OVER"

    OUTCOME_PLAYER_BLACKJACK = "PLAYER_BLACKJACK"
    OUTCOME_PLAYER_WINS = "PLAYER_WINS"
    OUTCOME_DEALER_WINS = "DEALER_WINS"
    OUTCOME_PUSH = "PUSH" # Tie
    OUTCOME_PLAYER_BUSTS = "PLAYER_BUSTS"
    OUTCOME_DEALER_BUSTS = "DEALER_BUSTS"

    def __init__(self, player_id: str, bet: int):
        self.player_id = player_id
        self.bet = bet
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.dealer_hidden_card = None
        self.game_state = self.GAME_STATE_NOT_STARTED
        self.outcome = None # Stores the result like OUTCOME_PLAYER_WINS

    def _deal_initial_cards(self):
        self.player_hand.add_card(self.deck.deal_card())
        self.player_hand.add_card(self.deck.deal_card())

        # Dealer's first card is visible, second is hidden
        self.dealer_hand.add_card(self.deck.deal_card())
        self.dealer_hidden_card = self.deck.deal_card()
        # Don't add hidden card to dealer's hand value until revealed

    def start_game(self):
        self._deal_initial_cards()
        self.game_state = self.GAME_STATE_PLAYER_TURN

        # Check for player Blackjack immediately
        if self.player_hand.value == 21:
            # Reveal dealer's hidden card to check for dealer Blackjack
            self.dealer_hand.add_card(self.dealer_hidden_card)
            self.dealer_hidden_card = None # Card is now revealed

            if self.dealer_hand.value == 21: # Both have Blackjack
                self.outcome = self.OUTCOME_PUSH
            else: # Player Blackjack, dealer does not have Blackjack
                self.outcome = self.OUTCOME_PLAYER_BLACKJACK
            self.game_state = self.GAME_STATE_GAME_OVER
            return self.get_game_status_message()

        return self.get_game_status_message()

    def player_hit(self):
        if self.game_state != self.GAME_STATE_PLAYER_TURN:
            return "Error: Not player's turn or game is over."

        card = self.deck.deal_card()
        if card:
            self.player_hand.add_card(card)

        if self.player_hand.value > 21:
            self.outcome = self.OUTCOME_PLAYER_BUSTS
            self.game_state = self.GAME_STATE_GAME_OVER
            return f"Player hits and busts with {self.player_hand.value}! {self.get_game_status_message()}"
        elif self.player_hand.value == 21:
            # Player has 21, automatically stands.
            return self.player_stand() # Transition to dealer's turn

        return f"Player hits. {self.get_game_status_message()}"

    def player_stand(self):
        if self.game_state != self.GAME_STATE_PLAYER_TURN:
            return "Error: Not player's turn or game is over."

        self.game_state = self.GAME_STATE_DEALER_TURN
        return f"Player stands. {self.dealer_play()}" # Dealer plays their turn

    def dealer_play(self):
        if self.game_state != self.GAME_STATE_DEALER_TURN:
            # This might be called internally after player stands or if player busts with Blackjack check
            pass

        # Reveal dealer's hidden card
        if self.dealer_hidden_card:
            self.dealer_hand.add_card(self.dealer_hidden_card)
            self.dealer_hidden_card = None

        status_messages = [f"Dealer reveals hidden card. Dealer's hand: {self.dealer_hand}"]

        # Dealer hits until hand value is 17 or more
        while self.dealer_hand.value < 17:
            if not self.deck.cards: # Should not happen if deck is sufficient
                status_messages.append("Dealer cannot draw, deck empty.")
                break
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            status_messages.append(f"Dealer hits and gets {card}. Dealer's hand: {self.dealer_hand}")

        if self.dealer_hand.value > 21:
            self.outcome = self.OUTCOME_DEALER_BUSTS
            status_messages.append(f"Dealer busts with {self.dealer_hand.value}!")

        self.game_state = self.GAME_STATE_GAME_OVER
        if not self.outcome: # If outcome not already set (e.g. by player bust)
            self._determine_winner_after_stand()

        status_messages.append(self.get_final_outcome_message())
        return " ".join(status_messages)

    def _determine_winner_after_stand(self):
        # This is called when player stands and dealer has played without busting.
        # Player bust is handled in player_hit. Dealer bust is handled in dealer_play.
        # Player Blackjack vs Dealer non-Blackjack is handled in start_game.
        if self.outcome: # Already determined (e.g. player Blackjack, player bust)
            return

        if self.player_hand.value > 21: # Should be caught by player_hit, but as a safeguard
            self.outcome = self.OUTCOME_PLAYER_BUSTS
        elif self.dealer_hand.value > 21: # Should be caught by dealer_play
            self.outcome = self.OUTCOME_DEALER_BUSTS
        elif self.player_hand.value > self.dealer_hand.value:
            self.outcome = self.OUTCOME_PLAYER_WINS
        elif self.dealer_hand.value > self.player_hand.value:
            self.outcome = self.OUTCOME_DEALER_WINS
        else: # player_hand.value == dealer_hand.value
            self.outcome = self.OUTCOME_PUSH

        self.game_state = self.GAME_STATE_GAME_OVER

    def get_payout_multiplier(self) -> float:
        if self.outcome == self.OUTCOME_PLAYER_BLACKJACK:
            return 2.5  # Standard 3:2 payout for Blackjack (bet + 1.5*bet)
        elif self.outcome == self.OUTCOME_PLAYER_WINS or self.outcome == self.OUTCOME_DEALER_BUSTS:
            return 2.0  # Standard 1:1 payout (bet + 1*bet)
        elif self.outcome == self.OUTCOME_PUSH:
            return 1.0  # Bet returned
        else: # Player loses (dealer wins, player busts)
            return 0.0  # Player loses the bet

    def get_game_status_message(self) -> str:
        player_cards_str = str(self.player_hand)

        if self.game_state == self.GAME_STATE_PLAYER_TURN and self.dealer_hidden_card:
            dealer_cards_str = f"{str(self.dealer_hand.cards[0])}, [Hidden]"
            dealer_value_str = f"(Showing: {self.dealer_hand.cards[0].value})"
        else: # Game over or dealer's turn (hidden card revealed)
            dealer_cards_str = str(self.dealer_hand)
            dealer_value_str = f"(Value: {self.dealer_hand.value})"

        status = (f"Player: {player_cards_str} (Value: {self.player_hand.value}) | "
                  f"Dealer: {dealer_cards_str} {dealer_value_str} | "
                  f"Bet: {self.bet} | State: {self.game_state}")
        if self.game_state == self.GAME_STATE_GAME_OVER and self.outcome:
            status += f" | Outcome: {self.outcome}"
        return status

    def get_final_outcome_message(self) -> str:
        if not self.outcome:
            return "Game is not over yet or outcome undetermined."

        base_msg = f"Final Hands - Player: {self.player_hand} (Value: {self.player_hand.value}), Dealer: {self.dealer_hand} (Value: {self.dealer_hand.value})."

        if self.outcome == self.OUTCOME_PLAYER_BLACKJACK:
            return f"{base_msg} Player Blackjack! Player wins {self.bet * 1.5} gold (plus original bet)."
        elif self.outcome == self.OUTCOME_PLAYER_WINS:
            return f"{base_msg} Player wins! Player wins {self.bet} gold (plus original bet)."
        elif self.outcome == self.OUTCOME_DEALER_BUSTS:
            return f"{base_msg} Dealer busts! Player wins {self.bet} gold (plus original bet)."
        elif self.outcome == self.OUTCOME_DEALER_WINS:
            return f"{base_msg} Dealer wins. Player loses {self.bet} gold."
        elif self.outcome == self.OUTCOME_PLAYER_BUSTS:
            return f"{base_msg} Player busts. Player loses {self.bet} gold."
        elif self.outcome == self.OUTCOME_PUSH:
            return f"{base_msg} Push (Tie). Player's bet of {self.bet} gold is returned."
        return "Error: Unknown outcome."


print("blackjack_engine.py updated with detailed Game logic.")
