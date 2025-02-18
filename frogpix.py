import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')


class YOLOViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("FrogPix")
        self.master.geometry("800x600")

        self.bg_image_path = r"C:\Users\topgu\Desktop\Splotowe Sieci Neuronowe\frogpix.png"
        self.icon_path = r"C:\Users\topgu\Desktop\Splotowe Sieci Neuronowe\frogpix.ico"

        try:
            self.master.iconbitmap(self.icon_path)
        except Exception as e:
            print("Błąd podczas ładowania ikony:", e)

        try:
            bg_image = Image.open(self.bg_image_path).convert("RGB")
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.background_label = tk.Label(master, image=self.bg_photo, bg='black')
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Błąd przy ładowaniu tła:", e)

        self.image_paths = []
        self.current_index = 0

        font = ("Orbitron", 14)

        self.image_label = tk.Label(master)
        self.image_label.pack(pady=10)

        # Ramka nawigacyjna (przyciski Previous i Next)
        self.nav_frame = tk.Frame(master, bg="#242424")
        self.btn_prev = ctk.CTkButton(
            self.nav_frame, text="<< Previous", command=self.show_prev_image,
            fg_color="#8A2BE2", text_color="white", hover_color="#7A1BBE",
            corner_radius=0, border_width=2, border_color="#7A1BBE",
            font=font, state=tk.DISABLED
        )
        self.btn_prev.pack(side=tk.LEFT, padx=10)

        self.btn_next = ctk.CTkButton(
            self.nav_frame, text="Next >>", command=self.show_next_image,
            fg_color="#8A2BE2", text_color="white", hover_color="#7A1BBE",
            corner_radius=0, border_width=2, border_color="#7A1BBE",
            font=font, state=tk.DISABLED
        )
        self.btn_next.pack(side=tk.LEFT, padx=10)

        # Na początku panel z przyciskami jest ukryty
        self.nav_frame.pack_forget()

        # Dodajemy etykietę do wyświetlania nazwy obrazu i kolejności.
        # Nie pakujemy jej od razu, więc na głównym ekranie nie będzie widoczna.
        self.info_label = ctk.CTkLabel(master, text="", font=font, text_color="white")

        # Ramka na ścieżkę folderu i przycisk "Select" (widoczna od początku)
        self.path_frame = tk.Frame(master, bg="#242424")
        self.input_entry = ctk.CTkEntry(
            self.path_frame, width=300, placeholder_text="Input folder",
            fg_color="black", text_color="white", font=font
        )
        self.input_entry.pack(side=tk.LEFT, padx=10)
        self.btn_load_folder = ctk.CTkButton(
            self.path_frame, text="Select", command=self.select_folder,
            fg_color="#8A2BE2", text_color="white", hover_color="#7A1BBE",
            corner_radius=0, border_width=2, border_color="#7A1BBE",
            font=font
        )
        self.btn_load_folder.pack(side=tk.LEFT)
        self.path_frame.pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder with images")
        if not folder:
            return

        self.image_paths = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]
        if not self.image_paths:
            messagebox.showerror("Error", "No images found in the folder!")
            return

        self.current_index = 0
        self.btn_next.configure(state=tk.NORMAL if len(self.image_paths) > 1 else tk.DISABLED)
        self.btn_prev.configure(state=tk.NORMAL if len(self.image_paths) > 1 else tk.DISABLED)

        self.master.configure(bg="#242424")
        self.background_label.place_forget()

        # Wyświetlamy panel nawigacyjny
        self.nav_frame.pack(pady=10)
        # Pakujemy info_label poniżej przycisków
        self.info_label.pack(pady=10)

        self.display_current_image()

    def display_current_image(self):
        if not self.image_paths:
            return

        image_path = self.image_paths[self.current_index]
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load image:\n{image_path}\n{e}")
            return

        label_path = os.path.splitext(image_path)[0] + ".txt"
        labels = []
        if os.path.exists(label_path):
            try:
                with open(label_path, "r") as f:
                    labels = [line.strip() for line in f if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Cannot load labels:\n{label_path}\n{e}")

        image_with_boxes = self.draw_yolo_boxes(image, labels)
        image_with_boxes.thumbnail((800, 600))
        self.photo = ImageTk.PhotoImage(image_with_boxes)
        self.image_label.config(image=self.photo)

        # Aktualizacja etykiety z nazwą obrazu i kolejnością (np. "obraz.jpg (1/50)")
        self.info_label.configure(
            text=f"{os.path.basename(image_path)} ({self.current_index+1}/{len(self.image_paths)})"
        )

    def draw_yolo_boxes(self, pil_image, labels):
        draw = ImageDraw.Draw(pil_image)
        img_width, img_height = pil_image.size
        for line in labels:
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                class_id = parts[0]
                x_center = float(parts[1])
                y_center = float(parts[2])
                width_norm = float(parts[3])
                height_norm = float(parts[4])
            except Exception:
                continue

            cx = x_center * img_width
            cy = y_center * img_height
            box_w = width_norm * img_width
            box_h = height_norm * img_height
            top_left = (cx - box_w / 2, cy - box_h / 2)
            bottom_right = (cx + box_w / 2, cy + box_h / 2)

            draw.rectangle([top_left, bottom_right], outline="lime", width=2)
            draw.text((top_left[0], top_left[1] - 15), class_id, fill="lime")
        return pil_image

    def show_next_image(self):
        if not self.image_paths:
            return
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self.display_current_image()

    def show_prev_image(self):
        if not self.image_paths:
            return
        self.current_index = (self.current_index - 1) % len(self.image_paths)
        self.display_current_image()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = YOLOViewer(root)
    root.mainloop()