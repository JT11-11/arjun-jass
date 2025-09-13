# Structure of the App
`main.py` goes through each game
`/game` these are where the games are stored, each games should inherit from the `Game` abstract class
`/llm` the directory where different LLM behaviours are stored

# main.py
run through each game type and the associated config
it initializes the game and injects the config into the game
simulates the game
while simulating the game, the results are saved into the csv_file
