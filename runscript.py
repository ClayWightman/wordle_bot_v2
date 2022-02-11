import csv


def get_all_words():
    words = []
    with open('valid_words.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            for word in row:
                words.append(word)
    return words


def get_possible_words(guess_word, pruned_words):
    possible_words = []
    for word in pruned_words:
        inx = 0
        viable_word = True
        for letter in word:
            if letter != guess_word[inx] and guess_word[inx] != '*':
                viable_word = False
            inx += 1
        if viable_word:
            possible_words.append(word)
    return possible_words


def add_letter_to_guess_word_from_two_halves(guess_word, half_one, half_two, pruned_words):
    half_of_half_one = len(half_one)/2
    half_of_half_two = len(half_two)/2
    half_one_letter_frequency_by_index = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}
    half_two_letter_frequency_by_index = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}
    for word in half_one:
        pos = 0
        for letter in word:
            if letter in half_one_letter_frequency_by_index[pos]:
                half_one_letter_frequency_by_index[pos][letter] += 1
            else:
                half_one_letter_frequency_by_index[pos][letter] = 1
            pos += 1
    for word in half_two:
        pos = 0
        for letter in word:
            if letter in half_two_letter_frequency_by_index[pos]:
                half_two_letter_frequency_by_index[pos][letter] += 1
            else:
                half_two_letter_frequency_by_index[pos][letter] = 1
            pos += 1
    lowest_difference = 99999
    best_position = None
    best_letter = None
    for letter_index in half_one_letter_frequency_by_index:
        if guess_word[letter_index] == '*':
            for letter in half_one_letter_frequency_by_index[letter_index]:
                total_split_difference = abs(half_of_half_one - half_one_letter_frequency_by_index[letter_index].get(letter, 0)) + abs(half_of_half_two - half_two_letter_frequency_by_index[letter_index].get(letter, 0))
                if total_split_difference < lowest_difference:
                    lowest_difference = total_split_difference
                    best_position = letter_index
                    best_letter = letter
    guess_word = guess_word[:best_position] + best_letter + guess_word[best_position+1:]
    return guess_word


def get_first_letter_for_guess_word(guess_word, pruned_words):
    letter_frequency_by_index = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}
    possible_words = get_possible_words(guess_word, pruned_words)
    for word in possible_words:
        pos = 0
        for letter in word:
            if letter in letter_frequency_by_index[pos]:
                letter_frequency_by_index[pos][letter] += 1
            else:
                letter_frequency_by_index[pos][letter] = 1
            pos += 1
    lowest_difference = 99999
    best_position = None
    best_letter = None
    half_of_possible_words = len(possible_words)/2
    for letter_index in letter_frequency_by_index:
        if guess_word[letter_index] == '*':
            for letter in letter_frequency_by_index[letter_index]:
                if abs(half_of_possible_words - letter_frequency_by_index[letter_index].get(letter, 0)) < lowest_difference:
                    lowest_difference = abs(half_of_possible_words - letter_frequency_by_index[letter_index].get(letter, 0))
                    best_position = letter_index
                    best_letter = letter
    guess_word = guess_word[:best_position] + best_letter + guess_word[best_position+1:]
    return guess_word


def split_words(guess_word, pruned_words):
    words_guessable = []
    words_not_guessable = []
    for word in pruned_words:
        inx = 0
        viable_word = True
        for letter in word:
            if letter != guess_word[inx] and guess_word[inx] != '*':
                viable_word = False
            inx += 1
        if viable_word:
            words_guessable.append(word)
        else:
            words_not_guessable.append(word)
    halves = [words_guessable, words_not_guessable]
    return halves


def get_guess_word(guess_word, pruned_words):
    if not '*' in guess_word:
        return guess_word
    if guess_word == '*****':
        guess_word = get_first_letter_for_guess_word(guess_word, pruned_words)
    halves = split_words(guess_word, pruned_words)
    half_one = halves[0]
    half_two = halves[1]
    guess_word = add_letter_to_guess_word_from_two_halves(guess_word, half_one, half_two, pruned_words)
    guess_word = get_guess_word(guess_word, pruned_words)
    return guess_word


def prune_words(guess_word, accuracy, pruned_words):
    new_pruned_words = pruned_words.copy()
    inx = 0
    for num in accuracy:
        if num == '2':
            for word in pruned_words:
                if word[inx] != guess_word[inx] and word in new_pruned_words:
                    new_pruned_words.remove(word)
        elif num == '1':  #TODO:  MAKE THIS REMOVE WORDS WHICH HAVE LETTERS IN THE SAME POSITION
            for word in pruned_words:
                if not guess_word[inx] in word and word in new_pruned_words:
                    new_pruned_words.remove(word)
                if word[inx] == guess_word[inx] and word in new_pruned_words:
                    new_pruned_words.remove(word)
        elif num == '0':
            letter_occurances_in_answer = 0
            if guess_word.count(guess_word[inx]) > 1:
                second_inx = 0
                for letter in guess_word:
                    if letter == guess_word[inx] and accuracy[second_inx] != '0':
                        letter_occurances_in_answer += 1
                    second_inx += 1
            if letter_occurances_in_answer == 0:
                #remove all words with this letter
                for word in pruned_words:
                    if guess_word[inx] in word and word in new_pruned_words:
                        new_pruned_words.remove(word)
            else:
                #remove all words with this letter more or less than calculated number of occurances
                for word in pruned_words:
                    if word.count(guess_word[inx]) != letter_occurances_in_answer and word in new_pruned_words:
                        new_pruned_words.remove(word)
        inx += 1
    return new_pruned_words


def runscript():
    pruned_words = get_all_words()
    turn = 0
    while turn < 6:
        print("length of pruned words is " + str(len(pruned_words)))
        guess_word = get_guess_word('*****', pruned_words)
        accuracy = input ('INPUT "' + guess_word + '" then input success values \n')
        if accuracy.count('0') + accuracy.count('1') + accuracy.count('2') != 5:
            print("There seems to be a mistake in your success values")
        else:
            pruned_words = prune_words(guess_word, accuracy, pruned_words)
            if accuracy == '22222':
                turn = 7
                print("Congradulations on your victory!")

            turn += 1
            
    if turn == 6:
        print("Sorry for your loss (in the game that is)")

runscript()
