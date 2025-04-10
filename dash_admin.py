import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import threading
import time
import json
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DashboardAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Parking Management System - Admin Dashboard")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Initialize database connection
        self.initialize_database()
        
        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Initialize data refresh thread
        self.start_data_refresh()
        
    def initialize_database(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="parc_automobile"
            )
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Error as e:
            messagebox.showerror("Error", f"Database connection error: {e}")
            
    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS parking_spaces (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    space_number VARCHAR(10) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'available',
                    vehicle_id INT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    license_plate VARCHAR(20) UNIQUE NOT NULL,
                    make VARCHAR(50),
                    model VARCHAR(50),
                    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    exit_time TIMESTAMP,
                    payment_status VARCHAR(20) DEFAULT 'pending'
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE,
                    amount DECIMAL(10,2),
                    payment_method VARCHAR(20),
                    vehicle_id INT
                )
            """)
            
            self.conn.commit()
        except Error as e:
            messagebox.showerror("Error", f"Table creation error: {e}")
            
    def create_sidebar(self):
        # Create sidebar frame
        self.sidebar = ctk.CTkFrame(self.main_container, width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Add logo
        logo_label = ctk.CTkLabel(self.sidebar, text="PMS", font=("Arial", 24, "bold"))
        logo_label.pack(pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Parking Spaces", self.show_parking_spaces),
            ("Vehicles", self.show_vehicles),
            ("Revenue", self.show_revenue),
            ("Reports", self.show_reports),
            ("Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=200,
                height=40,
                corner_radius=10
            )
            btn.pack(pady=5, padx=10)
            
        # Add theme toggle
        self.theme_btn = ctk.CTkButton(
            self.sidebar,
            text="Toggle Theme",
            command=self.toggle_theme,
            width=200,
            height=40,
            corner_radius=10
        )
        self.theme_btn.pack(side=tk.BOTTOM, pady=20, padx=10)
        
    def create_main_content(self):
        # Create main content frame
        self.main_content = ctk.CTkFrame(self.main_container)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        self.header = ctk.CTkFrame(self.main_content, height=60)
        self.header.pack(fill=tk.X, padx=10, pady=10)
        
        # Add header widgets
        self.title_label = ctk.CTkLabel(self.header, text="Dashboard", font=("Arial", 20, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=20)
        
        # Add notification button
        self.notification_btn = ctk.CTkButton(
            self.header,
            text="🔔",
            width=40,
            height=40,
            corner_radius=20,
            command=self.show_notifications
        )
        self.notification_btn.pack(side=tk.RIGHT, padx=20)
        
        # Create dashboard content
        self.dashboard_content = ctk.CTkFrame(self.main_content)
        self.dashboard_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize dashboard widgets
        self.create_dashboard_widgets()
        
    def create_dashboard_widgets(self):
        # Create grid layout for widgets
        self.dashboard_content.grid_columnconfigure((0, 1, 2), weight=1)
        self.dashboard_content.grid_rowconfigure((0, 1), weight=1)
        
        # Parking Space Status
        self.space_status_frame = ctk.CTkFrame(self.dashboard_content)
        self.space_status_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Revenue Chart
        self.revenue_frame = ctk.CTkFrame(self.dashboard_content)
        self.revenue_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Vehicle Statistics
        self.vehicle_stats_frame = ctk.CTkFrame(self.dashboard_content)
        self.vehicle_stats_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Recent Activity
        self.activity_frame = ctk.CTkFrame(self.dashboard_content)
        self.activity_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        # Update widgets with data
        self.update_dashboard_widgets()
        
    def update_dashboard_widgets(self):
        # Update parking space status
        self.update_space_status()
        
        # Update revenue chart
        self.update_revenue_chart()
        
        # Update vehicle statistics
        self.update_vehicle_stats()
        
        # Update recent activity
        self.update_recent_activity()
        
    def update_space_status(self):
        try:
            self.cursor.execute("SELECT status, COUNT(*) FROM parking_spaces GROUP BY status")
            results = self.cursor.fetchall()
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(5, 5))
            statuses = [row[0] for row in results]
            counts = [row[1] for row in results]
            
            ax.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Add canvas to frame
            canvas = FigureCanvasTkAgg(fig, master=self.space_status_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Error as e:
            messagebox.showerror("Error", f"Error updating space status: {e}")
            
    def update_revenue_chart(self):
        try:
            self.cursor.execute("""
                SELECT DATE(date) as day, SUM(amount) as total
                FROM revenue
                GROUP BY DATE(date)
                ORDER BY day DESC
                LIMIT 7
            """)
            results = self.cursor.fetchall()
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(5, 5))
            days = [row[0] for row in results]
            amounts = [row[1] for row in results]
            
            ax.bar(days, amounts)
            ax.set_title("Daily Revenue")
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount")
            
            # Add canvas to frame
            canvas = FigureCanvasTkAgg(fig, master=self.revenue_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Error as e:
            messagebox.showerror("Error", f"Error updating revenue chart: {e}")
            
    def update_vehicle_stats(self):
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_vehicles,
                    SUM(CASE WHEN exit_time IS NULL THEN 1 ELSE 0 END) as current_vehicles,
                    AVG(TIMESTAMPDIFF(HOUR, entry_time, COALESCE(exit_time, NOW()))) as avg_duration
                FROM vehicles
            """)
            result = self.cursor.fetchone()
            
            # Create stats display
            stats_frame = ctk.CTkFrame(self.vehicle_stats_frame)
            stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(stats_frame, text=f"Total Vehicles: {result[0]}", font=("Arial", 14)).pack(pady=5)
            ctk.CTkLabel(stats_frame, text=f"Current Vehicles: {result[1]}", font=("Arial", 14)).pack(pady=5)
            ctk.CTkLabel(stats_frame, text=f"Avg Duration: {result[2]:.1f} hours", font=("Arial", 14)).pack(pady=5)
            
        except Error as e:
            messagebox.showerror("Error", f"Error updating vehicle stats: {e}")
            
    def update_recent_activity(self):
        try:
            self.cursor.execute("""
                SELECT v.license_plate, v.entry_time, ps.space_number, ps.status
                FROM vehicles v
                JOIN parking_spaces ps ON v.id = ps.vehicle_id
                ORDER BY v.entry_time DESC
                LIMIT 10
            """)
            results = self.cursor.fetchall()
            
            # Create activity list
            activity_list = ctk.CTkScrollableFrame(self.activity_frame)
            activity_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for row in results:
                activity_item = ctk.CTkFrame(activity_list)
                activity_item.pack(fill=tk.X, pady=5)
                
                ctk.CTkLabel(activity_item, text=f"Vehicle {row[0]} entered at {row[1]}", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
                ctk.CTkLabel(activity_item, text=f"Space {row[2]} - {row[3]}", font=("Arial", 12)).pack(side=tk.RIGHT, padx=5)
                
        except Error as e:
            messagebox.showerror("Error", f"Error updating recent activity: {e}")
            
    def start_data_refresh(self):
        def refresh_data():
            while True:
                self.update_dashboard_widgets()
                time.sleep(60)  # Refresh every minute
                
        refresh_thread = threading.Thread(target=refresh_data, daemon=True)
        refresh_thread.start()
        
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
    def show_notifications(self):
        # Create notification window
        notification_window = ctk.CTkToplevel(self)
        notification_window.title("Notifications")
        notification_window.geometry("400x300")
        
        # Add notification list
        notification_list = ctk.CTkScrollableFrame(notification_window)
        notification_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample notifications
        notifications = [
            "Parking lot is 90% full",
            "New vehicle entered at Space A1",
            "Payment received for Vehicle ABC123",
            "System maintenance scheduled for tomorrow"
        ]
        
        for notification in notifications:
            notification_item = ctk.CTkFrame(notification_list)
            notification_item.pack(fill=tk.X, pady=5)
            
            ctk.CTkLabel(notification_item, text=notification, font=("Arial", 12)).pack(padx=5, pady=5)
            
    def show_dashboard(self):
        self.title_label.configure(text="Dashboard")
        self.create_dashboard_widgets()
        
    def show_parking_spaces(self):
        self.title_label.configure(text="Parking Spaces")
        # Implement parking spaces view
        
    def show_vehicles(self):
        self.title_label.configure(text="Vehicles")
        # Implement vehicles view
        
    def show_revenue(self):
        self.title_label.configure(text="Revenue")
        # Implement revenue view
        
    def show_reports(self):
        self.title_label.configure(text="Reports")
        # Implement reports view
        
    def show_settings(self):
        self.title_label.configure(text="Settings")
        # Implement settings view

if __name__ == "__main__":
    app = DashboardAdmin()
    app.mainloop()
