import sys
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import subprocess
import psutil
from settings import open_settings_window

# Global variables for managing the assistant process and GIF animation
assistant_process = None
gif_frames = []
gif_running = False
gif_image_id = None
current_frame = 0


def run_gui():
    # Your existing Tkinter code that sets up the GUI
    root = tk.Tk()
    root.title("Your Application")

    # Add GUI widgets, buttons, and logic here
    # Example:
    start_button = tk.Button(root, text="Start", command=start_function)
    start_button.pack()

    root.mainloop()


def start_function():
    print("Start button clicked!")
    # Any other logic for starting the main app

# Function to load GIF frames
def load_gif(filepath):
    """Load all frames of an animated GIF with transparency."""
    global gif_frames
    gif_frames.clear()
    gif = Image.open(filepath)
    for frame in ImageSequence.Iterator(gif):
        # Ensure the GIF frame has an alpha channel (transparency)
        if frame.mode != "RGBA":
            frame = frame.convert("RGBA")
        gif_frames.append(ImageTk.PhotoImage(frame))

# Function to update the GIF animation
def update_gif_frame(canvas):
    """Update the frame of the animated GIF while keeping the background."""
    global gif_running, current_frame, gif_image_id

    if gif_running and gif_frames:
        frame = gif_frames[current_frame]
        if gif_image_id is None:
            gif_image_id = canvas.create_image(
                (main_img.width // 2 + 8) - 3,  # Shift 20 pixels left
                (main_img.height // 2 + 4) - 2,  # Shift 30 pixels up
                image=frame,
                anchor="center",
                tags="animated_gif"
            )
            canvas.tag_lower(gif_image_id, "buttons")  # Lower GIF beneath buttons
        else:
            canvas.itemconfig(gif_image_id, image=frame)
        current_frame = (current_frame + 1) % len(gif_frames)
        root.after(100, lambda: update_gif_frame(canvas))  # Adjust the delay for frame rate

# Functions to control the GIF animation
def start_gif(canvas):
    """Start the animated GIF."""
    global gif_running
    if not gif_running:
        gif_running = True
        update_gif_frame(canvas)

def stop_gif(canvas):
    """Stop the animated GIF."""
    global gif_running, gif_image_id
    gif_running = False
    if gif_image_id is not None:
        canvas.delete(gif_image_id)
        gif_image_id = None

# Button event handlers
def on_start_click():
    print("Start button clicked")  # Debugging print statement
    global assistant_process
    assistant_process = subprocess.Popen([sys.executable, 'main.py'])  # Use sys.executable
    start_gif(canvas)

def on_stop_click():
    global assistant_process
    print("Stop button clicked")
    if assistant_process:
        try:
            parent = psutil.Process(assistant_process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            assistant_process = None
        except psutil.NoSuchProcess:
            print("The process does not exist.")
        except PermissionError:
            print("Permission denied: Unable to terminate the process.")
        except Exception as e:
            print(f"An error occurred: {e}")
    stop_gif(canvas)

def on_settings_click():
    print("Settings button clicked")
    try:
        open_settings_window()
    except Exception as e:
        print(f"Error opening settings window: {e}")

def on_close_click():
    global assistant_process
    print("Close button clicked")
    if assistant_process:
        try:
            parent = psutil.Process(assistant_process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except psutil.NoSuchProcess:
            print("The process does not exist.")
        except PermissionError:
            print("Permission denied: Unable to terminate the process.")
        except Exception as e:
            print(f"An error occurred: {e}")
    root.destroy()

# Custom class for transparent buttons
class TransparentButton:
    def __init__(self, canvas, pil_image, x, y, command, anchor="center"):
        self.canvas = canvas
        self.command = command
        self.original_pil_image = pil_image
        self.current_tk_image = ImageTk.PhotoImage(pil_image)
        self.image_id = canvas.create_image(x, y, image=self.current_tk_image, anchor=anchor, tags="buttons")
        self.x = x
        self.y = y
        # Bind the <ButtonPress> and <ButtonRelease> events to handle clicks
        canvas.tag_bind(self.image_id, "<ButtonPress>", self.on_press)
        canvas.tag_bind(self.image_id, "<ButtonRelease>", self.on_release)

    def on_press(self, event):
        self.animate(scale=0.9)  # Shrink the button slightly
        self.command()
        self.canvas.tag_raise(self.image_id)  # Bring the button to the front

    def on_release(self, event):
        self.animate(scale=1.0)  # Restore to original size

    def animate(self, scale):
        original_width, original_height = self.original_pil_image.size
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        resized_pil_image = self.original_pil_image.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )
        self.current_tk_image = ImageTk.PhotoImage(resized_pil_image)
        self.canvas.itemconfig(self.image_id, image=self.current_tk_image)

# Function to handle dragging the window
def make_window_draggable(root):
    def on_press(event):
        root._drag_data = {'x': event.x, 'y': event.y}

    def on_drag(event):
        deltax = event.x - root._drag_data['x']
        deltay = event.y - root._drag_data['y']
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    root.bind("<ButtonPress-1>", on_press)
    root.bind("<B1-Motion>", on_drag)

# Function to manage window focus and always on top behavior
def manage_focus(root):
    def on_focus_in(event):
        root.attributes("-topmost", True)

    def on_focus_out(event):
        root.attributes("-topmost", False)

    root.bind("<FocusIn>", on_focus_in)
    root.bind("<FocusOut>", on_focus_out)

# Main function to create the GUI
def create_circle_gui(
    main_image_path, start_button_path, stop_button_path, settings_button_path, close_button_path, animated_gif_path
):
    global root, canvas, main_img
    # Create a Tkinter root window without decorations
    root = tk.Tk()
    root.overrideredirect(True)  # Remove title bar and borders
    root.geometry("+100+100")  # Set initial position

    make_window_draggable(root)  # Enable dragging
    manage_focus(root)  # Manage window focus

    # Load the main GUI image (background)
    main_img = Image.open(main_image_path).convert("RGBA")
    main_img_tk = ImageTk.PhotoImage(main_img)

    # Create a canvas to display the main GUI image
    canvas = tk.Canvas(root, width=main_img.width, height=main_img.height, highlightthickness=0, bg='white')
    canvas.pack()

    # Set the background image on the canvas (ensure it's below other elements)
    canvas.create_image(0, 0, image=main_img_tk, anchor="nw", tags="background")

    # Configure the window to handle transparency
    root.wm_attributes("-transparentcolor", "white")
    canvas.configure(bg='white')

    # Load button images (with transparent backgrounds)
    start_img = Image.open(start_button_path).convert("RGBA").resize((36, 36))
    stop_img = Image.open(stop_button_path).convert("RGBA").resize((36, 36))
    settings_img = Image.open(settings_button_path).convert("RGBA").resize((36, 36))
    close_img = Image.open(close_button_path).convert("RGBA").resize((36, 36))

    # Load the animated GIF
    load_gif(animated_gif_path)

    # Create transparent buttons
    start_button = TransparentButton(
        canvas, start_img, x=32, y=main_img.height - 32, command=on_start_click
    )
    stop_button = TransparentButton(
        canvas, stop_img, x=main_img.width - 32, y=main_img.height - 32, command=on_stop_click
    )
    settings_button = TransparentButton(
        canvas, settings_img, x=32, y=32, command=on_settings_click, anchor="center"
    )
    close_button = TransparentButton(
        canvas, close_img, x=main_img.width - 32, y=32, command=on_close_click, anchor="center"
    )

    # Keep buttons always on top
    def raise_buttons():
        canvas.tag_raise("buttons")

    root.after(100, raise_buttons)  # Raise buttons above GIF after a short delay

    # Handle window close
    root.bind("<Escape>", lambda e: root.destroy())  # Press Escape to close the window

    # Keep references to avoid garbage collection
    root.main_img_tk = main_img_tk

    # Start the Tkinter loop
    root.mainloop()

# File paths (update with actual paths on your system)
main_gui_path = "C:/News Assistant/Pictures/main_gui.png"
start_button_path = "C:/News Assistant/Pictures/start_button.png"  # Transparent .png
stop_button_path = "C:/News Assistant/Pictures/stop_button.png"  # Transparent .png
settings_button_path = "C:/News Assistant/Pictures/settings_button.png"  # Transparent .png
close_button_path = "C:/News Assistant/Pictures/close_button.png"  # Transparent .png
animated_gif_path = "C:/News Assistant/Pictures/animated.gif"  # Your GIF file

# Create the GUI
create_circle_gui(main_gui_path, start_button_path, stop_button_path, settings_button_path, close_button_path, animated_gif_path)
