import time
from game_logic import GameLogic
from game_ui import GameUI
import keyboard

gl = GameLogic()
gui = GameUI()
gui.focusOnEmulatorScreen()

#print('test')
while 1:
    print("Updating Game State")

    gui.UpdateGameState()
    
    print("Calculating Action")
    next_action = gl.GetNextAction(gui.gs, gui.gv)
    print("Action: " + next_action.name)
    print(next_action.cards)
    
    if not gui.ProcessAction(next_action):
        break
    
    escape = keyboard.is_pressed("escape")
    if escape == 1:
        break

    
print('Game bot has been stopped.')