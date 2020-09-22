import random

numRandomNumbers = 3

successMessages = ["Nice", "Well done", "Congratulations", "You're psychic", "Excellent", "Nicely done", "Good job", "Correct"]
failureMessages = ["Wrong", "Incorrect", "Failure", "You lose", "False", "Try harder", "Disappointing", "Shameful", "Be better", "Git gud"]

def printNums(arr):
    for i in arr[:-1]:
        print(i, end=', ')
    print("and " + str(arr[-1]) + ".")

print("Let's play a game.\nI'm thinking of 3 numbers from 1 to 10. Guess any one of them, and you win.\nType 'q' to quit.")

while 1:
    randomNums = random.sample(range(1, 11), numRandomNumbers)

    print("\nYour choice: ", end='')
    userInput = input()
    
    if userInput.lower() == 'q':
        print("Goodbye!")
        exit()

    try:
        userNum = int(userInput)
        if userNum in randomNums:
            print(random.choice(successMessages) + "! My numbers were ", end='')
        else:
            print(random.choice(failureMessages) + ". My numbers were ", end='')
        printNums(randomNums)
        
        print("Let's play again! (or press 'q' to quit)")
    except ValueError:
        print(random.choice(failureMessages) + ". That wasn't a number...")
        
