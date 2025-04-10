import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class DashboardAdmin:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Admin - Gestion Parc Automobile")
        self.root.geometry("1200x600")
        
        # Connexion à la base de données
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
        
        # Création de l'interface
        self.create_widgets()
        
    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS voitures (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    marque VARCHAR(50) NOT NULL,
                    modele VARCHAR(50) NOT NULL,
                    immatriculation VARCHAR(20) UNIQUE NOT NULL,
                    etat VARCHAR(20) DEFAULT 'disponible',
                    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la table: {e}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titre
        ttk.Label(main_frame, text="Gestion du Parc Automobile", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Formulaire d'ajout
        form_frame = ttk.LabelFrame(main_frame, text="Ajouter une voiture", padding="10")
        form_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(form_frame, text="Marque:").grid(row=0, column=0, padx=5, pady=5)
        self.marque_entry = ttk.Entry(form_frame)
        self.marque_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Modèle:").grid(row=0, column=2, padx=5, pady=5)
        self.modele_entry = ttk.Entry(form_frame)
        self.modele_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Immatriculation:").grid(row=1, column=0, padx=5, pady=5)
        self.immatriculation_entry = ttk.Entry(form_frame)
        self.immatriculation_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Ajouter", command=self.ajouter_voiture).grid(row=1, column=3, padx=5, pady=5)
        
        # Barre de recherche
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(search_frame, text="Rechercher:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Rechercher", command=self.rechercher_voiture).grid(row=0, column=2, padx=5)
        
        # Tableau des voitures
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Marque", "Modèle", "Immatriculation", "État"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configuration des colonnes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Marque", text="Marque")
        self.tree.heading("Modèle", text="Modèle")
        self.tree.heading("Immatriculation", text="Immatriculation")
        self.tree.heading("État", text="État")
        
        # Boutons d'action
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(action_frame, text="Modifier", command=self.modifier_voiture).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Supprimer", command=self.supprimer_voiture).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Changer État", command=self.changer_etat).grid(row=0, column=2, padx=5)
        
        # Charger les données initiales
        self.charger_donnees()
    
    def charger_donnees(self):
        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM voitures")
            for row in self.cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données: {e}")
    
    def ajouter_voiture(self):
        marque = self.marque_entry.get()
        modele = self.modele_entry.get()
        immatriculation = self.immatriculation_entry.get()
        
        if not all([marque, modele, immatriculation]):
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO voitures (marque, modele, immatriculation)
                VALUES (%s, %s, %s)
            """, (marque, modele, immatriculation))
            self.conn.commit()
            messagebox.showinfo("Succès", "Voiture ajoutée avec succès")
            self.charger_donnees()
            # Réinitialiser les champs
            self.marque_entry.delete(0, tk.END)
            self.modele_entry.delete(0, tk.END)
            self.immatriculation_entry.delete(0, tk.END)
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {e}")
    
    def modifier_voiture(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture")
            return
        
        item = self.tree.item(selected_item[0])
        values = item['values']
        
        # Créer une fenêtre de modification
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifier la voiture")
        edit_window.geometry("300x200")
        
        ttk.Label(edit_window, text="Marque:").grid(row=0, column=0, padx=5, pady=5)
        marque_entry = ttk.Entry(edit_window)
        marque_entry.grid(row=0, column=1, padx=5, pady=5)
        marque_entry.insert(0, values[1])
        
        ttk.Label(edit_window, text="Modèle:").grid(row=1, column=0, padx=5, pady=5)
        modele_entry = ttk.Entry(edit_window)
        modele_entry.grid(row=1, column=1, padx=5, pady=5)
        modele_entry.insert(0, values[2])
        
        ttk.Label(edit_window, text="Immatriculation:").grid(row=2, column=0, padx=5, pady=5)
        immatriculation_entry = ttk.Entry(edit_window)
        immatriculation_entry.grid(row=2, column=1, padx=5, pady=5)
        immatriculation_entry.insert(0, values[3])
        
        def save_changes():
            try:
                self.cursor.execute("""
                    UPDATE voitures 
                    SET marque = %s, modele = %s, immatriculation = %s
                    WHERE id = %s
                """, (marque_entry.get(), modele_entry.get(), immatriculation_entry.get(), values[0]))
                self.conn.commit()
                messagebox.showinfo("Succès", "Voiture modifiée avec succès")
                self.charger_donnees()
                edit_window.destroy()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {e}")
        
        ttk.Button(edit_window, text="Enregistrer", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)
    
    def supprimer_voiture(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette voiture ?"):
            item = self.tree.item(selected_item[0])
            values = item['values']
            
            try:
                self.cursor.execute("DELETE FROM voitures WHERE id = %s", (values[0],))
                self.conn.commit()
                messagebox.showinfo("Succès", "Voiture supprimée avec succès")
                self.charger_donnees()
            except Error as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    
    def changer_etat(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une voiture")
            return
        
        item = self.tree.item(selected_item[0])
        values = item['values']
        nouvel_etat = "indisponible" if values[4] == "disponible" else "disponible"
        
        try:
            self.cursor.execute("""
                UPDATE voitures 
                SET etat = %s
                WHERE id = %s
            """, (nouvel_etat, values[0]))
            self.conn.commit()
            messagebox.showinfo("Succès", f"État changé à {nouvel_etat}")
            self.charger_donnees()
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors du changement d'état: {e}")
    
    def rechercher_voiture(self):
        search_term = self.search_entry.get()
        if not search_term:
            self.charger_donnees()
            return
        
        try:
            self.cursor.execute("""
                SELECT * FROM voitures 
                WHERE marque LIKE %s 
                OR modele LIKE %s 
                OR immatriculation LIKE %s
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            # Vider le tableau
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Afficher les résultats
            for row in self.cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardAdmin(root)
    root.mainloop()