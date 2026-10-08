import cv2
import numpy as np
import face_recognition
import os
import csv
import datetime
import pickle
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading

class AttendanceSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.face_locations = []
        self.face_encodings = []
        self.process_this_frame = True
        self.attendance_list = set()
        self.encoding_file = "face_encodings.pkl"
        
        # Initialize webcam
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            print("Error: Could not open webcam")
            exit()
        
        self.setup_ui()
        self.load_encodings()
        self.mark_attendance_thread = None
        
    def load_encodings(self):
        """Load face encodings from file or train if not exists"""
        if os.path.exists(self.encoding_file):
            with open(self.encoding_file, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                self.known_face_ids = data['ids']
            print(f"Loaded {len(self.known_face_names)} faces from encodings")
        else:
            print("No encodings found. Please train the system first.")
            messagebox.showwarning("Warning", "No face encodings found. Please train the system with student faces.")
            
    def save_encodings(self):
        """Save face encodings to file"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names,
            'ids': self.known_face_ids
        }
        with open(self.encoding_file, 'wb') as f:
            pickle.dump(data, f)
        print("Encodings saved successfully")
        
    def train_system(self):
        """Train the system with images from the 'students' directory"""
        student_folder = "students"
        if not os.path.exists(student_folder):
            os.makedirs(student_folder)
            messagebox.showinfo("Info", "Created 'students' folder. Please add student images.")
            return
            
        # Clear existing encodings
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        for student_file in os.listdir(student_folder):
            if student_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Extract name and ID from filename (format: ID_Name.jpg)
                    file_parts = student_file.split('_')
                    if len(file_parts) >= 2:
                        student_id = file_parts[0]
                        student_name = '_'.join(file_parts[1:]).split('.')[0]
                    else:
                        student_name = student_file.split('.')[0]
                        student_id = student_name
                    
                    image_path = os.path.join(student_folder, student_file)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(student_name)
                        self.known_face_ids.append(student_id)
                        print(f"Trained: {student_name} (ID: {student_id})")
                    else:
                        print(f"No face found in {student_file}")
                except Exception as e:
                    print(f"Error processing {student_file}: {e}")
                    
        self.save_encodings()
        messagebox.showinfo("Success", f"Trained {len(self.known_face_names)} faces successfully!")
        
    def mark_attendance(self, student_name, student_id):
        """Mark attendance in CSV file"""
        if student_id not in self.attendance_list:
            self.attendance_list.add(student_id)
            
            # Get current date and time
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            
            # Create attendance CSV if it doesn't exist
            filename = f"attendance_{date}.csv"
            file_exists = os.path.isfile(filename)
            
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Student ID', 'Name', 'Date', 'Time'])
                writer.writerow([student_id, student_name, date, time])
                
            print(f"Marked attendance for {student_name} at {time}")
            
    def process_frame(self):
        """Process video frame for face recognition"""
        ret, frame = self.video_capture.read()
        if not ret:
            return None
            
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Only process every other frame
        if self.process_this_frame:
            # Find faces in the frame
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            
            self.face_names = []
            for face_encoding in self.face_encodings:
                # Compare faces
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                student_id = None
                
                # Use face distance for better accuracy
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]
                    self.mark_attendance(name, student_id)
                
                self.face_names.append((name, student_id))
                
        self.process_this_frame = not self.process_this_frame
        
        # Display results
        for (top, right, bottom, left), (name, student_id) in zip(self.face_locations, self.face_names):
            # Scale back up since we scaled down
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw box around face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw label with name and ID
            label = f"{name} ({student_id})" if student_id else name
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
        
        return frame
        
    def setup_ui(self):
        """Setup GUI interface"""
        self.root = tk.Tk()
        self.root.title("AI Attendance System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Title
        title_label = tk.Label(self.root, text="AI Attendance System", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # Main frame for video and controls
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Video display frame
        self.video_frame = tk.Label(main_frame, bg='#333')
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#f0f0f0', width=250)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Attendance status
        status_label = tk.Label(control_frame, text="Attendance Status", 
                               font=('Arial', 16, 'bold'), bg='#f0f0f0')
        status_label.pack(pady=10)
        
        # Attendance list
        self.attendance_listbox = tk.Listbox(control_frame, height=15, width=30, 
                                            font=('Arial', 10))
        self.attendance_listbox.pack(pady=10)
        
        # Buttons
        train_btn = tk.Button(control_frame, text="Train System", 
                             command=self.train_system, bg='#4CAF50', fg='white',
                             font=('Arial', 12), width=20, height=2)
        train_btn.pack(pady=5)
        
        export_btn = tk.Button(control_frame, text="Export Attendance", 
                              command=self.export_attendance, bg='#2196F3', fg='white',
                              font=('Arial', 12), width=20, height=2)
        export_btn.pack(pady=5)
        
        clear_btn = tk.Button(control_frame, text="Clear Today's Attendance", 
                             command=self.clear_attendance, bg='#f44336', fg='white',
                             font=('Arial', 12), width=20, height=2)
        clear_btn.pack(pady=5)
        
        # Help text
        help_text = """
        Instructions:
        1. Add student photos to 'students' folder
        2. Format: ID_Name.jpg (e.g., 001_John.jpg)
        3. Click 'Train System' to train
        4. Faces will be recognized automatically
        5. Attendance is saved daily
        """
        help_label = tk.Label(control_frame, text=help_text, justify=tk.LEFT,
                             bg='#e8e8e8', font=('Arial', 9), padx=10, pady=10)
        help_label.pack(pady=20)
        
        # Total count
        self.count_label = tk.Label(control_frame, text="Present: 0", 
                                   font=('Arial', 12), bg='#f0f0f0')
        self.count_label.pack(pady=5)
        
        # Update UI
        self.update_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def update_ui(self):
        """Update the UI with new frames"""
        frame = self.process_frame()
        if frame is not None:
            # Convert to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize to fit the display
            img.thumbnail((640, 480))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
            
            # Update attendance count
            self.count_label.config(text=f"Present: {len(self.attendance_list)}")
            
            # Update attendance list
            self.attendance_listbox.delete(0, tk.END)
            for student_id in sorted(self.attendance_list):
                # Find name for this ID
                try:
                    idx = self.known_face_ids.index(student_id)
                    name = self.known_face_names[idx]
                    self.attendance_listbox.insert(tk.END, f"{student_id} - {name}")
                except ValueError:
                    self.attendance_listbox.insert(tk.END, f"{student_id}")
                    
        # Schedule next update
        self.root.after(30, self.update_ui)
        
    def export_attendance(self):
        """Export attendance to CSV file"""
        if not self.attendance_list:
            messagebox.showinfo("Info", "No attendance records to export")
            return
            
        now = datetime.datetime.now()
        filename = f"attendance_export_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Student ID', 'Name'])
            for student_id in sorted(self.attendance_list):
                try:
                    idx = self.known_face_ids.index(student_id)
                    name = self.known_face_names[idx]
                    writer.writerow([student_id, name])
                except ValueError:
                    writer.writerow([student_id, "Unknown"])
                    
        messagebox.showinfo("Success", f"Attendance exported to {filename}")
        
    def clear_attendance(self):
        """Clear current attendance list"""
        if messagebox.askyesno("Confirm", "Clear today's attendance?"):
            self.attendance_list.clear()
            self.attendance_listbox.delete(0, tk.END)
            self.count_label.config(text="Present: 0")
            messagebox.showinfo("Success", "Attendance cleared")
        
    def on_closing(self):
        """Clean up on window close"""
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.root.destroy()
        
    def run(self):
        """Start the attendance system"""
        self.root.mainloop()

def main():
    # Check for required directories
    if not os.path.exists("students"):
        os.makedirs("students")
        print("Created 'students' folder. Please add student images.")
        
    # Run the attendance system
    system = AttendanceSystem()
    system.run()

if __name__ == "__main__":
    main()