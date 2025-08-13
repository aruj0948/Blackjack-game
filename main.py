import pygame
from pygameRogers import *
import random

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (200,0,0) # Dark Red
GREEN = (0,150,0) # Dark Green
BLUE = (29,25,59) # Dark Blue

# Create new game
g = Game(800,600)

# Load Resources -> Images, Fonts, Backgrounds
gameFont = g.makeFont("Arial",38)
titleFont = g.makeFont("Arial",45)

simpleBackground = g.makeBackground(GREEN)
cardBackground = g.makeBackground("assets\Table.png") # Blackjack table image

amount1 = 500 # Chip option 1
amount2 = 1000 # Chip option 2
amount3 = 2500 # Chip option 3
chips = 0 # Player's total chips
betAmount = 0 # Current bet amount

diamondPics = []
for i in range(2,15):
    diamondPics.append(g.makeSpriteImage("assets\cards\DIAMONDS" + str(i) + ".jpg"))
heartPics = []
for i in range(2,15):
    heartPics.append(g.makeSpriteImage("assets\cards\HEARTS" + str(i) + ".jpg"))
spadePics = []
for i in range(2,15):
    spadePics.append(g.makeSpriteImage("assets\cards\SPADES" + str(i) + ".jpg"))
clubPics = []
for i in range(2,15):
    clubPics.append(g.makeSpriteImage("assets\cards\CLUBS" + str(i) + ".jpg"))

# Card back image (shown for dealer's hidden card)
topCard = g.makeSpriteImage("assets\cards\TOP.jpg")

# Create rooms
r1 = Room("Home Screen", simpleBackground)
r2 = Room("Game", cardBackground)
r3 = Room("Game Over", cardBackground)

g.addRoom(r1)
g.addRoom(r2)
g.addRoom(r3)

# Classes for Game Objects ------------------------------------------------------------------

# Card class to represent a single playing card
class Card(GameObject):
    def __init__(self, picture, value, suit):
        GameObject.__init__(self, picture)
        
        # Attributes

        # Face cards=10, Ace=11, others keep their value
        if value > 10 and value != 14:
            self.value = 10 # Face Cards

        elif value == 14:
            self.value = 11 # Ace

        else:
            self.value = value # 2 - 10

        self.suit = suit # H, D, C, S

# MainDeck builds and shuffles a full deck of 52 cards
class MainDeck(GameObject):

    def __init__(self):
        GameObject.__init__(self)

        self.deck = [] # List to hold all 52 cards
        
        # Loop from 0 to 12 (13 values: 2–14)
        for i in range(0, len(diamondPics)):
            # Add one card of each suit with value i+2 (2 to 14)
            self.deck.append(Card(diamondPics[i], (i+2), "D"))
            self.deck.append(Card(heartPics[i], (i+2), "H"))
            self.deck.append(Card(spadePics[i], (i+2), "S"))
            self.deck.append(Card(clubPics[i], (i+2), "C"))

        # Shuffle the deck after building
        random.shuffle(self.deck)

    def deal(self,num):
        # Deals "num" of cards from the deck
        tempList = [] # List of drawn cards

        for i in range(0,num):

            if len(self.deck) == 0:  # If deck is empty
                self.mainDeck = MainDeck() # Create new shuffled deck
                self.deck = self.mainDeck.deck # Establishes the deck

            c = self.deck.pop(0) # Gets the card
            tempList.append(c) # Adds card to list
        
        return tempList 

# Handles dealer's cards and score
class Dealer(GameObject):

    def __init__(self, xPos, yPos):
        GameObject.__init__(self)

        self.startingX = xPos # X position for first card
        self.startingY = yPos # Y position for cards
        self.count = 0 # Current hand value
        self.killList = [] # Cards to remove
        self.dealerCards = [] # Cards in hand
    
    # Display cards (num=1 shows first card face down)
    def cardDisplay(self,num):

        # Clear previous cards
        for card in self.killList:
            card.kill()
            self.count = 0

        if num == 1: # Initial deal (hide first card)
            for i in range(0,len(self.dealerCards)):
                if i == 0: # First card face down
                    card = GameObject(topCard) # Face down card
                    card.rect.x = self.startingX
                    card.rect.y = self.startingY
                    r2.addObject(card)
                    self.killList.append(card)
                else:
                    card = self.dealerCards[i] # Face up card
                    card.rect.x = self.startingX + (15 * i) # Change card location
                    card.rect.y = self.startingY
                    r2.addObject(card)
                    self.count += card.value # Add to current hand value

                self.killList.extend(self.dealerCards) # add cards in hand to the kill list
        else: # If player turn is over, show all cards
            for i in range(0,len(self.dealerCards)):
                card = self.dealerCards[i]
                card.rect.x = self.startingX + (15 * i) # Changing X-pos of each card
                card.rect.y = self.startingY
                r2.addObject(card)
                self.count += card.value # Update card value
            self.killList.extend(self.dealerCards)

        # Handle bust cases by converting Aces 11 -> 1 if needed
        if self.count > 21:
            for card in self.dealerCards:
                if card.value == 11: # If its a ace
                    card.value = 1 # Ace value -> 1
                    self.count = 0 # Reset hand value

                    # Recalculate total
                    for i in self.dealerCards:
                        self.count += i.value

        dealerValue.setText(str(self.count)) # Update display

# Handles player's cards and score
class Player(GameObject):

    def __init__(self, xPos, yPos):
        GameObject.__init__(self)

        # Attributes
        self.startingX = xPos # X position for first card
        self.startingY = yPos # Y position for cards
        self.count = 0 # Current hand value
        self.killList = [] # Cards to remove
        self.playerCards = [] # Cards in hand

    # Display cards and calculate score
    def cardDisplay(self):
        
        # Clear previous cards
        for card in self.killList:
            card.kill()
            self.count = 0

        # Display each card
        for i in range(0,len(self.playerCards)):
            card = self.playerCards[i]
            card.rect.x = self.startingX + (15 *i) # Changing X-pos of each card
            card.rect.y = self.startingY
            r2.addObject(card)

            self.count += card.value # Add to current hand value
        
        self.killList.extend(self.playerCards) # add cards in hand to the kill list

        # Handle bust cases by converting Aces 11 -> 1 if needed
        if self.count > 21:
            for card in self.playerCards:
                if card.value == 11: # If its a ace
                    card.value = 1 # Ace value -> 1
                    self.count = 0 # Reset hand value

                    # Recalculate total
                    for i in self.playerCards:
                        self.count += i.value

        playerValue.setText(str(self.count)) # Update display

# Button to go to the next room
class GameStart(TextRectangle):

    # To initialize the objects sent
    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
        
    def update(self):
        self.checkMousePressedOnMe(event)

        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False
            totalChipAmount.setText("Chip Amount: " + str(chips)) # show the amount of chips chosen
            g.nextRoom()

# Chip selection buttons on home screen
class Chip(TextRectangle):

    # To initialize the objects sent
    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor, chipAmount):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
        self.chipAmount = chipAmount # Amount this chip represents

    def update(self):
        global chips
        self.checkMousePressedOnMe(event)

        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False
            chips = self.chipAmount  # Set player's total chips
            
            # Remove chip selection buttons
            chip1.kill()
            chip2.kill()
            chip3.kill()
            chooseChips.kill()
            
            r1.addObject(game)  # Add start game button

# Betting amount during the games
class ChipsNumber(TextRectangle):

    # To initialize the objects sent
    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor, chipAmount):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
        self.chipAmount = chipAmount # Amount of the chip

    # Handles betting
    def update(self):
        global chips
        global betAmount

        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False

            if self.chipAmount == "Everything": # All-in
                betAmount += chips
                chips = 0
                self.kill()

            elif chips - self.chipAmount >= 0: # Normal bet
                betAmount += self.chipAmount
                chips -= self.chipAmount

            # Update displays
            totalChipAmount.setText("Chip Amount: " + str(chips))
            currentBettingAmount.setText("Bet Amount: " + str(betAmount))
            r2.addObject(betOver) # Add done betting button

# Done Betting confirmation button            
class DoneBetting(TextRectangle):

    # To initialize the objects sent
    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)

    # Finish betting phase
    def update(self):
        self.checkMousePressedOnMe(event)

        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False
            # Clean up betting display by removing betting buttons
            chipAmount1.kill()
            chipAmount2.kill()
            chipAmount3.kill()
            allIn.kill()
            self.kill()
            r2.addObject(deal) # Add deal button

# Deal initial cards button
class DealCards(TextRectangle):

    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)

    # Deal initial hands
    def update(self):
        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False

            gameWinner.setText("") # Clear previous result
            
            # Deal 2 cards each
            playerCard.playerCards = mainDeck.deal(2)
            dealerCard.dealerCards = mainDeck.deal(2)
            
            # Display cards (dealer shows one face down)
            playerCard.cardDisplay()
            dealerCard.cardDisplay(1)

            # Reset counts
            playerCard.count = 0
            dealerCard.count = 0

            # Add hit/stand buttons
            r2.addObject(hit)
            r2.addObject(stand)
            self.kill() # Remove deal button

# Hit button (request another card)
class Hit(TextRectangle):

    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
    
    # Handle hit action
    def update(self):
        global betAmount
        global chips
        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False

            # Deal one card to player
            deal = mainDeck.deal(1)
            playerCard.playerCards.extend(deal) # Add the drawn card to the cards in hand
            playerCard.cardDisplay() # Display the new cards

            # Check for bust
            if playerCard.count > 21:
                gameWinner.setText("Bust! Dealer Won")
                betAmount = 0  # Lose bet

                # Clean up display
                stand.kill()
                self.kill()
                r2.addObject(resetGame)
                r2.addObject(toWin)

            # Update displays    
            totalChipAmount.setText("Chip Amount: " + str(chips))
            currentBettingAmount.setText("Bet Amount: " + str(betAmount))

# Stand button (keep current hand)
class Stand(TextRectangle):

    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)

    # Handle stand action
    def update(self):
        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False
            global betAmount
            global chips
            hit.kill() # Remove hit button
            
            # Show all cards
            playerCard.cardDisplay()
            dealerCard.cardDisplay(2)

            # Dealer draws until 17 or higher
            while dealerCard.count <= 16:
                deal = mainDeck.deal(1)
                dealerCard.dealerCards.extend(deal)
                dealerCard.cardDisplay(2)

            # Determine winner
            if dealerCard.count == playerCard.count: # Tie
                gameWinner.setText("It's a tie")
                chips += betAmount # Return bet
                betAmount = 0

            elif dealerCard.count > 21 or dealerCard.count < playerCard.count: # Player wins
                if playerCard.count == 21:
                    betAmount *= 2  # Win 2x bet
                else:
                    betAmount *= 1.5  # Win 1.5x bet

                gameWinner.setText("Player Won")
                chips += betAmount
                betAmount = 0

            elif dealerCard.count > playerCard.count: # Dealer wins
                gameWinner.setText("Dealer Won!")
                betAmount = 0 # Lose bet

            # Update displays
            totalChipAmount.setText("Chip Amount: " + str(chips))
            currentBettingAmount.setText("Bet Amount: " + str(betAmount))
            
            # Add reset options
            r2.addObject(resetGame)
            r2.addObject(toWin)
            stand.kill() # Remove stand button

# Reset game state
class Reset(TextRectangle):

    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
    
    def update(self):
        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False

            # Add betting buttons, kind of a loop
            r2.addObject(chipAmount1)
            r2.addObject(chipAmount2)
            r2.addObject(chipAmount3)
            r2.addObject(allIn)
            
            # Clear all cards
            for i in dealerCard.killList:
                i.kill()
            for i in playerCard.playerCards:
                i.kill()
            
            # Check for game over (no chips left)
            if betAmount == 0 and chips == 0:
                winText.setText("Game Over! You lost")
                g.nextRoom() # Go to game over screen

            # Reset displays
            playerValue.setText("0")
            dealerValue.setText("0")

            # Clean up
            toWin.kill()
            self.kill()

# Cash Out button
class WonAmount(TextRectangle):

    def __init__(self, text, xPos, yPos, font, textColor, buttonWidth=None, buttonHeight=None, buttonColor=None):
        TextRectangle.__init__(self,text, xPos, yPos, font, textColor, buttonWidth, buttonHeight, buttonColor)
    
    # Handle cashing out
    def update(self):
        self.checkMousePressedOnMe(event)
        if self.mouseHasPressedOnMe and event.type == pygame.MOUSEBUTTONUP:
            self.mouseHasPressedOnMe = False

            winText.setText("You have won a grand total of $" + str(chips)) # Show won amount
            g.nextRoom() # Go to game over screen

# Initialize Game Objects
mainDeck = MainDeck()

# Home screen objects
title = TextRectangle("Blackjack", 0, 0, titleFont, WHITE, g.windowWidth, 60, BLUE)
game = GameStart("Start Game", (g.windowWidth/2)-110,(g.windowHeight/2)-25,titleFont, WHITE, 220, 50, BLUE)
chooseChips = TextRectangle("Choose your chip amount", (g.windowWidth/2)-225,(g.windowHeight/2)-27.5,titleFont, WHITE, 450, 55, RED)

# Chip selection buttons
chip1 = Chip(str(amount1),(g.windowWidth/2)-145,(g.windowHeight*0.75)-25,gameFont, WHITE, 90, 50, RED,amount1)
chip2 = Chip(str(amount2),(g.windowWidth/2)-45,(g.windowHeight*0.75)-25,gameFont, WHITE, 90, 50, RED,amount2)
chip3 = Chip(str(amount3),(g.windowWidth/2)+55,(g.windowHeight*0.75)-25,gameFont, WHITE, 90, 50, RED,amount3)

# Add objects to home screen
r1.addObject(title)
r1.addObject(chooseChips)
r1.addObject(chip1)
r1.addObject(chip2)
r1.addObject(chip3)

# Game room
totalChipAmount = TextRectangle("Chip Amount: " + str(chips), 10, 65, gameFont,WHITE)
currentBettingAmount = TextRectangle("Bet Amount: " + str(betAmount), 10, 100, gameFont,WHITE)

# Betting buttons
chipAmount1 = ChipsNumber(str(100),10, 160,gameFont, WHITE, 90, 50, RED,100)
chipAmount2 = ChipsNumber(str(300),10, 220,gameFont, WHITE, 90, 50, RED,300)
chipAmount3 = ChipsNumber(str(500),10, 280,gameFont, WHITE, 90, 50, RED,500)
allIn = ChipsNumber("All in?",10, 340,gameFont, WHITE, 90, 50, RED, "Everything")
betOver = DoneBetting("Done Betting?",10, 400,gameFont, WHITE, 300, 50, RED)

# Player/dealer labels
dealer = TextRectangle("Dealer", (g.windowWidth*0.75),(g.windowHeight*0.25)-22.5,gameFont,BLUE, 100, 45,WHITE)
player = TextRectangle("Player", (g.windowWidth*0.75),(g.windowHeight*0.75)-22.5,gameFont,BLUE, 100, 45,WHITE)

# Value display beside player/display labels
playerValue = TextRectangle(str(0), (g.windowWidth*0.75)-50,(g.windowHeight*0.75)-22.5, gameFont,WHITE)
dealerValue = TextRectangle(str(0), (g.windowWidth*0.75)-50,(g.windowHeight*0.25)-22.5, gameFont,WHITE)

# Game action buttons
deal = DealCards("Deal",(g.windowWidth/2)-50,(g.windowHeight/2)-22.5,gameFont,BLUE, 100, 45,WHITE)
hit = Hit("Hit",(g.windowWidth*0.25)-50,(g.windowHeight/2)-22.5,gameFont,BLUE, 100, 45,WHITE)
stand = Stand("Stand",(g.windowWidth*0.75)-50,(g.windowHeight/2)-22.5,gameFont,BLUE, 100, 45,WHITE)
resetGame = Reset("Reset Game",(g.windowWidth/2)-125,(g.windowHeight/2)-22.5,gameFont,BLUE, 250, 45,WHITE)

# Initialize player and dealer card handlers
playerCard = Player((g.windowWidth/2)-30, (g.windowHeight*0.75)-50)
dealerCard = Dealer( (g.windowWidth/2)-30, (g.windowHeight*0.25)-50)

# Who won and cash out buttons
gameWinner = TextRectangle("", 0, 0, titleFont, GREEN, g.windowWidth, 55, WHITE)
toWin = WonAmount("Cash Out?",(g.windowWidth)-210,(g.windowHeight)-55,gameFont,BLUE, 200, 45,WHITE)

# Adding objects to r2
r2.addObject(chipAmount1)
r2.addObject(chipAmount2)
r2.addObject(chipAmount3)
r2.addObject(allIn)
r2.addObject(currentBettingAmount)
r2.addObject(totalChipAmount)
r2.addObject(dealer)
r2.addObject(player)
r2.addObject(dealerValue)
r2.addObject(playerValue)
r2.addObject(gameWinner)

# Game Over 
winText = TextRectangle("", (g.windowWidth/2)-300,(g.windowHeight/2)-25,gameFont,WHITE,600,50,BLUE)
r3.addObject(winText)

# Start Game --------------------------------------------------------------------------------
g.start()
while g.running:

    # Limit the game execution framerate
    dt = g.clock.tick(60)

    # Check for events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            g.stop()
    
    # Update the gamestate of all the objects
    g.currentRoom().updateObjects()

    # render the background to the window surface
    g.currentRoom().renderBackground(g)

    # Render the object images to the background
    g.currentRoom().renderObjects(g)

    # Draw everything on the screen
    pygame.display.flip()

pygame.quit()