import os

class GameVals:
    cards = {}
    sliced_cards = {}
    borders = []

    # Variables related to screen size
    ScreenSize = "FullScreen"
    imageFolderName = 'Images'

    def __init__(self):

        if self.ScreenSize == "FullScreen":            
            #self.imageFolderName = 'FullScreenImages'
            self.imageFolderName = 'MobileImages'

            ### For Android
            self.drawDeckArea = [410, 90, 715, 250]
            self.deckArea = [7, 90, 410, 250]
            self.columnsStart = 5
            self.columnsStartH = 250
            self.columnsEndH = 1000
            self.columnWidth = 108
            self.columnOffset = 100
            self.cardcenterXoffset = 25
            self.cardcenterYoffset = 25

            ### For desktop
            # self.drawDeckArea = [330, 70, 750, 300]
            # self.deckArea = [850, 70, 1600, 300]
            # self.columnsStart = 325
            # self.columnsStartH = 325
            # self.columnsEndH = 1050
            # self.columnWidth = 175
            # self.columnOffset = 182
            # self.cardcenterXoffset = 25
            # self.cardcenterYoffset = 25

        for i in range(1,5):
            borderName = 'border' + str(i) + '.png'
            self.borders.append(borderName)
        
        for i in range(1,14):
            for ch in ['c','d','h','s']:
                card = ch+str(i) 
                cardpath = os.path.join(os.getcwd(), self.imageFolderName, card + '.png') 
                sliceCardPath = os.path.join(os.getcwd(), self.imageFolderName, 'Slices', card + '.png') 
                self.cards[card] = cardpath     
                self.sliced_cards[card] = sliceCardPath
