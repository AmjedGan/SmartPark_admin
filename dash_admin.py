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
        """Configure les styles personnalisés pour l'application"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Couleurs principales
        style.configure('Custom.TFrame',
            background="#f5f5f5",
            relief="flat"
        )
        
        # Style pour les labels
        style.configure('Custom.TLabel',
            font=('Segoe UI', 10),
            background="#f5f5f5",
            foreground="#333333",
            padding=5
        )
        
        # Style pour les champs de saisie
        style.configure('Custom.TEntry',
            font=('Segoe UI', 10),
            padding=5,
            relief="flat",
            fieldbackground="white"
        )
        
        # Style pour les boutons
        style.configure('Add.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=8,
            background="#4CAF50",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Edit.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=8,
            background="#2196F3",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Delete.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=8,
            background="#F44336",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Image.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=8,
            background="#9C27B0",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Search.TButton',
            font=('Segoe UI', 10),
            padding=6,
            background="#2196F3",
            foreground="white",
            relief="flat"
        )
        
        # Configuration des effets de survol
        style.map('Add.TButton',
            background=[('active', '#388E3C')],
            relief=[('pressed', 'sunken')]
        )
        
        style.map('Edit.TButton',
            background=[('active', '#1976D2')],
            relief=[('pressed', 'sunken')]
        )
        
        style.map('Delete.TButton',
            background=[('active', '#D32F2F')],
            relief=[('pressed', 'sunken')]
        )
        
        style.map('Image.TButton',
            background=[('active', '#7B1FA2')],
            relief=[('pressed', 'sunken')]
        )
        
        style.map('Search.TButton',
            background=[('active', '#1976D2')],
            relief=[('pressed', 'sunken')]
        )
        
        # Style pour le Treeview
        style.configure('Treeview',
            font=('Segoe UI', 10),
            background="white",
            foreground="#333333",
            fieldbackground="white",
            rowheight=25
        )
        
        style.configure('Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background="#2196F3",
            foreground="white",
            relief="flat"
        )
        
        # Configuration de la couleur de sélection en bleu clair
        style.map('Treeview',
            background=[('selected', '#90CAF9')],
            foreground=[('selected', '#333333')]
        )

    def load_icons(self):
        """Charge les icônes de l'application avec gestion des erreurs"""
        self.icon_add = None
        self.icon_edit = None
        self.icon_delete = None
        self.icon_search = None
        self.icon_image = None
        
        try:
            if not os.path.exists(self.icon_folder):
                os.makedirs(self.icon_folder)
                print(f"Le dossier {self.icon_folder} a été créé. Veuillez y ajouter les icônes nécessaires.")
                return
                
            # Liste des icônes nécessaires
            required_icons = {
                'pen.png': 'icon_add',
                'plus.png': 'icon_edit',
                'delete.png': 'icon_delete',
                'search.png': 'icon_search',
                'image.png': 'icon_image'
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
                        setattr(self, var_name, ImageTk.PhotoImage(icon))
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
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20", style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame pour la recherche
        search_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(search_frame, text="Rechercher:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, style='Custom.TEntry')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = ttk.Button(search_frame, text=" Rechercher", command=self.rechercher_voiture, style='Search.TButton')
        if hasattr(self, 'icon_search') and self.icon_search:
            search_button.configure(image=self.icon_search, compound="left")
        search_button.pack(side=tk.LEFT, padx=5)

        # Frame pour le formulaire
        form_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        form_frame.pack(fill=tk.X, pady=(0, 20))

        # Champs du formulaire alignés horizontalement
        ttk.Label(form_frame, text="Marque:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5)
        self.marque_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.marque_var, width=15, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)

        ttk.Label(form_frame, text="Modèle:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5)
        self.modele_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.modele_var, width=15, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)

        ttk.Label(form_frame, text="Année:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5)
        self.annee_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.annee_var, width=10, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)

        ttk.Label(form_frame, text="Prix:", style='Custom.TLabel').pack(side=tk.LEFT, padx=5)
        self.prix_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prix_var, width=10, style='Custom.TEntry').pack(side=tk.LEFT, padx=5)

        # Bouton sélectionner image
        image_button = ttk.Button(form_frame, text=" Sélectionner Image", command=self.select_image, style='Image.TButton')
        if hasattr(self, 'icon_image') and self.icon_image:
            image_button.configure(image=self.icon_image, compound="left")
        image_button.pack(side=tk.LEFT, padx=5)

        # Frame pour les boutons d'action
        button_frame = ttk.Frame(form_frame, style='Custom.TFrame')
        button_frame.pack(side=tk.RIGHT, padx=10)

        # Boutons d'action
        add_button = ttk.Button(button_frame, text=" Ajouter", command=self.add_car, style='Add.TButton')
        if hasattr(self, 'icon_add') and self.icon_add:
            add_button.configure(image=self.icon_add, compound="left")
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text=" Modifier", command=self.update_car, style='Edit.TButton')
        if hasattr(self, 'icon_edit') and self.icon_edit:
            edit_button.configure(image=self.icon_edit, compound="left")
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(button_frame, text=" Supprimer", command=self.delete_car, style='Delete.TButton')
        if hasattr(self, 'icon_delete') and self.icon_delete:
            delete_button.configure(image=self.icon_delete, compound="left")
        delete_button.pack(side=tk.LEFT, padx=5)

        # Treeview
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Marque", "Modèle", "Année", "Prix", "Image"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.tree.heading("ID", text="ID")
        self.tree.heading("Marque", text="Marque")
        self.tree.heading("Modèle", text="Modèle")
        self.tree.heading("Année", text="Année")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Image", text="Image")

        # Frame pour l'image
        self.image_frame = ttk.LabelFrame(main_frame, text="Image", padding="10", style='Custom.TFrame')
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.image_label = ttk.Label(self.image_frame, style='Custom.TLabel')
        self.image_label.pack(expand=True)

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
