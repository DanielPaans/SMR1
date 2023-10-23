from tkinter import *
import tkinter as tk
import tkinter.font as font


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        border_radius,
        padding,
        color,
        hover_color,
        active_color,
        text="",
        command=None,
    ):
        tk.Canvas.__init__(
            self,
            parent,
            borderwidth=0,
            relief="raised",
            highlightthickness=0,
            bg=parent["bg"],
        )
        self.color = color
        self.command = command
        font_size = 10
        self.font = font.Font(size=font_size, family="Helvetica")
        self.id = None
        self.border_radius = border_radius
        self.text = text
        self.hover_color = hover_color
        self.active_color = active_color

        self.height = font_size + (1 * padding)
        width = self.font.measure(text) + (1 * padding)

        self.width = width if width >= 80 else 80

        if border_radius > 0.5 * self.width:
            print("Error: border_radius is greater than width.")
            return None

        if border_radius > 0.5 * self.height:
            print("Error: border_radius is greater than height.")
            return None

        self.rad = 2 * border_radius

        self._create_button(text, color)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _create_button(self, text, color):
        self._shape(color)
        (x0, y0, x1, y1) = self.bbox("all")
        width = x1 - x0
        height = y1 - y0
        self.configure(width=width, height=height, cursor="hand2")
        self.create_text(width / 2, height / 2, text=text, fill="black", font=self.font)

    def _shape(self, color):
        if len(self.find_all()) > 0:
            self.delete("all")

        width = self.width
        height = self.height
        rad = self.rad
        border_radius = self.border_radius

        self.create_arc(
            (0, rad, rad, 0), start=90, extent=90, fill=color, outline=color
        )
        self.create_arc(
            (width - rad, 0, width, rad),
            start=0,
            extent=90,
            fill=color,
            outline=color,
        )
        self.create_arc(
            (width, height - rad, width - rad, height),
            start=270,
            extent=90,
            fill=color,
            outline=color,
        )
        self.create_arc(
            (0, height - rad, rad, height),
            start=180,
            extent=90,
            fill=color,
            outline=color,
        )
        return self.create_polygon(
            (
                0,
                height - border_radius,
                0,
                border_radius,
                border_radius,
                0,
                width - border_radius,
                0,
                width,
                border_radius,
                width,
                height - border_radius,
                width - border_radius,
                height,
                border_radius,
                height,
            ),
            fill=color,
            outline=color,
        )

    def _on_enter(self, event):
        self._create_button(self.text, self.hover_color)

    def _on_leave(self, event):
        self._create_button(self.text, self.color)

    def _on_press(self, event):
        self._create_button(self.text, self.active_color)

    def _on_release(self, event):
        self._create_button(self.text, self.color)
        if self.command is not None:
            self.command()
