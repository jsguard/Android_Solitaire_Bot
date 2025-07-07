import time
import os
import sys
import random
from Card import Card
from GameState import GameState
from Action import Action
from datetime import datetime
from game_vals import GameVals
import cv2
import numpy as np
import platform
from  ctypes import *
from PIL import Image
import logging

class GameUI:
    time_delay=0.01
    gv = GameVals()
    gs = GameState()
    cxOffset = gv.cardcenterXoffset
    cyOffset = gv.cardcenterYoffset
    DecCount = 0
    lib = None
    Screenshot = None
    current_directory = os.getcwd()
    AndroidBridgePath = current_directory + '/platform-tools'
    AndroidBridgeLib = AndroidBridgePath + '/android_bridge.dll'

    def __init__(self):
        logfilename = 'solitaire_bot_log.txt'
        logging.basicConfig(filename=logfilename, encoding='utf-8', format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        print('Wait for few seconds connecting phone...')
        logging.info('Wait for few seconds connecting phone...')
        self.lib = cdll.LoadLibrary(self.AndroidBridgeLib)
        readyFlag = self.lib.android_bridge_init(self.AndroidBridgePath.encode('ASCII'))
        if not readyFlag:
            print('No devices connected.')
            logging.error('No devices connected.')
            exit(0)
        
        cmdstr = ' shell monkey -p com.smilerlee.klondike -c android.intent.category.LAUNCHER 1'
        self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))
    #######################################
    ### Helper Functions
    #######################################

    def focusOnEmulatorScreen(self):
        # Click inside the emulator screen to make sure it is in focus
        cmdstr = 'shell input tap 360 50'
        self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))

    def GetCardsFromRegion(self, x1, y1, x2, y2, precision = 0.90, caller = '', filterForSpecialCards = False):
        #print(caller)
        cardsRendered = []
        im = self.region_grabber((x1, y1, x2, y2))        
        #im.save('Debug_region.png')
        for crd,crdpath in self.gv.cards.items():
            #print(crd + ":" + crdpath)
            if filterForSpecialCards and int(crd[1:]) > 10:                
                precision = 0.95
            pos1, mval = self.imagesearcharea(crdpath, x1, y1, x2, y2, precision, im)
            if pos1[0] != -1:
                #print(crd + " detected")
                # TODO May be define a class for [card,pos_x,pos_y] tuple
                cardsRendered.append([crd,x1+pos1[0]+self.cxOffset,y1+pos1[1]+self.cxOffset])            
        return cardsRendered

    def GetCardsFromRegion_1(self, x1, y1, x2, y2, precision = 0.90, caller = '', filterForSpecialCards = False):
        #print(caller)
        cardsRendered = []
        im = self.region_grabber((x1, y1, x2, y2))        
        #im.save('Debug_region.png')
        maxv = 0
        rcrd = -1
        pos = [-1, -1]
        for crd,crdpath in self.gv.cards.items():
            #print(crd + ":" + crdpath)
            # if filterForSpecialCards and int(crd[1:]) > 10:                
            #     precision = 0.95
            pos1, mval = self.imagesearcharea(crdpath, x1, y1, x2, y2, 0, im)
            if maxv < mval:
                maxv = mval
                pos = pos1
                rcrd = crd

                #print(crd + " detected")
                # TODO May be define a class for [card,pos_x,pos_y] tuple
        if maxv > precision:
            cardsRendered.append([rcrd,x1+pos[0]+self.cxOffset,y1+pos[1]+self.cxOffset])            
        return cardsRendered

    # y3 represents top portion of bottom most card in column
    def GetSlicedCardsFromRegion(self, x1, y1, x2, y2, y3, caller = ''):
        #print(caller)        
        #print("y3: " + str(y3))
        newy2 = y2
##        if y3 != -1 and y3 > 400:
##            newy2 = y3

        cardsRendered = []
        im = self.region_grabber((x1, y1, x2, newy2))        
        #im.save('debug_region.png')
        indOfLastRenderedCard = -1

        for crd,crdpath in self.gv.sliced_cards.items():
            #print(crd + ":" + crdpath)
            crdNumber = int(crd[1:])
            if crdNumber > 10:
                pos1, mval = self.imagesearcharea(crdpath, x1, y1, x2, y2, 0.97, im)
            else:
                pos1, mval = self.imagesearcharea(crdpath, x1, y1, x2, y2, 0.96, im)
            if pos1[0] != -1:
                # If we missed a card in sequence, keep trying to find it
                if indOfLastRenderedCard != -1 and crdNumber > indOfLastRenderedCard+1:
                    cardFound = False
                    tryCount = 0

                    while cardFound == False and tryCount < 3:
                        # Keep trying to search missing number card
                        for ch in ['s','c','d','h']:
                            crdToFind = ch + str(indOfLastRenderedCard+1)
                            crdCandidatePath = self.gv.sliced_cards[crdToFind]
                            if crdNumber > 10:
                                pos2, mval = self.imagesearcharea(crdCandidatePath, x1, y1, x2, y2, 0.93, im)
                            else:
                                pos2, mval = self.imagesearcharea(crdCandidatePath, x1, y1, x2, y2, 0.97, im)
                            if pos2[0] != -1:
                                cardsRendered.append([crd,x1+pos1[0]+self.cxOffset,y1+pos1[1]+self.cxOffset])
                                cardFound = True
                                break
                        if cardFound == False:
                            print("Could not find card with index:" + str(indOfLastRenderedCard+1) + ". Trying again...")
                            logging.error("Could not find card with index:" + str(indOfLastRenderedCard+1) + ". Trying again...")
                            tryCount += 1

                    if cardFound == False:
                        print("Card not found.. initialization")
                        logging.error("Card not found.. initialization")
                        self.gs.ui_components_to_render['top_deck'] = []
                        self.gs.ui_components_to_render['columns'] = [1,2,3,4,5,6,7]
                        #exit(0)
                
                #print(crd + " detected")
                # TODO May be define a class for [card,pos_x,pos_y] tuple
                #print("Found card: " + crd)
                indOfLastRenderedCard = crdNumber
                cardsRendered.append([crd,x1+pos1[0]+self.cxOffset,y1+pos1[1]+self.cxOffset])  
                
        return cardsRendered


    def GetNewCardsInColumn(self, x1, y1, caller = ''):
        #print(caller)
        im = self.region_grabber((x1, y1, x1+self.gv.columnWidth, y1+50))
        #im.save('debug_new_card.png')
        absolute_path = os.path.join(os.getcwd(), self.gv.imageFolderName, 'Slices','NewCardBorder.png')
        pos, mval = self.imagesearcharea(absolute_path, x1, y1, x1+self.gv.columnWidth, y1+50, 0.70, None)
        if pos[0] != -1:
            return True
        return False


    def findImgAndClick(self,imageName, precision = 0.90):
        absolute_path = os.path.join(os.getcwd(), self.gv.imageFolderName, imageName)
        pos = self.imagesearch(absolute_path, precision)
        if pos[0] != -1:
            self.click_image(absolute_path, pos, "left", 0, False, offset=5)
            return True
        return False

    def findImage(self,imageName, precision = 0.90):
        absolute_path = os.path.join(os.getcwd(), self.gv.imageFolderName, imageName)
        pos = self.imagesearch(absolute_path, precision)
        if pos[0] != -1:
            return True
        return False    
    #######################################
    ### Main Functions
    #######################################

    def UpdateGameState(self):
        cmdstr = 'shell wm size'
        retB = self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))
        if retB:
            print('Image size checking has been done.')
            logging.info('Image size checking has been done.')
        else:
            print('Image size checking has been skipped.')
            logging.info('Image size checking has been skipped.')


        # Render game state
        self.focusOnEmulatorScreen()

        ret = self.lib.android_screen_capture()
        if not ret:
            print('Cannot capture screenshot of the phone.')
            logging.error('Cannot capture screenshot of the phone.')

        imgfile = self.AndroidBridgePath + '/screenshot.png'

        img = cv2.imread(imgfile)
        
        self.Screenshot = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                
        #############################
        # Capture top right draw deck
        #############################

        if "draw_deck" in self.gs.ui_components_to_render:
            self.gs.draw_deck_top_card.clear()  
            cardsRendered = self.GetCardsFromRegion_1(self.gv.drawDeckArea[0], self.gv.drawDeckArea[1],
             self.gv.drawDeckArea[2], self.gv.drawDeckArea[3], 0.95, "Capture Draw Deck", True)        
            if len(cardsRendered) > 0:
                self.gs.draw_deck_top_card = cardsRendered[0] 
            else:
                # Draw new card if possible
                print("Drawing a new card")
                logging.info("Drawing a new card")
                self.findImgAndClick('draw_deck_card.png')
                
                cardsRendered = self.GetCardsFromRegion(self.gv.drawDeckArea[0], self.gv.drawDeckArea[1],
             self.gv.drawDeckArea[2], self.gv.drawDeckArea[3], 0.98, "Capture Draw Deck", True)        
                if len(cardsRendered) > 0:
                    self.gs.draw_deck_top_card = cardsRendered[0] 

        #########################
        # Capture top Left area
        #########################

        if "top_deck" in self.gs.ui_components_to_render:
            self.gs.deck_cards_top.clear()
            cardsRendered = self.GetCardsFromRegion(self.gv.deckArea[0],self.gv.deckArea[1],self.gv.deckArea[2],self.gv.deckArea[3], 0.96, "Capture Deck")
            for crd in cardsRendered:
                self.gs.deck_cards_top.append(crd)

        #############################
        # Capture card columns
        #############################

        if "columns" in self.gs.ui_components_to_render:
            left = self.gv.columnsStart
            top = self.gv.columnsStartH
            down = self.gv.columnsEndH
            self.DecCount = 0

            currColumnCards = []
            currColumnAllCards = []
            currNewCardsInColumn = []
            currEmptyColumnIndices = []            
            for ind in self.gs.empty_column_indices:
                currEmptyColumnIndices.append(ind)
            
            for i in range(0,7):
                if (i+1) not in self.gs.ui_components_to_render['columns']:
                    currColumnCards.append(self.gs.column_cards[i])
                    currColumnAllCards.append(self.gs.column_all_cards[i])
                    currNewCardsInColumn.append(self.gs.new_cards_in_column[i])
                else:
                    print("Rendering Column " + str(i+1))
                    logging.info("Rendering Column " + str(i+1))
                    cardsRendered = self.GetCardsFromRegion_1(left, top, left+self.gv.columnWidth, down, 0.95, "Capture Column Cards", True)            
                    crdToAdd = []
                    if len(cardsRendered) > 0:
                        crdToAdd = cardsRendered[0]   
                    else:                        
                        if (i+1) not in currEmptyColumnIndices:
                            currEmptyColumnIndices.append(i+1)
                    currColumnCards.append(crdToAdd)
                    
                    # Render all sliced card in column
                    if len(crdToAdd) > 0:        
                        #print("crdtoadd:")
                        #print(crdToAdd)                      
                        slicedCardsRendered = self.GetSlicedCardsFromRegion(left, top, left+self.gv.columnWidth, down, crdToAdd[2]-self.cyOffset, "Capture All Column Cards")
                        if len(slicedCardsRendered) > 0 and slicedCardsRendered[0][0] != crdToAdd[0]:
                            slicedCardsRendered.insert(0,crdToAdd)
                    else:
                        slicedCardsRendered = self.GetSlicedCardsFromRegion(left, top, left+self.gv.columnWidth, down, -1, "Capture All Column Cards")

                    ColumnAllCardsToAdd = slicedCardsRendered
                    if len(slicedCardsRendered) == 0:
                        ColumnAllCardsToAdd = [crdToAdd]
                    currColumnAllCards.append(ColumnAllCardsToAdd)

                    if len(ColumnAllCardsToAdd[-1:][0]) > 0:
                        #print(ColumnAllCardsToAdd)
                        #print(ColumnAllCardsToAdd[-1:][0])
                        # Check if there are new cards in this column (flippable new cards)
                        NewCardExists = self.GetNewCardsInColumn(left, top)
                        if NewCardExists:
                            currNewCardsInColumn.append(1)
                        else:
                            currNewCardsInColumn.append(0)
                    else:
                        currNewCardsInColumn.append(0)
                left += self.gv.columnOffset

            self.gs.column_cards.clear()
            for crd in currColumnCards:
                self.gs.column_cards.append(crd)

            self.gs.empty_column_indices.clear()
            for crd in currEmptyColumnIndices:
                self.gs.empty_column_indices.append(crd)

            self.gs.column_all_cards.clear()
            for crd in currColumnAllCards:
                self.gs.column_all_cards.append(crd)

            self.gs.new_cards_in_column.clear()
            for crd in currNewCardsInColumn:
                self.gs.new_cards_in_column.append(crd)
    
        '''
        print("=====")
        print("ColumnCards:")
        print(self.gs.column_cards)
        print("=====")
        print("ColumnAllCards:")
        print(self.gs.column_all_cards)
        print("=====")
        print("NewCardsInColumn:")
        print(self.gs.new_cards_in_column)
        print("=====")
        print("DeckCards:")
        print(self.gs.deck_cards_top)
        print("=====")
        print("Draw deck card:")
        print(self.gs.draw_deck_top_card)
        print("=====")
        print("Empty Column Indices:")
        print(self.gs.empty_column_indices)
        '''
        return

    def ProcessAction(self, a):
        print("Processing action: " + a.name)
        logging.info("Processing action: " + a.name)
        print(a.cards)
        logging.info(a.cards)
        #return
        
        if self.findImage('NewGame.png'):
            print('---------------------- Congratulation !!! --------------------')
            logging.info('---------------------- Congratulation !!! --------------------')
            return False
        if a.name == 'DrawNewCard':
            self.DecCount = self.DecCount + 1
            if self.DecCount > 8:
                print('Game Logic has been stuck!!!')
                logging.warning('Game Logic has been stuck!!!')
                self.gs.ui_components_to_render['top_deck'] = []
                self.gs.ui_components_to_render['draw_deck'] = []
                self.gs.ui_components_to_render['columns'] = [1,2,3,4,5,6,7]
                ##return False

            if not self.findImgAndClick('draw_deck_card.png'):
                self.findImgAndClick('redraw_deck_card.png')
        elif a.name == 'MoveCardToDeck':
            self.DecCount = 0
            print(a.cards[0])
            logging.info(a.cards[0])
            cmdstr = 'shell input tap ' + str(a.cards[0][1]) + ' ' + str(a.cards[0][2])
            self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))

        elif a.name == 'MoveCardToColumn':            
            self.DecCount = 0
            #print(a.cards)
            cmdstr = 'shell input tap ' + str(a.cards[0][1]) + ' ' + str(a.cards[0][2])
            self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))

        return True

    '''

    grabs a region (topx, topy, bottomx, bottomy)
    to the tuple (topx, topy, width, height)

    input : a tuple containing the 4 coordinates of the region to capture

    output : a PIL image of the area selected.

    '''
    def region_grabber(self, region):
        x1 = region[0]
        y1 = region[1]
        x2 = region[2]
        y2 = region[3]

        return self.Screenshot.crop([x1, y1, x2, y2])


    '''

    Searchs for an image within an area

    input :

    image : path to the image file (see opencv imread for supported types)
    x1 : top left x value
    y1 : top left y value
    x2 : bottom right x value
    y2 : bottom right y value
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    im : a PIL image, usefull if you intend to search the same unchanging region for several elements

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

    '''


    def imagesearcharea(self, image, x1, y1, x2, y2, precision=0.8, im=None):
        if im is None:
            im = self.region_grabber(region=(x1, y1, x2, y2))
            # im.save('testarea.png') usefull for debugging purposes, this will save the captured region as "testarea.png"

        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image, 0)

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < precision:
            return [-1, -1], 0
        return max_loc, max_val


    '''

    click on the center of an image with a bit of random.
    eg, if an image is 100*100 with an offset of 5 it may click at 52,50 the first time and then 55,53 etc
    Usefull to avoid anti-bot monitoring while staying precise.

    this function doesn't search for the image, it's only ment for easy clicking on the images.
    
    '''


    def click_image(self, image, pos, action, timestamp, dclick,offset=5):
        img = cv2.imread(image)    
        height, width, channels = img.shape
        cmdstr = 'shell input tap ' + str(pos[0] + int(self.r(width / 2, offset))) + ' ' + str(pos[1] + int(self.r(height / 2, offset)))
        self.lib.android_bridge_cmd(cmdstr.encode('ASCII'))

        ret = self.lib.android_screen_capture()
        if not ret:
            print('Cannot capture screenshot of the phone.')
            logging.error('Cannot capture screenshot of the phone.')

        imgfile = self.AndroidBridgePath + '/screenshot.png'
        img = cv2.imread(imgfile)

        self.Screenshot = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
    '''
    Searchs for an image on the screen

    input :

    image : path to the image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    im : a PIL image, usefull if you intend to search the same unchanging region for several elements

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

    '''


    def imagesearch(self, image, precision=0.8):
        im = self.Screenshot
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image, 0)
        template.shape[::-1]

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < precision:
            return [-1, -1]
        return max_loc

    def r(self, num, rand):
        return num + rand * random.random()

    def log_info(self, str):
        print(str)
        logging.info(str)