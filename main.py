import time
from game_logic import GameLogic
from game_ui import GameUI
import keyboard

gl = GameLogic()
gui = GameUI()
gui.focusOnEmulatorScreen()

#print('test')
while 1:
    gui.log_info("Updating Game State")

    gui.UpdateGameState()
    
    gui.log_info("Calculating Action")
    next_action = gl.GetNextAction(gui.gs, gui.gv)
    gui.log_info("Action: " + next_action.name)
    gui.log_info(next_action.cards)
    
    if not gui.ProcessAction(next_action):
        break
    
    escape = keyboard.is_pressed("escape")
    if escape == 1:
        break

    
gui.log_info('Game bot has been stopped.')