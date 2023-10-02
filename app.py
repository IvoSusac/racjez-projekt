import streamlit as st
import pandas as pd
from modelsetup import daily_words, pattern
import random
import re
from plots import append_list, display_scatterplot_2D, display_scatterplot_3D, model, horizontal_bar
from contextgame import getIdxDistance

def game(day_word, similarity_vector):
    if st.session_state.session_state['words'] == None:
        st.session_state.session_state['words'] = {}
    if st.session_state.session_state['no_of_guesses'] == None:
        st.session_state.session_state['no_of_guesses'] = 0
    if st.session_state.session_state['no_of_hints'] == None:
        st.session_state.session_state['no_of_hints'] = 1


    word = st.sidebar.text_input("Type the word that you think is similar to the target word")
    if st.session_state.session_state['no_of_guesses'] % 5 == 0 and st.session_state.session_state['no_of_guesses'] != 0:
        st.write('If you would like a hint, press the hint button')
    
    hint = st.button('Hint')
    if hint and st.session_state.session_state['no_of_hints'] < len(day_word):
        st.write(f"the first letters of the word are: {day_word[:st.session_state.session_state['no_of_hints']]}")
        st.session_state.session_state['no_of_hints'] += 1
        st.write(st.session_state.session_state['no_of_hints'])
    elif hint and st.session_state.session_state['no_of_hints'] >= len(day_word):
        st.write("No more hints available.")
    if word != '':
        st.session_state.session_state['no_of_guesses'] += 1
        distance = getIdxDistance(word, day_word, similarity_vector)
        if distance == 0:
            st.write('Congrats, you found the word! Restart for more challenges :)')
        if distance is None:
            st.write('The word you entered is not in the dictionary. Try again.')
        (st.session_state.session_state['words'])[word] = distance
        for word, distance in st.session_state.session_state['words'].items():
            st.write('{} -------- {}'.format(word, distance))



def main():
    game_or_plots = st.sidebar.selectbox('Select the app that you want to use', ('Context Game', 'Visualization'))
    if game_or_plots == 'Visualization':
        dim_red = st.sidebar.selectbox('Select the dimension reduction method', ('PCA','TSNE'))
        dimension = st.sidebar.selectbox(
             "Select the dimension of the visualization",
             ('2D', '3D'))
        user_input = st.sidebar.text_input("Type the word that you want to investigate. You can type more than one word by separating one word with other with comma (,). Make sure to write in the word with the appropriate POS tag, e.g. ball_NOUN",'')
        top_n = st.sidebar.slider('Select the amount of words associated with the input words you want to visualize ',
            5, 100, (5))
        annotation = st.sidebar.radio(
             "Enable or disable the annotation on the visualization",
             ('On', 'Off'))  

        if dim_red == 'TSNE':
            perplexity = st.sidebar.slider('Adjust the perplexity. The perplexity is related to the number of nearest neighbors that is used in other manifold learning algorithms. Larger datasets usually require a larger perplexity',
            5, 50, (5))

            learning_rate = st.sidebar.slider('Adjust the learning rate',
            10, 1000, (200))

            iteration = st.sidebar.slider('Adjust the number of iteration',
            250, 100000, (1000))

        else:
            perplexity = 0
            learning_rate = 0
            iteration = 0    

        if user_input == '':

            similar_word = None
            labels = None
            color_map = None

        else:

            user_input = [x.strip() for x in user_input.split(',')]
            result_word = []

            for words in user_input:
            
                sim_words = model.most_similar(words, topn = top_n)
                sim_words = append_list(sim_words, words)

                result_word.extend(sim_words)

            similar_word = [word[0] for word in result_word]
            similarity = [word[1] for word in result_word] 
            similar_word.extend(user_input)
            labels = [word[2] for word in result_word]
            label_dict = dict([(y,x+1) for x,y in enumerate(set(labels))])
            color_map = [label_dict[x] for x in labels]


        st.title('Word Embedding Visualization Based on Cosine Similarity')

        st.header('Visualizing word embeddings with the Plotly library.')

        st.write('On the left side of your screen you can adjust the dimension reduction method that is used to visualize the word embeddings. Select from two options - PCA or tSNE. The PCA method is a linear dimensionality reduction method that creates an orthogonal projection of the data to a lower dimensional space. The tSNE method is a non-linear dimensionality reduction method that uses a neural network and is well suited for embedding high-dimensional data for visualization in a low-dimensional space of two or three dimensions. If you want to visualize different words, select the dimensionality reduction method and type in words that you want to investigate in the appropriate text box. Type them in with their POS tag, e.g. ball_NOUN, time_NOUN. You can adjust the amount of words associated with the input words that you want to visualize. If using tSNE, you can also adjust the perplexity, learning rate and the number of iterations.')

        if dimension == '2D':
            st.header('2D Visualization')
            st.write('For more detail about each point, hover around each points to see the words. You can expand the visualization by clicking expand symbol in the top right corner of the visualization.')
            display_scatterplot_2D(model, user_input, similar_word, labels, color_map, annotation, dim_red, perplexity, learning_rate, iteration, top_n)
        else:
            st.header('3D Visualization')
            st.write('For more detail about each point, hover around each points to see the words. You can expand the visualization by clicking expand symbol in the top right corner of the visualization.')
            display_scatterplot_3D(model, user_input, similar_word, labels, color_map, annotation, dim_red, perplexity, learning_rate, iteration, top_n)

        st.header('The Top 5 Most Similar Words for Each Input')
        count=0
        for i in range (len(user_input)):

            st.write('The most similar words from '+str(user_input[i])+' are:')
            horizontal_bar(similar_word[count:count+5], similarity[count:count+5])

            count = count+top_n
    else:

        st.title('Word Guessing Game')

        st.header('Guess the target word!')

        st.write('Select the difficulty level of the target words on the left side of your screen. Type in a word you think is similar to the target word and press enter. The number on your screen signalizes how close you are to the target word. The smaller the number, the closer you are! If you want a hint, press the hint button. The first letters of the target word will be revealed. If you guess the word correctly, you can restart the game for more challenges. Good luck!')
        common_nouns = []

        with open('1000nouns/top-1000-nouns.txt') as f:
            for line in f:
                common_nouns.append(line.strip())


        common_nouns[0] = common_nouns[0][3:]

        common_nouns_filtered = []
        for noun in common_nouns:
            if noun in daily_words.keys():
                common_nouns_filtered.append(noun)

        
        if 'session_state' not in st.session_state:
                st.session_state.session_state = {
                    'level': None,
                    'easy_day_word': None,
                    'medium_day_word': None,
                    'hard_day_word': None,
                    'similarity_vector': None,
                    'similarity_vector_filtered': None,
                    'words': None,
                    'no_of_guesses': None,
                    'no_of_hints': None
                }
        
        selected_level = st.sidebar.selectbox('Select the level of difficulty', ('easy','medium','hard'))

        if selected_level != st.session_state.session_state['level']:
            st.session_state.session_state['level'] = selected_level
            st.session_state.session_state['easy_day_word'] = None
            st.session_state.session_state['medium_day_word'] = None
            st.session_state.session_state['hard_day_word'] = None
            st.session_state.session_state['similarity_vector'] = None
            st.session_state.session_state['similarity_vector_filtered'] = None
            st.session_state.session_state['words'] = None
            st.session_state.session_state['no_of_guesses'] = None
            st.session_state.session_state['no_of_hints'] = None
             


        if st.session_state.session_state['level'] == 'easy':
            if st.session_state.session_state['easy_day_word'] == None:
                st.session_state.session_state['easy_day_word'] = random.choice(common_nouns_filtered[:100])
                easy_day_word = st.session_state.session_state['easy_day_word']
                easy_day_word = random.choice(common_nouns_filtered[:100])
                easy_day_word_with_tag = '_'.join([easy_day_word, 'NOUN'])
                #print(easy_day_word)
                st.session_state.session_state['similarity_vector'] = model.similar_by_word(easy_day_word_with_tag, topn=len(model.key_to_index))

                st.session_state.session_state['similarity_vector_filtered'] = []

                for word, similarity in st.session_state.session_state['similarity_vector']:
                        if re.match(pattern, word.split('_')[0]):
                                st.session_state.session_state['similarity_vector_filtered'].append((word.split('_')[0], similarity))

                game(st.session_state.session_state['easy_day_word'], st.session_state.session_state['similarity_vector_filtered'])
            else:
                game(st.session_state.session_state['easy_day_word'], st.session_state.session_state['similarity_vector_filtered'])


        elif st.session_state.session_state['level'] == 'medium':
            if st.session_state.session_state['medium_day_word'] == None:
              st.session_state.session_state['medium_day_word'] = random.choice(common_nouns_filtered[100:])
              medium_day_word = st.session_state.session_state['medium_day_word']
              medium_day_word_with_tag = '_'.join([medium_day_word, 'NOUN'])
              #print(medium_day_word)
              st.session_state.session_state['similarity_vector'] = model.similar_by_word(medium_day_word_with_tag, topn=len(model.key_to_index))

              st.session_state.session_state['similarity_vector_filtered'] = []

              for word, similarity in st.session_state.session_state['similarity_vector']:
                      if re.match(pattern, word.split('_')[0]):
                              st.session_state.session_state['similarity_vector_filtered'].append((word.split('_')[0], similarity))

              game(st.session_state.session_state['medium_day_word'], st.session_state.session_state['similarity_vector_filtered'])
            else:
              game(st.session_state.session_state['medium_day_word'], st.session_state.session_state['similarity_vector_filtered'])


        elif st.session_state.session_state['level'] == 'hard':
            if 'hard_day_word' not in st.session_state:
                st.session_state.hard_day_word = random.choice(list(daily_words.keys()))
                hard_day_word = st.session_state.hard_day_word
                hard_day_word_with_tag = '_'.join([hard_day_word, 'NOUN'])
                #print(hard_day_word)
                st.session_state.similarity_vector = model.similar_by_word(hard_day_word_with_tag, topn=len(model.key_to_index))
    
                st.session_state.similarity_vector_filtered = []
    
                for word, similarity in st.session_state.similarity_vector:
                        if re.match(pattern, word.split('_')[0]):
                                st.session_state.similarity_vector_filtered.append((word.split('_')[0], similarity))
    
                game(st.session_state.hard_day_word, st.session_state.similarity_vector_filtered)
            else:
                game(st.session_state.hard_day_word, st.session_state.similarity_vector_filtered)
if __name__ == "__main__":
    main()