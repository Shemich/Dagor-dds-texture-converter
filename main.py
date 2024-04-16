import os
from PIL import Image
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

def process_normal_texture(input_file, output_folder, channel, progress_var, total_files):
    # Open the image
    img = Image.open(input_file)
    
    # Create a new image only with one channel
    new_img = Image.new("RGB", img.size)
    pixels = new_img.load()
    
    # Extract the specified channel from the image
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            color = img.getpixel((x, y))
            if channel == 'spec':
                smoothness = color[0] / 255.0
                pixels[x, y] = (int(smoothness * 255), int(smoothness * 255), int(smoothness * 255))
            elif channel == 'normal':
                green = color[1]
                alpha = color[3]
                pixels[x, y] = (alpha, green, 255)
            elif channel == 'metal':
                metalness = color[2] / 255.0
                pixels[x, y] = (int(metalness * 255), int(metalness * 255), int(metalness * 255))
    
    # Determine the output file name
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, f"{base_name}_{channel}.png")
    
    # Save the image
    new_img.save(output_file)
    
    # Update the progress
    progress_var.step() 
    root.update()

def process_diffuse_texture(input_file, output_folder, progress_var):
    # Open the image
    img = Image.open(input_file)
    
    # Create a new image with RGB mode
    new_img = img.convert("RGB")
    
    # Determine the output file name for Diffuse Color
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_color = os.path.join(output_folder, f"{base_name}_co.png")
    
    # Save the image without alpha channel (Diffuse Color)
    new_img.save(output_color)
    
    progress_var.step()
    root.update()
    
    # Determine the output file name for Ambient Occlusion (alpha channel)
    output_ao = os.path.join(output_folder, f"{base_name}_ao.png")
    
    # Extract alpha channel as a separate image (Ambient Occlusion)
    alpha_channel = img.split()[3]
    alpha_channel.save(output_ao)
    
    progress_var.step()
    root.update()

def select_files():
    # Open file dialog to select files
    file_paths = filedialog.askopenfilenames()
    return file_paths

def convert_textures():
    # Select input files
    input_files = select_files()
    if not input_files:
        return
    
    # Ask for output folder
    output_folder = filedialog.askdirectory(title="Выберите папку для сохранения")
    if not output_folder:
        return
    
    # Create subfolder for converted textures
    output_subfolder = os.path.join(output_folder, "converted_textures")
    os.makedirs(output_subfolder, exist_ok=True)

    # Count total number of files
    total_files = len(input_files)
    
    # Create progress window
    progress_window = tk.Toplevel()
    progress_window.title("Прогресс конвертации")
    
    # Create and configure progress bar
    progress_var = ctk.CTkProgressBar(master=progress_window, determinate_speed = 15)
    progress_var.pack(padx=20, pady=20)
    
    # Count processed files with _n.dds and _d.dds suffixes
    count_n = 0
    count_d = 0
    
    # Process each selected file
    for input_file in input_files:
        # Determine file type based on suffix
        if input_file.endswith("_n.dds"):
            count_n += 1
            # Specular (smoothness)
            process_normal_texture(input_file, output_subfolder, 'spec', progress_var, total_files)
            # Normal (Y) + Alpha (X)
            process_normal_texture(input_file, output_subfolder, 'normal', progress_var, total_files)
            # Metallic (metalness)
            process_normal_texture(input_file, output_subfolder, 'metal', progress_var, total_files)
        elif input_file.endswith("_d.dds"):
            count_d += 1
            # Process Diffuse texture (without alpha channel)
            process_diffuse_texture(input_file, output_subfolder, progress_var)

    # Close progress window after completion
    progress_window.destroy()

    # # Вывод окна с информацией о завершении конвертации
    msg = f"Конвертация завершена!\nОбработано текстур _n: {count_n}\nОбработано текстур _d: {count_d}"
    # Show completion message
    messagebox.showinfo("Готово", msg)

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Create main GUI window
root = ctk.CTk()
root.title("Конвертер текстур")
root.geometry("300x400")

# Create button to select files and start conversion
select_button = ctk.CTkButton(master=root, text="Выбрать текстуры для конвертации", command=convert_textures)
select_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Start GUI main loop
root.mainloop()