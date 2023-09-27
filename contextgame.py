import re
import random
from modelsetup import daily_words, guessing_words, word_vectors, pattern

def getIdxDistance(word, day_word, similarity_vector):
  if word == day_word:
    return 0
  for idx, i in enumerate(similarity_vector):
    if i[0] == word:
      return idx + 1


def main():
    
    common_nouns = []

    with open('1000nouns/top-1000-nouns.txt') as f:
        for line in f:
            common_nouns.append(line.strip())

    common_nouns[0] #prva rijec je time ali u formatu 'ï»¿time', treba popraviti

    common_nouns[0] = common_nouns[0][3:]

    common_nouns_filtered = []
    for noun in common_nouns:
        if noun in daily_words.keys():
            common_nouns_filtered.append(noun)
    
    level = input('Choose difficulty level (easy/medium/hard): ')


    if level == 'easy':
      easy_day_word = random.choice(common_nouns_filtered[:100])
      easy_day_word_with_tag = '_'.join([easy_day_word, 'NOUN'])
      #print(easy_day_word)
      similarity_vector = word_vectors.similar_by_word(easy_day_word_with_tag, topn=len(word_vectors.key_to_index))

      similarity_vector_filtered = []

      for word, similarity in similarity_vector:
            if re.match(pattern, word.split('_')[0]):
                    similarity_vector_filtered.append((word.split('_')[0], similarity))
    
      game(easy_day_word, similarity_vector_filtered)
    
    
    elif level == 'medium':
      medium_day_word = random.choice(common_nouns_filtered[100:])
      medium_day_word_with_tag = '_'.join([medium_day_word, 'NOUN'])
      #print(medium_day_word)
      similarity_vector = word_vectors.similar_by_word(medium_day_word_with_tag, topn=len(word_vectors.key_to_index))

      similarity_vector_filtered = []

      for word, similarity in similarity_vector:
            if re.match(pattern, word.split('_')[0]):
                    similarity_vector_filtered.append((word.split('_')[0], similarity))
    
      game(medium_day_word, similarity_vector_filtered)


    elif level == 'hard':
      hard_day_word = random.choice(list(daily_words.keys()))
      hard_day_word_with_tag = '_'.join([hard_day_word, 'NOUN'])
      #print(hard_day_word)
      similarity_vector = word_vectors.similar_by_word(hard_day_word_with_tag, topn=len(word_vectors.key_to_index))
    
      similarity_vector_filtered = []

      for word, similarity in similarity_vector:
            if re.match(pattern, word.split('_')[0]):
                    similarity_vector_filtered.append((word.split('_')[0], similarity))

      game(hard_day_word, similarity_vector_filtered)

    else:
      print('Invalid input. Type in easy, medium or hard.')


def game(day_word, similarity_vector):
    words = {}
    no_of_guesses = 0
    no_of_hints = 1

    while True:
        if no_of_guesses % 5 == 0 and no_of_guesses != 0:
            print('If you would like a hint, type in /hint')
        
        word = input('Enter a word: ')

        if word == '/hint' and no_of_hints < len(day_word):
            print (f"the first letters of the word are: {day_word[:no_of_hints]}")
            no_of_hints += 1
        elif word == '/hint' and no_of_hints >= len(day_word):
            print("No more hints available.")

        no_of_guesses += 1

        distance = getIdxDistance(word, day_word, similarity_vector)

        if distance == 0:
            print('Congrats, you found the word! Restart for more challenges :)')
            break

        if distance is None and word != '/hint':
            print('The word you entered is not in the dictionary. Try again.')
            continue
        elif word == '/hint':
            continue

        words[word] = distance
            
        print('{} -------- {}'.format(word, distance))


if __name__ == '__main__':
    main()
