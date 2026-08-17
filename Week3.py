"""
Week 3: Imaging and Special Effects - Interactive Game Window with Arcade Library
This program creates an interactive game window with a character that can be controlled
via keyboard (arrow keys) and mouse (click and drag).
"""

from pathlib import Path

import arcade

# Asset directory, resolved relative to this file so the script runs from anywhere
ASSET_DIR = Path(__file__).parent / "lab" / "asset"

# Window dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Image Window"

# Background colors
DARK_BLUE = (25, 25, 112)  # Dark blue color


class GameWindow(arcade.Window):
    """
    Main application class that represents the game window.
    Handles all graphics, input, and game logic.
    """

    def __init__(self):
        """
        Initialize the GameWindow.
        Sets up window properties, loads textures, and initializes game variables.
        """
        # Initialize parent class with window dimensions and title
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set background color to dark blue
        self.clear_color = arcade.color.DARK_BLUE

        # ----- TASK 2: Load Textures -----
        try:
            self.background = arcade.load_texture(ASSET_DIR / "background.jpeg")
            self.subbackground = arcade.load_texture(ASSET_DIR / "snowBackground.png")
            self.character = arcade.load_texture(ASSET_DIR / "character.png")
        except FileNotFoundError as e:
            print(f"Warning: Could not load texture: {e}")
            print(f"Please ensure all image files are in {ASSET_DIR}")
            # Create placeholder textures if files not found
            self.background = None
            self.subbackground = None
            self.character = None

        # ----- TASK 3: Character Movement -----
        # Character position
        self.playerX = 200
        self.playerY = 200

        # Character movement speed (pixels per key press)
        self.playerMovingSpeed = 5

        # ----- TASK 4: Character Dimensions -----
        self.playerWidth = 100
        self.playerHeight = 70

        # ----- TASK 5: Mouse Drag -----
        self.dragging = False

    def on_draw(self):
        """
        Render the game.
        This function is called whenever the screen needs to be updated.
        """
        # Clear the screen with the background color
        self.clear()

        # ----- TASK 2: Draw Textures -----
        # Draw main background at (0, 0) with size 800x600
        # arcade.LBWH builds a rect from its left/bottom corner plus width/height
        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            )

        # Draw sub-background (snowy area) at (130, 200) with size 550x300
        if self.subbackground:
            arcade.draw_texture_rect(
                self.subbackground,
                arcade.LBWH(130, 200, 550, 300),
            )

        # Draw character at (playerX, playerY) with size 100x70
        if self.character:
            arcade.draw_texture_rect(
                self.character,
                arcade.LBWH(
                    self.playerX, self.playerY, self.playerWidth, self.playerHeight
                ),
            )

    def on_key_press(self, key, _):
        """
        Handle keyboard input for character movement.
        Arrow keys control character movement in different directions.

        Args:
            key: The key that was pressed
            _: Unused parameter (modifiers)
        """
        # ----- TASK 3: Implement Keyboard Controls -----
        if key == arcade.key.LEFT:
            # Move left
            self.playerX -= self.playerMovingSpeed
        elif key == arcade.key.RIGHT:
            # Move right
            self.playerX += self.playerMovingSpeed
        elif key == arcade.key.UP:
            # Move up
            self.playerY += self.playerMovingSpeed
        elif key == arcade.key.DOWN:
            # Move down
            self.playerY -= self.playerMovingSpeed

        # ----- TASK 4: Check Boundary -----
        self.checkBoundary()

    def checkBoundary(self):
        """
        Enforce boundary constraints to keep the character within the snowy area.
        Prevents the character from moving outside the designated play area.
        """
        # ----- TASK 4: Boundary Checking -----
        # Constrain X position: min 130, max 680 - playerWidth
        self.playerX = max(130, min(self.playerX, 680 - self.playerWidth))

        # Constrain Y position: min 200, max 500 - playerHeight
        self.playerY = max(200, min(self.playerY, 500 - self.playerHeight))

    def on_mouse_press(self, x, y, button, _):
        """
        Handle mouse press events.
        Detects if the character is clicked and initiates dragging.

        Args:
            x: X coordinate of mouse click
            y: Y coordinate of mouse click
            button: Which mouse button was pressed
            _: Unused parameter (modifiers)
        """
        # ----- TASK 5: Mouse Click Detection -----
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Check if click is within character bounds
            if (
                self.playerX <= x <= self.playerX + self.playerWidth
                and self.playerY <= y <= self.playerY + self.playerHeight
            ):
                self.dragging = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Handle mouse drag events.
        Updates character position while mouse is being dragged.

        Args:
            x: Current X coordinate of mouse
            y: Current Y coordinate of mouse
            dx: Change in X since last update
            dy: Change in Y since last update
            buttons: Which mouse buttons are pressed
            modifiers: Keyboard modifiers (Ctrl, Shift, etc.)
        """
        # ----- TASK 5: Mouse Drag Movement -----
        if self.dragging:
            # Update character position to follow mouse
            # Center the character on the mouse cursor
            self.playerX = x - self.playerWidth / 2
            self.playerY = y - self.playerHeight / 2

            # Enforce boundary constraints
            self.checkBoundary()

    def on_mouse_release(self, x, y, button, _):
        """
        Handle mouse release events.
        Stops dragging when the mouse button is released.

        Args:
            x: X coordinate of mouse release
            y: Y coordinate of mouse release
            button: Which mouse button was released
            _: Unused parameter (modifiers)
        """
        # ----- TASK 5: Mouse Release -----
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.dragging = False


def main():
    """Main function to create and run the game."""
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
