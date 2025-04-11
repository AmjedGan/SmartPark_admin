import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter import *

class AuthentificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartPark - Authentification")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TRadiobutton', font=('Arial', 10))
        
        # Variables
        self.type_utilisateur = tk.StringVar(value="Client")
        self.nom_utilisateur = tk.StringVar()
        self.mot_de_passe = tk.StringVar()
        
        self.creer_interface()
        self.verifier_base_donnees()
    
    def creer_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="SmartPark", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Frame pour les boutons radio
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Radiobutton(type_frame, text="Client", variable=self.type_utilisateur, 
                       value="Client").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(type_frame, text="Admin", variable=self.type_utilisateur, 
                       value="Admin").pack(side=tk.LEFT, padx=20)
        
        # Frame pour les champs de saisie
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Nom d'utilisateur
        ttk.Label(input_frame, text="Nom d'utilisateur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.nom_utilisateur).grid(row=0, column=1, padx=5, pady=5)
        
        # Mot de passe
        ttk.Label(input_frame, text="Mot de passe:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.mot_de_passe, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        # Bouton de connexion
        ttk.Button(main_frame, text="Se connecter", command=self.verifier_authentification).pack(pady=20)
    
    def verifier_base_donnees(self):
        try:
            conn = sqlite3.connect('parc_automobile.db')
            cursor = conn.cursor()
            
            # Vérifier si la table utilisateurs existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='utilisateurs'")
            if not cursor.fetchone():
                # Créer la table utilisateurs si elle n'existe pas
                cursor.execute('''
                    CREATE TABLE utilisateurs (
                        id INTEGER PRIMARY KEY,
                        nom_utilisateur TEXT UNIQUE,
                        mot_de_passe TEXT,
                        type_utilisateur TEXT
                    )
                ''')
                
                # Ajouter les utilisateurs par défaut
                cursor.execute("INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, type_utilisateur) VALUES (?, ?, ?)",
                             ("admin", "admin123", "Admin"))
                cursor.execute("INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, type_utilisateur) VALUES (?, ?, ?)",
                             ("client", "client123", "Client"))
                conn.commit()
            
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {str(e)}")
    
    def verifier_authentification(self):
        nom = self.nom_utilisateur.get()
        mdp = self.mot_de_passe.get()
        type_user = self.type_utilisateur.get()
        
        if not nom or not mdp:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        try:
            conn = sqlite3.connect('parc_automobile.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM utilisateurs WHERE nom_utilisateur = ? AND mot_de_passe = ? AND type_utilisateur = ?",
                          (nom, mdp, type_user))
            utilisateur = cursor.fetchone()
            
            conn.close()
            
            if utilisateur:
                messagebox.showinfo("Succès", f"Bienvenue {type_user}!")
                if type_user == "Admin":
                    self.afficher_interface_admin()
                else:
                    self.afficher_interface_client()
            else:
                messagebox.showerror("Erreur", "Identifiants incorrects")
        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Erreur de connexion à la base de données: {str(e)}")
    
    def afficher_interface_admin(self):
        # Création d'une nouvelle fenêtre pour l'interface admin
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Interface Admin")
        admin_window.geometry("600x400")
        
        # Ajoutez ici les éléments de l'interface admin
        ttk.Label(admin_window, text="Interface Administrateur", font=('Arial', 16, 'bold')).pack(pady=20)
        # ... autres éléments de l'interface admin
    
    def afficher_interface_client(self):
        # Création d'une nouvelle fenêtre pour l'interface client
        client_window = tk.Toplevel(self.root)
        client_window.title("Interface Client")
        client_window.geometry("600x400")
        
        # Ajoutez ici les éléments de l'interface client
        ttk.Label(client_window, text="Interface Client", font=('Arial', 16, 'bold')).pack(pady=20)
        # ... autres éléments de l'interface client

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthentificationApp(root)
    root.mainloop()
