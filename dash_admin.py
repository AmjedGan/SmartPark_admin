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
            font=('Calibri', 11, 'bold'),
            padding=8,
            background="#4CAF50",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Edit.TButton',
            font=('Calibri', 11, 'bold'),
            padding=8,
            background="#2196F3",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Delete.TButton',
            font=('Calibri', 11, 'bold'),
            padding=8,
            background="#F44336",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Image.TButton',
            font=('Calibri', 11, 'bold'),
            padding=8,
            background="#9C27B0",
            foreground="white",
            relief="flat"
        )
        
        style.configure('Search.TButton',
            font=('Calibri', 11),
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

        # Style pour le cadre de l'image
        #style.configure('Image.TFrame',
            #background="#ffffff",
            #relief="flat",
            #borderwidth=0
        #)
        
        # Style pour le label de l'image
        # style.configure('Image.TLabel',
        #     background="#ffffff",
        #     anchor="center"
        # )

    def load_icons(self):
        """Charge les icônes de l'application avec gestion des erreurs"""
        self.icon_add = None
        self.icon_edit = None
        self.icon_delete = None
        self.icon_search = None
        self.icon_image = None
        self.icon_reload = None
        self.icon_newimage = None
        
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
                'image.png': 'icon_image',
                'reload.png': 'icon_reload',
                'newimage.png': 'icon_newimage'
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
        # Barre de titre
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        # title_label = ttk.Label(
        #     header_frame,
        #     #text="Gestion de Parc Automobile",
        #     #style="Header.TLabel"
        # )
        # title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Frame principal avec grid
        main_frame = ttk.Frame(self.root, style="Content.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Configuration des colonnes du main_frame
        main_frame.columnconfigure(0, weight=3)  # Colonne gauche plus large
        main_frame.columnconfigure(1, weight=1)  # Colonne droite plus étroite

        # Frame pour l'image (en haut à droite)
        self.image_frame = ttk.LabelFrame(main_frame, text="Image du véhicule", style="Image.TFrame")
        self.image_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        
        # Label pour l'image avec un style spécifique
        self.image_label = ttk.Label(self.image_frame, style="Image.TLabel")
        self.image_label.pack(expand=True, fill=tk.BOTH, padx=25, pady=10)

        # Frame pour le formulaire (en bas)
        form_frame = ttk.LabelFrame(main_frame, text="Informations du véhicule", style="Content.TFrame")
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Grid pour les champs du formulaire
        # Ligne 1
        ttk.Label(form_frame, text="Marque:", style="Content.TLabel").grid(row=0, column=0, padx=5, pady=5)
        self.marque_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.marque_var, width=20).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Modèle:", style="Content.TLabel").grid(row=0, column=2, padx=5, pady=5)
        self.modele_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.modele_var, width=20).grid(row=0, column=3, padx=5, pady=5)

        # Ligne 2
        ttk.Label(form_frame, text="Année:", style="Content.TLabel").grid(row=1, column=0, padx=5, pady=5)
        self.annee_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.annee_var, width=20).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Prix:", style="Content.TLabel").grid(row=1, column=2, padx=5, pady=5)
        self.prix_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prix_var, width=20).grid(row=1, column=3, padx=5, pady=5)

        # Frame pour les boutons (sous le formulaire)
        button_frame = ttk.Frame(form_frame, style="Content.TFrame")
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        # Première ligne de boutons
        top_button_frame = ttk.Frame(button_frame)
        top_button_frame.pack(fill=tk.X, pady=5)

        selectimage_button=ttk.Button(top_button_frame, text="Sélectionner Image", command=self.select_image, style="Action.TButton")
        if hasattr(self, 'icon_newimage') and self.icon_newimage:
            selectimage_button.configure(image=self.icon_newimage, compound="left")
        selectimage_button.pack(side=tk.LEFT, padx=5)

        add_button = ttk.Button(top_button_frame, text="Ajouter", command=self.add_car, style="Action.TButton")
        if hasattr(self, 'icon_edit') and self.icon_edit:
            add_button.configure(image=self.icon_edit, compound="left")
        add_button.pack(side=tk.LEFT, padx=5)

        modifier_button=ttk.Button(top_button_frame, text="Modifier", command=self.update_car, style="Action.TButton")
        if hasattr(self, 'icon_add') and self.icon_add:
            modifier_button.configure(image=self.icon_add, compound="left")
        modifier_button.pack(side=tk.LEFT, padx=5)

        reload_button=ttk.Button(top_button_frame, text="Rafraîchir", command=self.load_voiture_admin, style="Action.TButton")
        if hasattr(self, 'icon_reload') and self.icon_reload:
            reload_button.configure(image=self.icon_reload, compound="right")
        reload_button.pack(side=tk.RIGHT, padx=5)

        # Deuxième ligne avec le bouton Supprimer
        bottom_button_frame = ttk.Frame(button_frame)
        bottom_button_frame.pack(fill=tk.X, pady=5)

        delete_button=ttk.Button(bottom_button_frame, text="Supprimer", command=self.delete_car, style="Action.TButton")
        if hasattr(self, 'icon_delete') and self.icon_delete:
            delete_button.configure(image=self.icon_delete, compound="left")
        delete_button.pack(side=tk.TOP, padx=5)

        # Frame pour la recherche (au-dessus du tableau)
        search_frame = ttk.Frame(main_frame, style="Content.TFrame")
        search_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(search_frame, text="Rechercher:", style="Content.TLabel").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)

        # Tableau principal
        self.tree = ttk.Treeview(
            main_frame,
            columns=("ID", "Marque", "Modele", "Annee", "Prix", "Actions"),
            show="headings",
            style="Treeview"
        )
        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # Configuration des colonnes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Marque", text="Marque")
        self.tree.heading("Modele", text="Modèle")
        self.tree.heading("Annee", text="Année")
        self.tree.heading("Prix", text="Prix")
        self.tree.heading("Actions", text="Actions")

        # Ajustement des colonnes
        self.tree.column("ID", width=50)
        self.tree.column("Marque", width=200)
        self.tree.column("Modele", width=200)
        self.tree.column("Annee", width=100)
        self.tree.column("Prix", width=100)
        self.tree.column("Actions", width=200)

        # Ajouter l'événement de sélection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Scrollbar pour le tableau
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=3, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame pour la pagination
        # pagination_frame = ttk.Frame(main_frame, style="Content.TFrame")
        # pagination_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # ttk.Button(pagination_frame, text="<", style="Action.TButton").pack(side=tk.LEFT, padx=2)
        # ttk.Button(pagination_frame, text="1", style="Action.TButton").pack(side=tk.LEFT, padx=2)
        # ttk.Button(pagination_frame, text="2", style="Action.TButton").pack(side=tk.LEFT, padx=2)
        # ttk.Button(pagination_frame, text="3", style="Action.TButton").pack(side=tk.LEFT, padx=2)
        # ttk.Button(pagination_frame, text=">", style="Action.TButton").pack(side=tk.LEFT, padx=2)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)

    def display_image(self, image_path):
        try:
            # Ouvrir l'image
            image = Image.open(image_path)
            
            # Redimensionner l'image à une taille fixe de 300x300
            image = image.resize((120, 120), Image.Resampling.LANCZOS)
            
            # Créer et afficher l'image
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Garder une référence
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")
            self.image_label.configure(image='')
            self.current_image_path = None

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
        try:
            self.cursor.execute('SELECT * FROM voiture_admin ORDER BY date_ajout DESC')
            for car in self.cursor.fetchall():
                # Créer une chaîne pour représenter les actions disponibles
                actions = "👁️ Consulter"
                
                # Insérer la ligne avec les valeurs et les actions
                values = list(car[:5]) + [actions]
                item = self.tree.insert('', 'end', values=values)
                
                # Lier un événement de clic sur la colonne Actions
                self.tree.tag_bind(item, '<ButtonRelease-1>', lambda e, car=car: self.handle_action_click(e, car))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données: {str(e)}")

    def handle_action_click(self, event, car):
        # Obtenir la colonne cliquée
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#6":  # Colonne Actions
                # Créer un menu contextuel
                popup = tk.Menu(self.root, tearoff=0)
                popup.add_command(label="👁️ Consulter", command=lambda: self.show_image_dialog(car[5]))
                
                
                # Afficher le menu à la position du clic
                try:
                    popup.tk_popup(event.x_root, event.y_root)
                finally:
                    popup.grab_release()

    def show_image_dialog(self, image_path):
        if not image_path or not os.path.exists(image_path):
            messagebox.showwarning("Attention", "Aucune image disponible")
            return

        # Créer une nouvelle fenêtre pour l'image
        dialog = tk.Toplevel(self.root)
        dialog.title("Aperçu de l'image")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        try:
            # Ouvrir et redimensionner l'image
            image = Image.open(image_path)
            # Calculer les dimensions pour maintenir le ratio
            ratio = min(700/image.width, 500/image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # Créer un label pour afficher l'image
            label = ttk.Label(dialog, image=photo)
            label.image = photo  # Garder une référence
            label.pack(padx=20, pady=20)
            
            # Bouton pour fermer
            ttk.Button(dialog, text="Fermer", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            dialog.destroy()
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")

    def show_edit_dialog(self, car_id):
        try:
            # Récupérer les données de la voiture
            self.cursor.execute('SELECT * FROM voiture_admin WHERE id = %s', (car_id,))
            car = self.cursor.fetchone()
            if not car:
                messagebox.showerror("Erreur", "Voiture non trouvée")
                return

            dialog = tk.Toplevel(self.root)
            dialog.title("Modifier une voiture")
            dialog.geometry("400x500")
            dialog.transient(self.root)
            dialog.grab_set()

            # Variables pour stocker les valeurs
            marque_var = tk.StringVar(value=car[1])
            modele_var = tk.StringVar(value=car[2])
            annee_var = tk.StringVar(value=str(car[3]))
            prix_var = tk.StringVar(value=str(car[4]))
            image_path = car[5]

            # Création des champs du formulaire
            ttk.Label(dialog, text="Marque:").pack(pady=5)
            marque_entry = ttk.Entry(dialog, textvariable=marque_var)
            marque_entry.pack(pady=5)

            ttk.Label(dialog, text="Modèle:").pack(pady=5)
            modele_entry = ttk.Entry(dialog, textvariable=modele_var)
            modele_entry.pack(pady=5)

            ttk.Label(dialog, text="Année:").pack(pady=5)
            annee_entry = ttk.Entry(dialog, textvariable=annee_var)
            annee_entry.pack(pady=5)

            ttk.Label(dialog, text="Prix:").pack(pady=5)
            prix_entry = ttk.Entry(dialog, textvariable=prix_var)
            prix_entry.pack(pady=5)

            # Image actuelle
            if image_path and os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    image.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(image)
                    img_label = ttk.Label(dialog, image=photo)
                    img_label.image = photo
                    img_label.pack(pady=10)
                except Exception:
                    pass

            # Bouton pour changer l'image
            def update_image():
                new_image_path = self.select_image()
                if new_image_path:
                    nonlocal image_path
                    image_path = new_image_path

            ttk.Button(dialog, text="Changer l'image", command=update_image).pack(pady=10)

            # Boutons de confirmation
            buttons_frame = ttk.Frame(dialog)
            buttons_frame.pack(pady=20)

            def save_changes():
                try:
                    self.cursor.execute('''
                        UPDATE voiture_admin 
                        SET marque=%s, modele=%s, annee=%s, prix=%s, image_path=%s
                        WHERE id=%s
                    ''', (
                        marque_var.get(),
                        modele_var.get(),
                        int(annee_var.get()),
                        float(prix_var.get()),
                        image_path,
                        car_id
                    ))
                    self.conn.commit()
                    dialog.destroy()
                    self.load_voiture_admin()
                    messagebox.showinfo("Succès", "Voiture modifiée avec succès!")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")

            ttk.Button(buttons_frame, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Enregistrer", command=save_changes).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du formulaire: {str(e)}")

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            # Récupérer l'ID de la voiture sélectionnée
            car_id = self.tree.item(selected_item[0])['values'][0]
            
            try:
                # Récupérer les informations de la voiture, y compris le chemin de l'image
                self.cursor.execute('SELECT * FROM voiture_admin WHERE id = %s', (car_id,))
                car = self.cursor.fetchone()
                if car:
                    # Mettre à jour les champs du formulaire
                    # self.marque_var.set(car[1])
                    # self.modele_var.set(car[2])
                    # self.annee_var.set(str(car[3]))
                    # self.prix_var.set(str(car[4]))
                    
                    # Afficher l'image si elle existe
                    if car[5] and os.path.exists(car[5]):
                        self.display_image(car[5])
                        self.current_image_path = car[5]
                    else:
                        # Effacer l'image si aucune image n'est disponible
                        self.image_label.configure(image='')
                        self.current_image_path = None
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des données: {str(e)}")

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

    def delete_all_cars(self):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer toutes les voitures?"):
            try:
                self.cursor.execute('DELETE FROM voiture_admin')
                self.conn.commit()
                self.load_voiture_admin()
                messagebox.showinfo("Succès", "Toutes les voitures ont été supprimées avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CarManagementApp(root)
    root.mainloop()
