import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import os
import shutil
from datetime import datetime

class CarManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Parc Automobile")
        self.root.geometry("1200x600")
        self.root.configure(bg="#e6f2ff")

        self.image_folder = "car_images"
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

        self.icon_folder = "icons"
        self.load_icons()
        self.configure_styles()

        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="parc_automobile"
            )
            self.cursor = self.conn.cursor()
            self.create_table()
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {e}")

        self.current_image_path = None
        self.create_widgets()
        self.load_voiture_admin()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        background="#007acc",
                        foreground="white",
                        font=('Segoe UI', 10, 'bold'),
                        padding=6)
        style.map("TButton",
                  background=[('active', '#005f99')])

        style.configure("TLabel", font=('Segoe UI', 10))
        style.configure("TEntry", font=('Segoe UI', 10), padding=5)

        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white",
                        font=('Segoe UI', 10))
        style.configure("Treeview.Heading",
                        font=('Segoe UI', 10, 'bold'),
                        background="#007acc",
                        foreground="white")

        style.configure("TLabelframe", background="#f2f2f2")
        style.configure("TLabelframe.Label", font=('Segoe UI', 10, 'bold'))

    def load_icons(self):
        """Charge les icônes de l'application avec gestion des erreurs"""
        self.icon_add = None
        self.icon_edit = None
        self.icon_delete = None
        self.icon_search = None
        
        try:
            if not os.path.exists(self.icon_folder):
                os.makedirs(self.icon_folder)
                print(f"Le dossier {self.icon_folder} a été créé. Veuillez y ajouter les icônes nécessaires.")
                return
                
            # Liste des icônes nécessaires
            required_icons = {
                'pen.png': 'self.icon_add',
                '.png': 'self.icon_edit',
                'delete.png': 'self.icon_delete',
                'search.png': 'self.icon_search'
            }
            
            # Vérification et chargement des icônes
            for icon_file, var_name in required_icons.items():
                icon_path = os.path.join(self.icon_folder, icon_file)
                print(f"Tentative de chargement de l'icône: {icon_path}")
                if os.path.exists(icon_path):
                    try:
                        icon = Image.open(icon_path)
                        if icon_file == 'search.png':
                            icon = icon.resize((16, 16))
                        else:
                            icon = icon.resize((20, 20))
                        setattr(self, var_name[2:], ImageTk.PhotoImage(icon))
                        print(f"Icône {icon_file} chargée avec succès")
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'icône {icon_file}: {str(e)}")
                else:
                    print(f"Icône manquante: {icon_file}")
                    
        except Exception as e:
            print(f"Erreur lors de l'initialisation des icônes: {str(e)}")

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS voiture_admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                marque VARCHAR(255) NOT NULL,
                modele VARCHAR(255) NOT NULL,
                annee INT,
                prix DECIMAL(10,2),
                image_path TEXT,
                date_ajout DATETIME
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = ttk.Button(search_frame, text=" Rechercher", command=self.rechercher_voiture)
        if self.icon_search:
            search_button.configure(image=self.icon_search, compound="left")
        search_button.pack(side=tk.LEFT, padx=5)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = ttk.LabelFrame(content_frame, text="Informations Voiture", padding="10")
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(form_frame, text="Marque:").grid(row=0, column=0, sticky=tk.W)
        self.marque_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.marque_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Modèle:").grid(row=1, column=0, sticky=tk.W)
        self.modele_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.modele_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Année:").grid(row=2, column=0, sticky=tk.W)
        self.annee_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.annee_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Prix:").grid(row=3, column=0, sticky=tk.W)
        self.prix_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prix_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(form_frame, text="Sélectionner Image", command=self.select_image).grid(row=4, column=0, columnspan=2, pady=10)

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        add_button = ttk.Button(button_frame, text=" Ajouter", command=self.add_car)
        if self.icon_add:
            add_button.configure(image=self.icon_add, compound="left")
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text=" Modifier", command=self.update_car)
        if self.icon_edit:
            edit_button.configure(image=self.icon_edit, compound="left")
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text=" Supprimer", command=self.delete_car)
        if self.icon_delete:
            delete_button.configure(image=self.icon_delete, compound="left")
        delete_button.pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(content_frame, columns=("ID", "Marque", "Modèle", "Année", "Prix", "Image"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Marque", text="Marque")
        self.tree.heading("Modèle", text="Modèle")
        self.tree.heading("Année", text="Année")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Image", text="Image")

        self.image_frame = ttk.LabelFrame(content_frame, text="Image", padding="10")
        self.image_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack()

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)

    def display_image(self, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")

    def add_car(self):
        if not self.validate_form():
            return
        try:
            dest_path = None
            if self.current_image_path:
                image_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.current_image_path)}"
                dest_path = os.path.join(self.image_folder, image_name)
                shutil.copy2(self.current_image_path, dest_path)

            self.cursor.execute('''
                INSERT INTO voiture_admin (marque, modele, annee, prix, image_path, date_ajout)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                self.marque_var.get(),
                self.modele_var.get(),
                int(self.annee_var.get()),
                float(self.prix_var.get()),
                dest_path,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.conn.commit()
            self.clear_form()
            self.load_voiture_admin()
            messagebox.showinfo("Succès", "Voiture ajoutée avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")

    def update_car(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture à modifier")
            return
        if not self.validate_form():
            return
        try:
            car_id = self.tree.item(selected_item[0])['values'][0]
            dest_path = self.tree.item(selected_item[0])['values'][5]
            if self.current_image_path:
                image_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.current_image_path)}"
                dest_path = os.path.join(self.image_folder, image_name)
                shutil.copy2(self.current_image_path, dest_path)

            self.cursor.execute('''
                UPDATE voiture_admin 
                SET marque=%s, modele=%s, annee=%s, prix=%s, image_path=%s
                WHERE id=%s
            ''', (
                self.marque_var.get(),
                self.modele_var.get(),
                int(self.annee_var.get()),
                float(self.prix_var.get()),
                dest_path,
                car_id
            ))
            self.conn.commit()
            self.clear_form()
            self.load_voiture_admin()
            messagebox.showinfo("Succès", "Voiture modifiée avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")

    def delete_car(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture à supprimer")
            return
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette voiture?"):
            try:
                car_id = self.tree.item(selected_item[0])['values'][0]
                image_path = self.tree.item(selected_item[0])['values'][5]
                self.cursor.execute('DELETE FROM voiture_admin WHERE id=%s', (car_id,))
                self.conn.commit()
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                self.clear_form()
                self.load_voiture_admin()
                messagebox.showinfo("Succès", "Voiture supprimée avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

    def load_voiture_admin(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.cursor.execute('SELECT * FROM voiture_admin ORDER BY date_ajout DESC')
        for car in self.cursor.fetchall():
            self.tree.insert('', 'end', values=car)

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            self.marque_var.set(values[1])
            self.modele_var.set(values[2])
            self.annee_var.set(values[3])
            self.prix_var.set(values[4])
            if values[5]:
                self.display_image(values[5])
                self.current_image_path = values[5]
            else:
                self.image_label.configure(image='')
                self.current_image_path = None

    def validate_form(self):
        if not self.marque_var.get():
            messagebox.showwarning("Attention", "Veuillez entrer la marque")
            return False
        if not self.modele_var.get():
            messagebox.showwarning("Attention", "Veuillez entrer le modèle")
            return False
        if not self.annee_var.get():
            messagebox.showwarning("Attention", "Veuillez entrer l'année")
            return False
        if not self.prix_var.get():
            messagebox.showwarning("Attention", "Veuillez entrer le prix")
            return False
        return True

    def clear_form(self):
        self.marque_var.set('')
        self.modele_var.set('')
        self.annee_var.set('')
        self.prix_var.set('')
        self.image_label.configure(image='')
        self.current_image_path = None

    def on_search_change(self, *args):
        self.rechercher_voiture()

    def rechercher_voiture(self):
        terme = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        if terme:
            self.cursor.execute("""
                SELECT * FROM voiture_admin 
                WHERE LOWER(marque) LIKE %s 
                OR LOWER(modele) LIKE %s 
                OR CAST(annee AS CHAR) LIKE %s
            """, (f"%{terme}%", f"%{terme}%", f"%{terme}%"))
        else:
            self.cursor.execute("SELECT * FROM voiture_admin ORDER BY date_ajout DESC")
        for car in self.cursor.fetchall():
            self.tree.insert('', 'end', values=car)

if __name__ == "__main__":
    root = tk.Tk()
    app = CarManagementApp(root)
    root.mainloop()
