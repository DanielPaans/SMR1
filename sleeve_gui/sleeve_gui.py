from textwrap import wrap
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import cv2
from PIL import Image, ImageTk

from .button import RoundedButton
from sleeve_detection import SleeveDetection

SLEEVE_DETECTOR = SleeveDetection()


class SleeveGUI:
    def __init__(self) -> None:
        self.queue = None
        self.root = self._initialize_root()
        self.style = self._initialize_style()
        self.cap, self.camera_pane = self._initialize_camera()
        self.side_pane = self._initialize_side_frame()

    def _initialize_root(self):
        root = tk.Tk()
        root.title("Sleeve Picker")

        return root

    def _initialize_style(self):
        style = ttk.Style()
        style.configure(
            "TButton",
            font=("Helvetica", 12),
            padding=10,
            background="blue",
            foreground="white",
        )

        return style

    def _initialize_camera(self):
        cap = cv2.VideoCapture(0)
        label = tk.Label(self.root)
        label.pack(side=tk.RIGHT)
        return cap, label

    def _initialize_side_frame(self):
        sidebar_frame = tk.Frame(self.root)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Create a label for the sidebar
        sidebar_label = tk.Label(sidebar_frame, text="Sleeve Picker UI")
        sidebar_label.pack()
        sidebar_text = tk.Label(
            sidebar_frame,
            text="",
            wraplength=150,
            font=("Helvetica", 12),  # Change font and font size
            padx=10,  # Add padding
            pady=10,
        )
        sidebar_text.pack()

        button_font = ("Helvetica", 12)

        # Create a rounded button image
        button = RoundedButton(
            sidebar_frame,
            text="Callibrate",
            border_radius=4,
            padding=30,
            command=self._button_click,
            color="#4d87b3",
            hover_color="#709ec2",
            active_color="#3d6b8f",
        )
        button.pack()

    # Create a function to update the camera feed
    def _update_camera_feed(self):
        ret, frame = self.cap.read()  # Read a frame from the camera
        if ret:
            frame = SLEEVE_DETECTOR.detect(frame, self.queue)
            # Convert the frame from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the frame to a PhotoImage object
            img = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
            # Update the label with the new image
            self.camera_pane.config(image=img)
            self.camera_pane.img = img
            # Schedule the function to run again after 10 ms (you can adjust this delay)
            self.root.after(10, self._update_camera_feed)
        else:
            # If there's no more frames, release the camera and close the window
            self.cap.release()
            self.root.quit()

    # Create a function to update the sidebar text
    def _update_sidebar_text(self, new_text):
        self.sidebar_text.config(text=new_text)

    # Create a function to handle button clicks
    def _button_click(self):
        self._update_sidebar_text("Button Clicked!")

    def run(self, queue):
        self.queue = queue
        self._update_camera_feed()
        self.root.mainloop()
