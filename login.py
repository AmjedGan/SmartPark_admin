import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import os
import sys
from PIL import Image, ImageTk

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Connexion - Gestion de Parc Automobile")
        self.root.geometry("800x600")  # Augmentation de la taille de la fenêtre
        
        # Création du dossier images s'il n'existe pas
        if not os.path.exists("images"):
            os.makedirs("images")
            messagebox.showinfo("Information", "Un dossier 'images' a été créé. Veuillez y placer votre image de fond (bg_login.jpg)")
            
        # Chargement de l'image de fond
        try:
            # Charger l'image de fond
            bg_image = Image.open("images/bg_login.png")
            # Redimensionner l'image pour correspondre à la taille de la fenêtre
            bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            
            # Création d'un canvas pour l'image de fond
            self.canvas = tk.Canvas(root, width=800, height=600)
            self.canvas.pack(fill="both", expand=True)
            
            # Ajout de l'image de fond au canvas
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
            self.root.configure(bg="#f0f2f5")
            self.canvas = None
        
        # Configuration de la connexion à la base de données
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'parc_automobile'
        }
        
        self.configure_styles()
        self.create_widgets()
        self.create_table()

    def configure_styles(self):
        style = ttk.Style()
        
        # Style pour le frame principal avec fond transparent
        style.configure('Main.TFrame',
            background='white'
        )
        
        # Style pour le frame du formulaire avec fond semi-transparent
        style.configure('Form.TFrame',
            background='white',
            relief="solid",
            borderwidth=1
        )
        
        # Style pour les labels
        style.configure('Label.TLabel',
            font=('Segoe UI', 10),
            background='white',
            foreground="#333333"
        )
        
        # Style pour les labels transparents
        style.configure('Transparent.TLabel',
            font=('Segoe UI', 10),
            background='white',
            foreground="#333333"
        )
        
        # Style pour les champs de saisie
        style.configure('Entry.TEntry',
            font=('Segoe UI', 10),
            padding=8,
            relief="flat",
            fieldbackground="white"
        )

    def create_table(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Création de la table utilisateurs si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL
                )
            """)
            
            # Vérification si l'administrateur existe déjà
            cursor.execute("SELECT COUNT(*) FROM utilisateurs WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Insertion de l'administrateur par défaut
                cursor.execute("""
                    INSERT INTO utilisateurs (username, password, role)
                    VALUES ('admin', 'admin123', 'admin')
                """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {e}")

    def create_widgets(self):
        # Frame principal semi-transparent
        main_frame = ttk.Frame(self.root if not self.canvas else self.canvas, style='Main.TFrame', padding="20")
        if self.canvas:
            main_frame_window = self.canvas.create_window(400, 300, window=main_frame, anchor="center")
        else:
            main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame blanc semi-transparent pour le formulaire
        form_container = ttk.Frame(main_frame, style='Form.TFrame', padding="30")
        form_container.pack(pady=20)
        
        # Logo ou titre
        title_label = ttk.Label(
            form_container,
            text="Gestion de Parc Automobile",
            font=('Segoe UI', 20, 'bold'),
            foreground="#2196F3",
            background='white'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            form_container,
            text="Connexion Administrateur",
            font=('Segoe UI', 12),
            foreground="#666666",
            background='white'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Username
        username_label = ttk.Label(
            form_container,
            text="Nom d'utilisateur",
            style='Label.TLabel'
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(
            form_container,
            textvariable=self.username_var,
            style='Entry.TEntry'
        )
        username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password
        password_label = ttk.Label(
            form_container,
            text="Mot de passe",
            style='Label.TLabel'
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            form_container,
            textvariable=self.password_var,
            show="*",
            style='Entry.TEntry'
        )
        password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Bouton de connexion personnalisé
        login_button = tk.Button(
            form_container,
            text="SE CONNECTER",
            command=self.login,
            font=('Segoe UI', 11, 'bold'),
            fg='white',
            bg='#2196F3',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        login_button.pack(fill=tk.X, pady=10)
        
        # Effet de survol pour le bouton
        def on_enter(e):
            login_button['background'] = '#1976D2'
            
        def on_leave(e):
            login_button['background'] = '#2196F3'
            
        login_button.bind("<Enter>", on_enter)
        login_button.bind("<Leave>", on_leave)
        
        # Informations de connexion par défaut
        info_label = ttk.Label(
            form_container,
            font=('Segoe UI', 9),
            foreground="#666666",
            background='white',
            justify=tk.CENTER
        )
        info_label.pack(pady=(10, 0))

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
            
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM utilisateurs 
                WHERE username = %s AND password = %s
            """, (username, password))
            
            user = cursor.fetchone()
            
            if user:
                # Fermer la fenêtre de connexion
                self.root.destroy()
                
                # Importer et lancer l'interface principale
                from dash_admin import CarManagementApp
                root = tk.Tk()
                app = CarManagementApp(root)
                root.mainloop()
            else:
                messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
                
            cursor.close()
            conn.close()
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur de connexion: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop() 