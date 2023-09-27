from gensim.models import KeyedVectors
import re
import enchant

model = "model1/model.txt"

word_vectors = KeyedVectors.load_word2vec_format(model, binary=False, limit=50000)

dict = enchant.Dict("en_US")

# regex koji provjerava ima li rijec 3+ slova
pattern = r'^[a-z]{3,}$'

daily_words = {}
guessing_words = {}

for key, value in word_vectors.key_to_index.items():
        splitter = key.split('_')
        if dict.check(splitter[0]):
            if splitter[1] == 'NOUN' and re.match(pattern, splitter[0]):
                if daily_words.get(splitter[0]) is not None:
                    daily_words[splitter[0]].append(splitter[1])
                    guessing_words[splitter[0]].append(splitter[1])
                else:
                    daily_words[splitter[0]] = [splitter[1]]
                    guessing_words[splitter[0]] = [splitter[1]]
            elif (splitter[1] == 'ADJ' or splitter[1] == 'VERB') and re.match(pattern, splitter[0]):
                if guessing_words.get(splitter[0]) is not None:
                    guessing_words[splitter[0]].append(splitter[1])
                else:
                    guessing_words[splitter[0]] = [splitter[1]]

