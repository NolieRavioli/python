# if you cannot move, you lose. NIM Logic.
# updated Nov 19 22
# By Nolan Peet

from random import randint
from time import sleep
from math import floor, log


def dumb_step(balls, legal):
    return randint(1, legal) if balls > 3 else 1


def smart_step(balls, legal):
    """ these are my MAGIC numbers. xₙ = 2xₙ₋₁ + 1, where x₁ = 2.
        xₙ = 3(2ⁿ)-1 when n₁ = 0 is the way to represent that without referencing the last result.
        thinking of doubling the last value is like saying 2^n.
        3...-1 ensures that when n=0, your opponent is left with exactly 2 balls... idk
        so, solving for int(n) where xₙ is balls: n = floor(log₂((balls+1)/3))
         2xₙ₋₁+1:[2 ,5,11,23,47,95]
            xₙ+1:[3, 6,12,24,48,96]
            xₙ/3:[1, 2, 4, 8,16,32]
        log2(xₙ):[0, 1, 2, 3, 4, 5]
    magic_number = 3 × 2ᶠˡᵒᵒʳ⁽ˡᵒᵍ₂⁽⁽ᵇᵃˡˡˢ⁺¹⁾/³⁾⁾ - 1
    OR if you think of 2ᶠˡᵒᵒʳ⁽ˡᵒᵍ₂⁽⁽ᵇᵃˡˡˢ⁺¹⁾/³⁾⁾ as a binary representation,
    you're asking 'what is the index of the leading 1 in the binary form?', therefore,
    len(bin(balls))-1-bin(balls).find('1') = floor(log((balls + 1) / 3, 2))"""
    magic_number = 3 * 2 ** floor(log((balls + 1) / 3, 2)) - 1
    if balls == 1:
        print("...too easy...")
        sleep(2)
    return balls - magic_number if 0 < balls - magic_number <= legal else 1


def player_step(balls, legal):
    if balls != 1:
        print("Your move.\n     There are", balls, "balls.")
        while True:
            # Repeats until the player picks a legal move
            take = input("How many are you going to take?"+("(1)" if balls <= 3 else f"(1-{legal})")+"\n         ")
            if take.isdigit() and 0 < int(take) <= legal:
                return int(take)
    else:
        print("one remains.... and you SNATCH IT!")
        sleep(2)
        return 1


def nim_game():
    # All the parts come together.
    input("This is a game, The rules are as follows:\n"
          "Starting with a random number of balls between 20 and 100,\n"
          "The goal is to grab the last ball!\n"
          "You may grab any number of balls up to half the number of current balls (inclusive, rounding down).\n"
          "GOOD LUCK AND HAVE FUN, GAMER.\n"
          "Press Enter to continue!")

    balls = randint(20, 100)
    while True:
        difficulty = input("Bot difficulty: Easy(0) or Hard(1)")
        if difficulty.isdigit() and int(difficulty) in [0, 1]:
            difficulty = int(difficulty)
            break
        elif difficulty.lower() in ['e', 'h', 'hard', 'easy']:
            difficulty = 0 if difficulty.lower() in ['e', 'easy'] else 1
            break
    print("and here comes the coin flip....")
    for i in range(3):
        print(3-i)
        sleep(1)
    who_moves = randint(0, 1)
    print("HEADS!!!" if who_moves else "TAILS.")
    sleep(1)
    print(f"Starting Game with {balls} balls.")
    sleep(2)

    while balls > 0:
        # MAIN GAME LOOP
        legal = balls // 2  # maximun amount of balls you can take within the game rules
        if who_moves == 1:
            # PLAYER MOVE
            balls -= player_step(balls, legal)
            who_moves = 0  # Bot's turn now
        else:
            # BOT MOVE
            bot_move = smart_step(balls, legal) if difficulty == 1 else dumb_step(balls, legal)
            balls -= bot_move
            print("The bot moved. It took", bot_move, "balls.")
            who_moves = 1  # User's turn now

    # END OF GAME
    if who_moves:
        print("The bot won! :(")
    else:
        print("You won!! :)")
    sleep(5)


nim_game()  # run game
