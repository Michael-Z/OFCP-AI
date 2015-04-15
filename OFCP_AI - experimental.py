# basis for MCTS
# very simple random monte carlo simulations
# TODO: integrate with scoring system to produce valid, usable results
#       produce tree from simulations 

from random import randint
import random
import helpers
import copy 

num_top_first_count = 0 # ensure that initial 5 card placement doesn't put too many top (very unlikely but possible)

number_top = 0      # keep track of cards placed top. When this reaches 3 prevent any more 
number_middle = 0   # max 5
number_bottom = 0   # max 5

deck = []           # random deck for simulations 
placed_cards_s = [] # stores records of simulated placed cards

class Node:
    ''' A node in the game tree '''
    def __init__(self):
        #self.moves_to_try = ?.findMoves()
        pass

def reset():
    ''' reset variables for a new round '''
    global num_top_first_count
    global deck
    num_top_first_count = 0
    deck = []
        
def find_valid_moves(game_state):
    ''' reads game state and detects how many valid placements are available for each row '''
    global number_bottom
    global number_middle
    global number_top
    
    number_bottom = 0
    number_middle = 0
    number_top = 0
    
    for i in range(1,14):
        temp = game_state['properties2']['cards']['items']['position'+str(i)]
        if temp != None:
            if i <= 5:
                number_bottom += 1
            elif i <= 10:
                number_middle += 1
            elif i <= 13:
                number_top += 1
    #print "Valid placements: Bottom", 5 - number_bottom, ", Middle", 5 - number_middle, ", Top", 3 - number_top, "\n"

def produce_deck_of_cards():
    ''' generates a standard deck of 52 cards. Ranks ace -> king; Suits hearts, diamonds, spades and clubs'''
    global deck
    deck = []
    suits = ["h", "d", "s", "c"]
    for suit in suits:
        for i in range(1,14):
            temp = suit
            if i < 10:
                temp += "0"
            temp += str(i)
            deck.append(temp)
    return deck

def prune_deck_of_cards(game_state):
    ''' prunes deck of cards - reads in game state and removes any cards that have already been played on the board '''
    global deck
    
    #print 'game_state\n' + str(game_state) + '\n'
    
    unavailable_cards = []
    for i in range(1,14):
        for j in range(1,3):
            temp = game_state['properties'+str(j)]['cards']['items']['position'+str(i)]
            if temp != None:
                unavailable_cards.append(temp)
    
    for x in unavailable_cards: # remove any occurrences of placed cards from the deck
        deck[:] = (value for value in deck if value != x)
    
    #print 'Pruned deck\n' + str(game_state)+'\n\n'
    
def simulateGame(game_state, row, card):
    ''' takes in game state and chosen row to place given card in. 
    randomly simulates rest of game and returns score '''
	
    game_state = simulate_append_card(game_state, row, card)    # append card to appropriate position in game state
    prune_deck_of_cards(game_state)
    
    global deck     # get available cards for placement 
    tdeck = deck[:]
    random.shuffle(tdeck)
    
    gs_copy = copy.deepcopy(game_state) # deepcopy copies all elements including nested ones 
    
    # populate empty slots in game board with random cards
    for i in range(1,14):
        for j in range(1,3):
            if gs_copy['properties'+str(j)]['cards']['items']['position'+str(i)] == None:
                gs_copy['properties'+str(j)]['cards']['items']['position'+str(i)] = tdeck.pop(0)
    
    scores = helpers.scoring_helper(gs_copy) # score game board # THIS LINE IS CAUSING ERRORS - NEED TO WORK OUT WHY THERES AN INDEX ERROR 
    p1score = 0 
    p2score = 0
    p1_multiplier = 1 
    p2_multiplier = 1
    if scores[3][0] == True: # p1 fouls, scores 0
        p1_multiplier = 0 
    if scores[3][1] == True: # p2 fouls, scores 0
        p2_multiplier = 0 
    p1score = (scores[0][1] + scores[1][1] + scores[2][1]) * p1_multiplier
    p2score = (scores[0][2] + scores[1][2] + scores[2][2]) * p2_multiplier
    print "Ai calculates potential score of ", p2score - p1score, "for placing", card, "in", row
    print "    ", scores
    print game_state['properties2'], "\nvs\n'", game_state['properties1']
    return p2score - p1score
    #return randint(0,50) # return random score between 0-50 inclusive for test purposes

def simulate_append_card(game_state, row, card):
    ''' pass in game_state + a card and destination row
    returns a modified game_state with that card added to that row '''
    
    global placed_cards_s
    global number_bottom
    global number_middle
    global number_top
    
    if card in placed_cards_s: # avoid duplicate placements 
        #print "AVOIDED PLACING A DUPLICATED", card + "."
        return game_state
    
    #print "Old AI board state:", str(game_state['properties2']['cards']['items']), '\n'
    
    if row == 1:
        for i in range(1,6):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_bottom += 1
                break
    
    elif row == 2:
        for i in range(6,11):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_middle += 1
                break

    elif row == 3:
        for i in range(11,14):
            if game_state['properties2']['cards']['items']['position'+str(i)] == None:
                game_state['properties2']['cards']['items']['position'+str(i)] = card
                placed_cards_s.append(card)
                number_top += 1
                break    
    
    else:
        print "Invalid row passed to simulate_append_card:\n", row
    
    #print "New AI board state:", str(game_state['properties2']['cards']['items']), '\n'
    return game_state
    
def chooseMove(game_state, card, iterations):
    ''' takes game state and dealt card as input, produces tree from monte carlo
    simulations and returns optimal move - 1 for bottom, 2 for middle, 3 for top '''
    
    if type(card) == type([]): # calculate first 5 cards to place
        if (len(card) == 5):
            moves = []
            for c in card:
                move = chooseMove(game_state, c, iterations) # store recommend row id placement for each card c 
                moves.append(move)
                #game_state = simulate_append_card(game_state,move,c) # simulate this placement for continuity - updates game_state
            print moves
            return moves
        else:
            print "Invalid amount of cards - need 5!"
            return None
    
    elif type(card) == type('') and len(card) == 3: # calculate 1 card placement
    
        find_valid_moves(game_state)  # finds free spaces in each row and records counts in global vars number_bottom, number_middle, number_top

        global number_top
        global numer_middle
        global number_bottom
        global num_top_first_count
        global deck
        
        #print "Current cards placed top,", number_top, ", middle,",number_middle,",bottom,",number_bottom,"and 1st it top",num_top_first_count,"\n"
        
        # booleans - True if there are free slots in row 
        valid_bottom = True
        valid_middle = True
        valid_top = True
        
        if number_bottom == 5:
            valid_bottom = False
        if number_middle == 5:
            valid_middle = False
        if number_top == 3 or num_top_first_count == 3:
            valid_top = False
        
        # if there is only one row with free slots save some processing time and just return that move without calculating scores
        if valid_bottom == False and valid_middle == False and valid_top == True:
            return 3 # top 
        elif valid_top == False and valid_bottom == False and valid_middle == True:
            return 2 # middle
        elif valid_middle == False and valid_top == False and valid_bottom == True:
            return 1 # bottom
        elif valid_bottom == False and valid_middle == False and valid_top == False:
            print "\nThere are no valid places to move! Check game state for duplicates/ errors!\nGame State:", game_state['properties2']
            #raw_input('waiting...')
            return None 
        
        deck = produce_deck_of_cards()
        prune_deck_of_cards(game_state)
        
        predicted_scores = [ [1,0], [2,0], [3,0] ] # first index: row choice, second index: total score
        for i in range (1,iterations):
            row = randint(1,3)  # select a random row 
            predicted_scores[row -1][1] = simulateGame(game_state, row, card) #then get estimated score for simulated game with card placed in that row
        
        #print str(game_state)
        
        t1 = predicted_scores[0][1]
        t2 = predicted_scores[1][1]
        t3 = predicted_scores[2][1]        
        
        # use slight weighting so that preference for placements is bottom > middle > top
        if t1 >= t2:
            if valid_bottom == True and t1 >= t3 :
                return 1             #bottom
            elif valid_top == True and t3 > t2:
                num_top_first_count += 1
                return 3             #top    
            elif valid_middle == True:
                return 2             #middle
            
        if t2 >= t1:
            if valid_middle == True and t2 >= t3:
                return 2             #middle
            elif valid_top == True:
                num_top_first_count += 1
                return 3             #top
                
        if t3 >= t1:
            if valid_top == True and t3 >= t2:
                num_top_first_count += 1
                return 3             #top
            elif valid_middle == True:
                return 2             #middle
                
        else:                       
            if valid_bottom == True:
                return 1 
            elif valid_middle == True:
                return 2 
            elif valid_top == True:
                num_top_first_count += 1
                return 3
            else:
                print "No valid placements available!"
                return None 
    
    else:
        print "Invalid cards. Need type: String e.g. 's01' (ace of spades)"
        return None

def place_one(game_state, card, iterations):
    ''' takes game_state, card and iterations as parameters
    determines optimal placement for card given game state 
    
    Test function - server calls chooseMove function directly'''
    
    row_counts = [0,0,0]
    x = 1
    global number_top
    for i in range(0,x):  # run x simulations of iterations each 
        number_top = 0 # reset
        chosen_row = chooseMove(game_state, card, iterations)
        row_counts[chosen_row -1] += 1
    print row_counts
    
    chosenrow = 0
    if row_counts[0] >= row_counts[1]:
        if row_counts[0] >= row_counts[2]:
            chosenrow = 'Bottom'
        else:
            chosenrow = 'Top'
    
    elif row_counts[1] >=  row_counts[0]:
        if row_counts[1] >= row_counts[2]:
            chosenrow = 'Middle'
        else:
            chosenrow = 'Top'
    
    else:
        chosenrow = 'Top'
   
    return chosenrow

def place_five_initial(game_state, cards, iterations):
    ''' takes game_state, cards array and iterations as parameters
    determines optimal placement for cards given game state 
    
    Test function - server calls chooseMove function directly'''
    
    count_row_1 = 0
    count_row_2 = 0
    count_row_3 = 0 
    
    illegal_moves = 0
    global number_top
    
    #row_counts = [0,0,0]
    x = 1
    for i in range(0,x):  # # run x simulations of iterations each 
        card_placements = [0,0,0,0,0]
        number_top = 0 # reset num top
        
        chosen_rows = chooseMove(game_state, cards, iterations)
        
        j = 0
        for row in chosen_rows:
            card_placements[j] += row
            j += 1
            
        cardid = 1
        t_count_top = 0
        for placement in card_placements:
            print "Place card", cardid, "in row", placement 
            if placement == 1:
                count_row_1 += 1
            elif placement == 2:
                count_row_2 += 1
            elif placement == 3:
                count_row_3 += 1
                t_count_top += 1
            else:
                print "AN EROR OCCURRED\n"
            cardid += 1
        
        if t_count_top > 3:
            print "Illegal amount of placements in top row!"
            illegal_moves += 1
        
        print "" #linebreak
    
    print "Row 1:", count_row_1, ", Row 2:", count_row_2, ", Row 3:", count_row_3
    
    print "There were", illegal_moves, "illegal recommended moves in this simulation.\n"
    
    return card_placements
    
    
if __name__ == "__main__":

    print "Test run: Modelling 100 simulations of placing cards!...\n"
    user_choice = raw_input(" Type 0 to test a single card,\n Type 1 to test 5 card initial placement.\n\
    Anything else: exit.\n")
    
    ### exit ###
    if user_choice not in ['0','1']:
        print "Exiting now..."
        quit()
    
    times_to_run = raw_input("How many test would you like to run? \n")
    
    valid = False
    try:
        times_to_run = int(times_to_run)
        valid = True 
    except:
        print "Invalid input! Required type: integer.\n"
    
    #### 1 card test ####
    if user_choice == "0" and valid == True:
        game_state = None
        card = 's01' # example test card (ace of spades)
        num_iterations = 500
        for i in range(0, times_to_run):
            chosenrow = place_one(game_state, card, num_iterations)
            print "Recommendation: Place card in", chosenrow, "row!"
    
    
    #### 5 card test ####
    elif user_choice == "1" and valid == True:
        
        game_state = None
        cards = ['s01', 'd01', 'h01', 'c10', 'd05']  # example test cards 
        num_iterations = 500
        placements_array = []
        for i in range(0, times_to_run):
            placements_array.append( place_five_initial(game_state, cards, num_iterations) )
        print "Simulations results: ", placements_array
    
    
    print "\nThis is a helper script implementing MCTS for OFCP.\n\
    Intended use: import module externally.\n"
    
    raw_input("Press Enter to continue...")