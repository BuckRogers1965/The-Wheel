import pygame
import json
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 800
FPS = 60
BACKGROUND = (160, 160, 160) 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (65, 105, 225)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# Wheel values
WHEEL_VALUES = [500, 550, 600, 650, 700, 750, 800, 850, 900, 300, 400, 450]
WHEEL_COLORS = [RED, BLUE, GREEN, YELLOW, RED, BLUE, GREEN, YELLOW, RED, BLUE, GREEN, YELLOW]

VOWELS = set('AEIOU')
VOWEL_COST = 250

class WheelGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("The Wheel")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 60)
        self.huge_font = pygame.font.Font(None, 72)
        
        # Load puzzles
        self.puzzles = self.load_puzzles()
        self.current_puzzle = None
        self.current_category = ""
        self.revealed = []
        self.guessed_letters = set()
        
        # Wheel
        self.wheel_angle = 0
        self.wheel_spinning = False
        self.wheel_speed = 0
        self.current_value = 0
        
        # Score
        self.score = 0
        
        # Game state
        self.can_guess = False
        self.message = ""
        
        self.new_puzzle()
    
    def load_puzzles(self):
        """Load puzzles from JSON file, or use defaults if file doesn't exist"""
        try:
            with open('puzzles.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default puzzles
            default = {
                "Famous Phrases": [
                    "THE EARLY BIRD GETS THE WORM",
                    "A PENNY SAVED IS A PENNY EARNED",
                    "ACTIONS SPEAK LOUDER THAN WORDS",
                    "BETTER LATE THAN NEVER"
                ],
                "Movies": [
                    "THE WIZARD OF OZ",
                    "GONE WITH THE WIND",
                    "STAR WARS",
                    "BACK TO THE FUTURE"
                ],
                "Places": [
                    "NEW YORK CITY",
                    "GRAND CANYON",
                    "EIFFEL TOWER",
                    "GOLDEN GATE BRIDGE"
                ]
            }
            # Save default puzzles
            with open('puzzles.json', 'w') as f:
                json.dump(default, f, indent=2)
            return default
    
    def new_puzzle(self):
        """Start a new puzzle"""
        self.current_category = random.choice(list(self.puzzles.keys()))
        self.current_puzzle = random.choice(self.puzzles[self.current_category]).upper()
        self.revealed = ['_' if c.isalpha() else c for c in self.current_puzzle]
        self.guessed_letters = set()
        self.current_value = 0
        self.can_guess = False
        self.message = ""
    
    def spin_wheel(self):
        """Start spinning the wheel"""
        if not self.wheel_spinning and not self.can_guess:
            self.wheel_spinning = True
            self.wheel_speed = random.uniform(15, 25)
            self.message = "Spinning..."
    
    def update_wheel(self):
        """Update wheel animation"""
        if self.wheel_spinning:
            self.wheel_angle += self.wheel_speed
            self.wheel_speed *= 0.98  # Deceleration
            
            if self.wheel_speed < 0.1:
                self.wheel_spinning = False
                # Calculate which segment we landed on
                normalized_angle = self.wheel_angle % 360
                segment = int((normalized_angle / 360) * len(WHEEL_VALUES))
                self.current_value = WHEEL_VALUES[segment]
                self.can_guess = True
                self.message = f"Landed on ${self.current_value}!"
    
    def draw_wheel(self):
        """Draw the spinning wheel"""
        center_x, center_y = 200, 200
        radius = 130
        
        # Draw wheel segments
        num_segments = len(WHEEL_VALUES)
        angle_per_segment = 360 / num_segments
        
        for i in range(num_segments):
            start_angle = math.radians(self.wheel_angle + i * angle_per_segment)
            end_angle = math.radians(self.wheel_angle + (i + 1) * angle_per_segment)
            
            # Draw segment
            points = [
                (center_x, center_y),
                (center_x + radius * math.cos(start_angle), 
                 center_y + radius * math.sin(start_angle)),
                (center_x + radius * math.cos(end_angle), 
                 center_y + radius * math.sin(end_angle))
            ]
            pygame.draw.polygon(self.screen, WHEEL_COLORS[i], points)
            pygame.draw.polygon(self.screen, BLACK, points, 2)
            
            # Draw value
            mid_angle = (start_angle + end_angle) / 2
            text_x = center_x + (radius * 0.65) * math.cos(mid_angle)
            text_y = center_y + (radius * 0.65) * math.sin(mid_angle)
            text = self.small_font.render(str(WHEEL_VALUES[i]), True, WHITE)
            text_rect = text.get_rect(center=(text_x, text_y))
            self.screen.blit(text, text_rect)
        
        # Draw center circle
        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 25)
        pygame.draw.circle(self.screen, GOLD, (center_x, center_y), 20)
        
        # Draw pointer at top
        pygame.draw.polygon(self.screen, RED, [
            (center_x, center_y - radius - 30),
            (center_x - 20, center_y - radius - 10),
            (center_x + 20, center_y - radius - 10)
        ])
        pygame.draw.polygon(self.screen, BLACK, [
            (center_x, center_y - radius - 30),
            (center_x - 20, center_y - radius - 10),
            (center_x + 20, center_y - radius - 10)
        ], 3)

    def draw_puzzle(self):
        """Draw the puzzle board stacked like the real game"""
        x_start = 500
        y_start = 120
        box_size = 60
        gap = 6
        max_per_row = 13
        
        # Draw category
        cat_text = self.large_font.render(self.current_category, True, BLUE)
        cat_rect = cat_text.get_rect(center=(925, 60))
        self.screen.blit(cat_text, cat_rect)
        
        # Split into words and build rows without breaking words
        words = self.current_puzzle.split(' ')
        rows = []
        current_row = []
        current_count = 0
        char_index = 0
        
        for word in words:
            word_length = len(word)
            space_needed = word_length + (0.5 if current_count > 0 else 0)
            
            # If adding this word exceeds limit, start new row
            if current_count > 0 and current_count + space_needed > max_per_row:
                rows.append(current_row)
                current_row = []
                current_count = 0
            
            # Add space before word if not first word in row
            if current_count > 0:
                current_row.append(char_index)
                char_index += 1
                current_count += 0.5
            
            # Add all letters of the word
            for letter in word:
                current_row.append(char_index)
                char_index += 1
                current_count += 1
        
        if current_row:
            rows.append(current_row)
        
        # Draw each row centered
        y = y_start
        
        for row in rows:
            # Calculate row width
            row_width = 0
            for idx in row:
                if self.current_puzzle[idx] == ' ':
                    row_width += box_size // 2
                else:
                    row_width += box_size + gap
            
            # Center the row
            x = x_start + (850 - row_width) // 2
            
            for idx in row:
                char = self.current_puzzle[idx]
                revealed_char = self.revealed[idx]
                
                if char == ' ':
                    x += box_size // 2
                else:
                    # Draw box
                    color = WHITE if revealed_char == '_' else LIGHT_GRAY
                    pygame.draw.rect(self.screen, color, (x, y, box_size, box_size))
                    pygame.draw.rect(self.screen, BLACK, (x, y, box_size, box_size), 3)
                    
                    # Draw letter
                    if revealed_char != '_':
                        letter = self.large_font.render(revealed_char, True, BLACK)
                        letter_rect = letter.get_rect(center=(x + box_size // 2, y + box_size // 2))
                        self.screen.blit(letter, letter_rect)
                    
                    x += box_size + gap
            
            y += box_size + gap + 8
    
    def draw_puzzle_old(self):
        """Draw the puzzle board stacked like the real game"""
        x_start = 500
        y_start = 120
        box_size = 60
        gap = 6
        max_per_row = 13
        
        # Draw category
        cat_text = self.large_font.render(self.current_category, True, BLUE)
        cat_rect = cat_text.get_rect(center=(975, 60))
        self.screen.blit(cat_text, cat_rect)
        
        # Split puzzle into rows that fit
        chars = list(self.current_puzzle)
        rows = []
        current_row = []
        current_count = 0
        
        for i, char in enumerate(chars):
            if char == ' ':
                # Check if we should break to new line
                if current_count >= max_per_row - 2:
                    rows.append(current_row)
                    current_row = []
                    current_count = 0
                else:
                    current_row.append(i)
                    current_count += 0.5  # Space takes half width
            else:
                if current_count >= max_per_row:
                    rows.append(current_row)
                    current_row = [i]
                    current_count = 1
                else:
                    current_row.append(i)
                    current_count += 1
        
        if current_row:
            rows.append(current_row)
        
        # Draw each row centered
        y = y_start
        
        for row in rows:
            # Calculate row width
            row_width = 0
            for idx in row:
                if self.current_puzzle[idx] == ' ':
                    row_width += box_size // 2
                else:
                    row_width += box_size + gap
            
            # Center the row
            x = x_start + (850 - row_width) // 2
            
            for idx in row:
                char = self.current_puzzle[idx]
                revealed_char = self.revealed[idx]
                
                if char == ' ':
                    x += box_size // 2
                else:
                    # Draw box
                    color = WHITE if revealed_char == '_' else LIGHT_GRAY
                    pygame.draw.rect(self.screen, color, (x, y, box_size, box_size))
                    pygame.draw.rect(self.screen, BLACK, (x, y, box_size, box_size), 3)
                    
                    # Draw letter
                    if revealed_char != '_':
                        letter = self.large_font.render(revealed_char, True, BLACK)
                        letter_rect = letter.get_rect(center=(x + box_size // 2, y + box_size // 2))
                        self.screen.blit(letter, letter_rect)
                    
                    x += box_size + gap
            
            y += box_size + gap + 8
    
    def draw_guessed_letters(self):
        """Draw already guessed letters"""
        text = self.font.render("Guessed Letters:", True, BLACK)
        self.screen.blit(text, (550, 420))
        
        # Separate consonants and vowels
        consonants = sorted([l for l in self.guessed_letters if l not in VOWELS])
        vowels = sorted([l for l in self.guessed_letters if l in VOWELS])
        
        y = 460
        x = 550
        
        # Draw consonants
        for letter in consonants:
            letter_text = self.large_font.render(letter, True, BLUE)
            self.screen.blit(letter_text, (x, y))
            x += 45
            if x > 1300:
                x = 550
                y += 50
        
        # Draw vowels
        if vowels:
            if x > 550:
                y += 50
            x = 550
            vowel_label = self.small_font.render("(Vowels)", True, RED)
            self.screen.blit(vowel_label, (x, y))
            y += 35
            x = 550
            for letter in vowels:
                letter_text = self.large_font.render(letter, True, RED)
                self.screen.blit(letter_text, (x, y))
                x += 45
                if x > 1300:
                    x = 550
                    y += 50
    
    def draw_options(self):
        """Draw available options based on game state"""
        box_x = 30
        box_y = 440 
        
        # Title
        title = self.large_font.render("YOUR OPTIONS:", True, BLACK)
        self.screen.blit(title, (box_x, box_y))
        
        y = box_y + 60
        
        # Only show available options
        
        # Option: Spin
        if not self.can_guess and not self.wheel_spinning:
            opt1 = self.font.render("► Press SPACE to SPIN the wheel", True, GREEN)
            self.screen.blit(opt1, (box_x, y))
            y += 50
        
        # Option: Buy vowel (only if can afford and vowels available)
        has_vowels = any(v in self.current_puzzle and v not in self.guessed_letters for v in VOWELS)
        if self.score >= VOWEL_COST and has_vowels:
            opt2 = self.font.render(f"► Press V to BUY A VOWEL (${VOWEL_COST})", True, GREEN)
            self.screen.blit(opt2, (box_x, y))
            y += 50
        
        # Option: Guess consonant (only after spinning)
        if self.can_guess:
            opt3 = self.font.render("► Type a CONSONANT to guess", True, GREEN)
            self.screen.blit(opt3, (box_x, y))
            y += 50
        
        # Option: Solve (only if haven't spun)
        if not self.can_guess and not self.wheel_spinning:
            opt4 = self.font.render("► Press ENTER to SOLVE the puzzle", True, GREEN)
            self.screen.blit(opt4, (box_x, y))
            y += 50
        
        y += 20
        
        # New puzzle (always available)
        new_puz = self.small_font.render("Press ESC for new puzzle", True, GRAY)
        self.screen.blit(new_puz, (box_x, y))
    
    def draw_score(self):
        """Draw score"""
        score_bg = pygame.Rect(550, 680, 800, 100)
        pygame.draw.rect(self.screen, GOLD, score_bg)
        pygame.draw.rect(self.screen, BLACK, score_bg, 4)
        
        score_text = self.huge_font.render(f"SCORE: ${self.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(975, 730))
        self.screen.blit(score_text, score_rect)
    
    def draw_message(self):
        """Draw status message"""
        if self.message:
            msg_text = self.large_font.render(self.message, True, BLUE)
            msg_rect = msg_text.get_rect(center=(200, 370))
            self.screen.blit(msg_text, msg_rect)
    
    def buy_vowel(self):
        """Buy a vowel"""
        if self.score < VOWEL_COST:
            self.message = f"Need ${VOWEL_COST}!"
            return False
        
        # Check if vowels available
        available_vowels = [v for v in VOWELS if v in self.current_puzzle and v not in self.guessed_letters]
        if not available_vowels:
            self.message = "No vowels left!"
            return False
        
        self.message = "Type a vowel (A, E, I, O, U)"
        return True
        
    def guess_letter(self, letter, is_vowel_purchase=False):
        """Process a letter guess"""
        letter = letter.upper()
        
        if letter in self.guessed_letters:
            self.message = "Already guessed!"
            return
        
        if not letter.isalpha():
            return
        
        # Check vowel rules
        if letter in VOWELS:
            if not is_vowel_purchase:
                self.message = "Buy vowels with V key!"
                return
            if self.score < VOWEL_COST:
                self.message = f"Need ${VOWEL_COST}!"
                return
            self.score -= VOWEL_COST
        else:
            # Consonant - must have spun
            if not self.can_guess:
                self.message = "Spin the wheel first!"
                return
        
        self.guessed_letters.add(letter)
        
        # Check if letter is in puzzle
        if letter in self.current_puzzle:
            count = self.current_puzzle.count(letter)
            
            if letter not in VOWELS:
                self.score += self.current_value * count
                self.message = f"Yes! +${self.current_value * count}"
                # After guessing a consonant, must spin again
                self.current_value = 0
                self.can_guess = False
            else:
                self.message = f"Yes! Found {count}"
            
            # Reveal letters
            for i, c in enumerate(self.current_puzzle):
                if c == letter:
                    self.revealed[i] = letter
            
            # Check if puzzle is solved
            if '_' not in self.revealed:
                self.score += 1000  # Bonus for solving
                self.message = "SOLVED! +$1000 bonus!"
                pygame.time.wait(3000)
                self.new_puzzle()
        else:
            self.message = f"Sorry, no {letter}"
            self.current_value = 0
            self.can_guess = False
    
    def solve_puzzle(self):
        """Allow player to solve the puzzle"""
        self.message = "Feature coming soon!"
        # In a full implementation, this would prompt for the full answer
    
    def run(self):
        """Main game loop"""
        running = True
        waiting_for_vowel = False
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.spin_wheel()
                    elif event.key == pygame.K_ESCAPE:
                        self.new_puzzle()
                    elif event.key == pygame.K_v:
                        # Only allow buying vowel if can afford it
                        if self.score >= VOWEL_COST:
                            has_vowels = any(v in self.current_puzzle and v not in self.guessed_letters for v in VOWELS)
                            if has_vowels:
                                waiting_for_vowel = True
                                self.buy_vowel()
                    elif event.key == pygame.K_RETURN:
                        # Can only solve if haven't spun
                        if not self.can_guess:
                            self.solve_puzzle()
                    elif event.unicode.isalpha():
                        letter = event.unicode.upper()
                        # Allow typing consonants after spinning
                        if self.can_guess and letter not in VOWELS:
                            self.guess_letter(letter, is_vowel_purchase=False)
                        # Allow typing vowels when buying
                        elif waiting_for_vowel and letter in VOWELS:
                            self.guess_letter(letter, is_vowel_purchase=True)
                            waiting_for_vowel = False
            
            # Update
            self.update_wheel()
            
            # Draw
            self.screen.fill(BACKGROUND)
            
            # Draw dividing line
            pygame.draw.line(self.screen, BLACK, (400, 0), (500, HEIGHT), 4)
            
            # Left side - wheel and options
            self.draw_wheel()
            self.draw_message()
            self.draw_options()
            
            # Right side - puzzle
            self.draw_puzzle()
            self.draw_guessed_letters()
            self.draw_score()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = WheelGame()
    game.run()
