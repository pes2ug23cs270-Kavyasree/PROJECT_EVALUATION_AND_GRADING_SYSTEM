# ==============================
# STANDARD IMPORTS
# ==============================
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# ==============================
# DATABASE CONFIG
# ==============================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kavya@0108',
    'database': 'project_eval'
}


# Small helper: open connection + cursor
def get_conn_cursor():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    return conn, cursor


# Small helper: run a statement safely and show errors in GUI
def exec_sql(sql, params=None, success_msg="Done"):
    try:
        conn, cursor = get_conn_cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        messagebox.showinfo("Success", success_msg)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        try:
            conn.close()
        except:
            pass


# ============================================================
# MAIN APPLICATION (TABS ARE ORDERED TO MATCH THE RUBRIC FLOW)
# ============================================================
class ProjectEvalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProjectEval Management System")
        self.geometry("1350x820")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=1, fill="both")

        # ---- CRUD Tabs (Create / Read / Update / Delete) ----
        self.init_students_tab()     # Student CRUD
        self.init_teams_tab()        # Team CRUD
        self.init_projects_tab()     # Project CRUD
        self.init_marks_tab()        # Marks CRUD
        self.init_evaluations_tab()  # Evaluation CRUD
        self.init_grades_tab()       # Grade CRUD

        # ---- Reports / Views ----
        self.init_reports_tab()

        # ---- Queries (Nested, Join, Aggregate) ----
        self.init_queries_tab()

        # ---- Users (Create/Grant/List/Delete) ----
        self.init_user_tab()

        # ---- DB Tools (Triggers + Procedures + Views creation) ----
        self.init_dbtools_tab()


    # ============================================================
    # [RUBRIC] STUDENTS — CREATE / READ / UPDATE / DELETE (WITH GUI)
    # ============================================================
    def init_students_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Students")

        columns = ["StudentID","Dept","Year","Fname","Lname","Age","PhoneNo"]
        self.stud_tree = ttk.Treeview(tab, columns=columns, show='headings', height=18)
        for c in columns:
            self.stud_tree.heading(c, text=c)
            self.stud_tree.column(c, width=110, anchor="center")
        self.stud_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.student_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.student_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add (Create)",   command=self.add_student).grid(row=7, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All (Read)",command=self.show_students).grid(row=7, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update",         command=self.update_student).grid(row=8, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete",         command=self.delete_student).grid(row=8, column=1, pady=6, sticky="ew")

        self.show_students()

    def add_student(self):
        vals = [self.student_fields[c].get() for c in self.student_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("INSERT INTO Student VALUES (%s,%s,%s,%s,%s,%s,%s)", vals)
            conn.commit()
            messagebox.showinfo("OK", "Student added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_students()
            try: conn.close()
            except: pass

    def update_student(self):
        vals = [self.student_fields[c].get() for c in self.student_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Student 
                SET Dept=%s, Year=%s, Fname=%s, Lname=%s, Age=%s, PhoneNo=%s 
                WHERE StudentID=%s
            """, (vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[0]))
            conn.commit()
            messagebox.showinfo("OK", "Student updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_students()
            try: conn.close()
            except: pass

    def delete_student(self):
        sid = self.student_fields["StudentID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Student WHERE StudentID=%s", (sid,))
            conn.commit()
            messagebox.showinfo("OK", "Student deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_students()
            try: conn.close()
            except: pass

    def show_students(self):
        self.stud_tree.delete(*self.stud_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Student")
            for row in cursor.fetchall():
                self.stud_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] TEAMS — CRUD (WITH GUI)
    # ============================================================
    def init_teams_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Teams")

        columns=["TeamID","TeamName","Members","StudentID"]
        self.team_tree = ttk.Treeview(tab, columns=columns, show='headings', height=18)
        for c in columns:
            self.team_tree.heading(c, text=c)
            self.team_tree.column(c, width=120, anchor="center")
        self.team_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.team_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.team_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add",    command=self.add_team).grid(row=6, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All", command=self.show_teams).grid(row=6, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update", command=self.update_team).grid(row=7, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete", command=self.delete_team).grid(row=7, column=1, pady=6, sticky="ew")

        self.show_teams()

    def add_team(self):
        vals = [self.team_fields[c].get() for c in self.team_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("INSERT INTO Team VALUES (%s,%s,%s,%s)", vals)
            conn.commit()
            messagebox.showinfo("OK", "Team added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_teams()
            try: conn.close()
            except: pass

    def update_team(self):
        v = [self.team_fields[c].get() for c in self.team_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Team SET TeamName=%s, Members=%s, StudentID=%s 
                WHERE TeamID=%s
            """, (v[1], v[2], v[3], v[0]))
            conn.commit()
            messagebox.showinfo("OK", "Team updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_teams()
            try: conn.close()
            except: pass

    def delete_team(self):
        tid = self.team_fields["TeamID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Team WHERE TeamID=%s", (tid,))
            conn.commit()
            messagebox.showinfo("OK", "Team deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_teams()
            try: conn.close()
            except: pass

    def show_teams(self):
        self.team_tree.delete(*self.team_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Team")
            for row in cursor.fetchall():
                self.team_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] PROJECTS — CRUD (WITH GUI)
    # ============================================================
    def init_projects_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Projects")

        columns=["ProjectID","Title","Domain","Technology","Duration","TeamID"]
        self.project_tree = ttk.Treeview(tab, columns=columns, show='headings', height=18)

        for c in columns:
            self.project_tree.heading(c, text=c)
            self.project_tree.column(c, width=140 if c in ("Title","Technology") else 110, anchor="center")
        self.project_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.project_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.project_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add",    command=self.add_project).grid(row=7, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All", command=self.show_projects).grid(row=7, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update", command=self.update_project).grid(row=8, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete", command=self.delete_project).grid(row=8, column=1, pady=6, sticky="ew")

        self.show_projects()

    def add_project(self):
        vals = [self.project_fields[c].get() for c in self.project_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("INSERT INTO Project VALUES (%s,%s,%s,%s,%s,%s)", vals)
            conn.commit()
            messagebox.showinfo("OK", "Project added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_projects()
            try: conn.close()
            except: pass

    def update_project(self):
        v = [self.project_fields[c].get() for c in self.project_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Project 
                SET Title=%s, Domain=%s, Technology=%s, Duration=%s, TeamID=%s
                WHERE ProjectID=%s
            """, (v[1], v[2], v[3], v[4], v[5], v[0]))
            conn.commit()
            messagebox.showinfo("OK", "Project updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_projects()
            try: conn.close()
            except: pass

    def delete_project(self):
        pid = self.project_fields["ProjectID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Project WHERE ProjectID=%s", (pid,))
            conn.commit()
            messagebox.showinfo("OK", "Project deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_projects()
            try: conn.close()
            except: pass

    def show_projects(self):
        self.project_tree.delete(*self.project_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Project")
            for row in cursor.fetchall():
                self.project_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] MARKS — CRUD (WITH GUI)
    #   + uses Trigger/Procedure (from DB Tools tab) to keep Percentage in sync
    # ============================================================
    def init_marks_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Marks")

        columns=["MarksObtained","MaxMarks","Percentage","EvaluationID"]
        self.marks_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)
        for c in columns:
            self.marks_tree.heading(c, text=c)
            self.marks_tree.column(c, width=130, anchor="center")
        self.marks_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.marks_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.marks_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add",    command=self.add_marks).grid(row=6, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All", command=self.show_marks).grid(row=6, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update", command=self.update_marks).grid(row=7, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete", command=self.delete_marks).grid(row=7, column=1, pady=6, sticky="ew")

        # Optional: call stored procedure to recompute a single EvaluationID
        tk.Button(tab, text="Recalculate % (CALL proc)", command=self.recalc_percentage_for_eid).grid(row=8, column=0, columnspan=2, pady=6, sticky="ew")

        self.show_marks()

    def add_marks(self):
        v = [self.marks_fields[c].get() for c in self.marks_fields]
        try:
            conn, cursor = get_conn_cursor()
            # Percentage is NULL; trigger will compute it automatically IF created
            cursor.execute("INSERT INTO Marks (MarksObtained, MaxMarks, Percentage, EvaluationID) VALUES (%s,%s,NULL,%s)", (v[0], v[1], v[3]))
            conn.commit()
            messagebox.showinfo("OK", "Marks added (Percentage auto via trigger if enabled)")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_marks()
            try: conn.close()
            except: pass

    def update_marks(self):
        v = [self.marks_fields[c].get() for c in self.marks_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Marks 
                SET MarksObtained=%s, MaxMarks=%s, Percentage=NULL
                WHERE EvaluationID=%s
            """, (v[0], v[1], v[3]))
            conn.commit()
            messagebox.showinfo("OK", "Marks updated (Percentage will refresh via trigger on UPDATE if enabled)")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_marks()
            try: conn.close()
            except: pass

    def delete_marks(self):
        eid = self.marks_fields["EvaluationID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Marks WHERE EvaluationID=%s", (eid,))
            conn.commit()
            messagebox.showinfo("OK", "Marks deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_marks()
            try: conn.close()
            except: pass

    def show_marks(self):
        self.marks_tree.delete(*self.marks_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Marks")
            for row in cursor.fetchall():
                self.marks_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass

    def recalc_percentage_for_eid(self):
        """[RUBRIC] PROCEDURE CALL WITH GUI:
           Calls stored procedure sp_recalc_percentage(eid) created in DB Tools.
        """
        eid = self.marks_fields["EvaluationID"].get()
        if not eid:
            messagebox.showerror("Error", "Enter EvaluationID to recalculate")
            return
        try:
            conn, cursor = get_conn_cursor()
            cursor.callproc("sp_recalc_percentage", [int(eid)])
            conn.commit()
            messagebox.showinfo("OK", f"Recalculated Percentage for EvaluationID={eid}")
        except Exception as e:
            messagebox.showerror("Error", f"Procedure call failed: {e}")
        finally:
            self.show_marks()
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] EVALUATIONS — CRUD (WITH GUI)
    # ============================================================
    def init_evaluations_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Evaluations")

        columns=["EvaluationID","TotalMarks","Rounds","EvalDate","Comments"]
        self.eval_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)

        for c in columns:
            self.eval_tree.heading(c, text=c)
            self.eval_tree.column(c, width=130, anchor="center")
        self.eval_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.eval_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.eval_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add",    command=self.add_evaluation).grid(row=6, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All", command=self.show_evaluations).grid(row=6, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update", command=self.update_evaluation).grid(row=7, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete", command=self.delete_evaluation).grid(row=7, column=1, pady=6, sticky="ew")

        self.show_evaluations()

    def add_evaluation(self):
        v = [self.eval_fields[c].get() for c in self.eval_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("INSERT INTO Evaluation VALUES (%s,%s,%s,%s,%s)", v)
            conn.commit()
            messagebox.showinfo("OK", "Evaluation added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_evaluations()
            try: conn.close()
            except: pass

    def update_evaluation(self):
        v = [self.eval_fields[c].get() for c in self.eval_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Evaluation 
                SET TotalMarks=%s, Rounds=%s, EvalDate=%s, Comments=%s
                WHERE EvaluationID=%s
            """, (v[1], v[2], v[3], v[4], v[0]))
            conn.commit()
            messagebox.showinfo("OK", "Evaluation updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_evaluations()
            try: conn.close()
            except: pass

    def delete_evaluation(self):
        eid = self.eval_fields["EvaluationID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Evaluation WHERE EvaluationID=%s", (eid,))
            conn.commit()
            messagebox.showinfo("OK", "Evaluation deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_evaluations()
            try: conn.close()
            except: pass

    def show_evaluations(self):
        self.eval_tree.delete(*self.eval_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Evaluation")
            for row in cursor.fetchall():
                self.eval_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] GRADES — CRUD (WITH GUI)
    # ============================================================
    def init_grades_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Grades")

        columns=["Grade","FinalScore","ProjectID"]
        self.grade_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)
        for c in columns:
            self.grade_tree.heading(c, text=c)
            self.grade_tree.column(c, width=130, anchor="center")
        self.grade_tree.grid(row=0, column=3, rowspan=12, sticky="nsew", padx=10, pady=10)

        self.grade_fields = {c: tk.Entry(tab, width=18) for c in columns}
        for i, c in enumerate(columns):
            tk.Label(tab, text=c).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            self.grade_fields[c].grid(row=i, column=1, padx=6, pady=4)

        tk.Button(tab, text="Add",    command=self.add_grade).grid(row=4, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Show All", command=self.show_grades).grid(row=4, column=1, pady=6, sticky="ew")
        tk.Button(tab, text="Update", command=self.update_grade).grid(row=5, column=0, pady=6, sticky="ew")
        tk.Button(tab, text="Delete", command=self.delete_grade).grid(row=5, column=1, pady=6, sticky="ew")

        self.show_grades()

    def add_grade(self):
        v = [self.grade_fields[c].get() for c in self.grade_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("INSERT INTO Grade VALUES (%s,%s,%s)", v)
            conn.commit()
            messagebox.showinfo("OK", "Grade added")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_grades()
            try: conn.close()
            except: pass

    def update_grade(self):
        v = [self.grade_fields[c].get() for c in self.grade_fields]
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                UPDATE Grade 
                SET Grade=%s, FinalScore=%s 
                WHERE ProjectID=%s
            """, (v[0], v[1], v[2]))
            conn.commit()
            messagebox.showinfo("OK", "Grade updated")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_grades()
            try: conn.close()
            except: pass

    def delete_grade(self):
        pid = self.grade_fields["ProjectID"].get()
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DELETE FROM Grade WHERE ProjectID=%s", (pid,))
            conn.commit()
            messagebox.showinfo("OK", "Grade deleted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.show_grades()
            try: conn.close()
            except: pass

    def show_grades(self):
        self.grade_tree.delete(*self.grade_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM Grade")
            for row in cursor.fetchall():
                self.grade_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] REPORTS (VIEWS) — WITH GUI
    # ============================================================
    def init_reports_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Reports (Views)")

        # Create (or recreate) sample views from GUI via DB Tools tab
        tk.Label(tab, text="Project Summary View").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        tk.Button(tab, text="Load Summary", command=self.show_project_summary).grid(row=0, column=1, padx=6, pady=6)

        columns = ['ProjectID','Title','Domain','Technology','Duration','TeamName','Members','Grade','FinalScore']
        self.report_tree = ttk.Treeview(tab, columns=columns, show='headings', height=12)
        for c in columns:
            self.report_tree.heading(c, text=c)
            self.report_tree.column(c, width=120, anchor="center")
        self.report_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=6)

        tk.Label(tab, text="Top Projects").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.top_tree = ttk.Treeview(tab, columns=["ProjectID","Title","FinalScore"], show='headings', height=8)
        for c in ["ProjectID","Title","FinalScore"]:
            self.top_tree.heading(c, text=c)
            self.top_tree.column(c, width=150 if c == "Title" else 120, anchor="center")
        self.top_tree.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=6)

        tk.Button(tab, text="Load Top Projects", command=self.show_top_projects).grid(row=2, column=1, padx=6, pady=6)

    def show_project_summary(self):
        self.report_tree.delete(*self.report_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM vw_project_summary")
            for row in cursor.fetchall():
                self.report_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Load view failed: {e}")
        finally:
            try: conn.close()
            except: pass

    def show_top_projects(self):
        self.top_tree.delete(*self.top_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT * FROM vw_top_projects LIMIT 10")
            for row in cursor.fetchall():
                self.top_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Load view failed: {e}")
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] QUERIES — NESTED / JOIN / AGGREGATE (WITH GUI)
    # ============================================================
    def init_queries_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Queries")

        # Buttons for each rubric query type
        tk.Button(tab, text="Nested Query (FinalScore > AVG)", command=self.run_nested_query).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        tk.Button(tab, text="Join Query (Student ↔ Team)", command=self.run_join_query).grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        tk.Button(tab, text="Aggregate Query (COUNT by Domain)", command=self.run_aggregate_query).grid(row=2, column=0, padx=6, pady=6, sticky="ew")

        columns = ["Col1","Col2","Col3","Col4","Col5"]
        self.query_tree = ttk.Treeview(tab, columns=columns, show='headings', height=20)
        for c in columns:
            self.query_tree.heading(c, text=c)
            self.query_tree.column(c, width=160, anchor="center")
        self.query_tree.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

    def run_nested_query(self):
        """[RUBRIC] Nested Query with GUI"""
        self.query_tree.delete(*self.query_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                SELECT ProjectID, FinalScore 
                FROM Grade 
                WHERE FinalScore > (SELECT AVG(FinalScore) FROM Grade)
            """)
            rows = cursor.fetchall()
            for r in rows:
                self.query_tree.insert('', tk.END, values=(r[0], r[1], "", "", ""))
            if not rows:
                messagebox.showinfo("Info", "No rows matched the nested query.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass

    def run_join_query(self):
        """[RUBRIC] Join Query with GUI"""
        self.query_tree.delete(*self.query_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                SELECT s.StudentID, s.Fname, t.TeamName
                FROM Student s 
                JOIN Team t ON s.StudentID = t.StudentID
            """)
            rows = cursor.fetchall()
            for r in rows:
                self.query_tree.insert('', tk.END, values=(r[0], r[1], r[2], "", ""))
            if not rows:
                messagebox.showinfo("Info", "No rows found for join result.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass

    def run_aggregate_query(self):
        """[RUBRIC] Aggregate Query with GUI"""
        self.query_tree.delete(*self.query_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("""
                SELECT Domain, COUNT(*) AS TotalProjects 
                FROM Project 
                GROUP BY Domain
            """)
            rows = cursor.fetchall()
            for r in rows:
                self.query_tree.insert('', tk.END, values=(r[0], r[1], "", "", ""))
            if not rows:
                messagebox.showinfo("Info", "No projects grouped by domain.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass


    # ============================================================
    # [RUBRIC] USERS CREATION / VARIED PRIVILEGES — WITH GUI
    # ============================================================
    def init_user_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="User Creation")

        # --- Create user form ---
        tk.Label(tab, text="MySQL Username:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        tk.Label(tab, text="Password:").grid(row=1, column=0, padx=6, pady=6, sticky="w")

        self.user_entry = tk.Entry(tab, width=22)
        self.pass_entry = tk.Entry(tab, width=22, show="*")
        self.user_entry.grid(row=0, column=1, padx=6, pady=6)
        self.pass_entry.grid(row=1, column=1, padx=6, pady=6)

        tk.Label(tab, text="Privileges:").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.priv_select = tk.Listbox(tab, selectmode="multiple", height=6, exportselection=False)
        for p in ["SELECT", "INSERT", "UPDATE", "DELETE", "ALL PRIVILEGES"]:
            self.priv_select.insert(tk.END, p)
        self.priv_select.grid(row=2, column=1, padx=6, pady=6, sticky="ew")

        tk.Button(tab, text="Create User",      command=self.create_user).grid(row=3, column=0, padx=6, pady=6, sticky="ew")
        tk.Button(tab, text="Grant Privileges", command=self.grant_privileges).grid(row=3, column=1, padx=6, pady=6, sticky="ew")

        # --- Users table ---
        tk.Label(tab, text="Existing Users:").grid(row=4, column=0, padx=6, pady=10, sticky="w")
        columns = ["User", "Host"]
        self.user_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=160, anchor="center")
        self.user_tree.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=10, pady=6)

        tk.Button(tab, text="Refresh Users", command=self.load_users).grid(row=6, column=0, padx=6, pady=6, sticky="ew")
        tk.Button(tab, text="Delete User",   command=self.delete_user).grid(row=6, column=1, padx=6, pady=6, sticky="ew")

        self.load_users()

    def create_user(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password")
            return
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute(f"CREATE USER %s@'localhost' IDENTIFIED BY %s", (username, password))
            conn.commit()
            messagebox.showinfo("Success", f"User '{username}' created")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass
            self.load_users()

    def grant_privileges(self):
        username = self.user_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Enter username to grant privileges")
            return
        selections = self.priv_select.curselection()
        if not selections:
            messagebox.showerror("Error", "Choose at least one privilege")
            return

        chosen = [self.priv_select.get(i) for i in selections]
        privilege_sql = "ALL PRIVILEGES" if "ALL PRIVILEGES" in chosen else ", ".join(chosen)

        try:
            conn, cursor = get_conn_cursor()
            cursor.execute(f"GRANT {privilege_sql} ON project_eval.* TO %s@'localhost'", (username,))
            cursor.execute("FLUSH PRIVILEGES")
            conn.commit()
            messagebox.showinfo("Success", "Privileges granted")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass

    def load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("SELECT User, Host FROM mysql.user")
            for row in cursor.fetchall():
                self.user_tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a user to delete")
            return
        user, host = self.user_tree.item(selected[0])["values"]

        # Avoid accidental removal of system accounts
        if user in {"root", "mysql.session", "mysql.sys", "debian-sys-maint"}:
            messagebox.showerror("Error", "Cannot delete system users")
            return

        try:
            conn, cursor = get_conn_cursor()
            cursor.execute(f"DROP USER %s@%s", (user, host))
            cursor.execute("FLUSH PRIVILEGES")
            conn.commit()
            messagebox.showinfo("Deleted", f"User '{user}'@'{host}' removed")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            try: conn.close()
            except: pass
            self.load_users()


    # ============================================================
    # [RUBRIC] TRIGGERS + PROCEDURES/FUNCTIONS — WITH GUI
    #   Tab provides ready-made SQL to:
    #     - Create/Drop trigger: trg_marks_set_percentage
    #     - Create/Drop stored procedure: sp_recalc_percentage(eid)
    #     - Create/Drop views used by Reports
    # ============================================================
    def init_dbtools_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="DB Tools (Triggers/Procedures/Views)")

        # ---- TRIGGER CONTROLS ----
        ttk.Label(tab, text="Trigger: Auto-calc Percentage before INSERT/UPDATE on Marks").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ttk.Button(tab, text="Create Trigger", command=self.create_trigger).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        ttk.Button(tab, text="Drop Trigger",   command=self.drop_trigger).grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        # ---- PROCEDURE CONTROLS ----
        ttk.Label(tab, text="Procedure: sp_recalc_percentage(eid)").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        ttk.Button(tab, text="Create Procedure", command=self.create_procedure).grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        ttk.Button(tab, text="Drop Procedure",   command=self.drop_procedure).grid(row=1, column=2, padx=6, pady=6, sticky="ew")

        # ---- VIEWS CONTROLS ----
        ttk.Label(tab, text="Views: vw_project_summary / vw_top_projects").grid(row=2, column=0, sticky="w", padx=8, pady=8)
        ttk.Button(tab, text="Create/Replace Views", command=self.create_views).grid(row=2, column=1, padx=6, pady=6, sticky="ew")
        ttk.Button(tab, text="Drop Views",           command=self.drop_views).grid(row=2, column=2, padx=6, pady=6, sticky="ew")

        ttk.Label(tab, text="Use these buttons to demo rubric points for Triggers / Procedures / Views with GUI.").grid(row=3, column=0, columnspan=3, padx=8, pady=10, sticky="w")

    # ---------- Trigger DDL ----------
    def create_trigger(self):
        """
        Trigger: trg_marks_set_percentage
        BEFORE INSERT/UPDATE on Marks to compute Percentage = (MarksObtained / MaxMarks) * 100
        """
        ddl_drop = "DROP TRIGGER IF EXISTS trg_marks_set_percentage"
        ddl_create = """
            CREATE TRIGGER trg_marks_set_percentage
            BEFORE INSERT ON Marks
            FOR EACH ROW
            BEGIN
                IF NEW.MaxMarks IS NOT NULL AND NEW.MaxMarks <> 0 AND NEW.MarksObtained IS NOT NULL THEN
                    SET NEW.Percentage = (NEW.MarksObtained / NEW.MaxMarks) * 100;
                ELSE
                    SET NEW.Percentage = NULL;
                END IF;
            END
        """
        # Also cover UPDATE case with a second trigger
        ddl_drop2 = "DROP TRIGGER IF EXISTS trg_marks_set_percentage_upd"
        ddl_create2 = """
            CREATE TRIGGER trg_marks_set_percentage_upd
            BEFORE UPDATE ON Marks
            FOR EACH ROW
            BEGIN
                IF NEW.MaxMarks IS NOT NULL AND NEW.MaxMarks <> 0 AND NEW.MarksObtained IS NOT NULL THEN
                    SET NEW.Percentage = (NEW.MarksObtained / NEW.MaxMarks) * 100;
                ELSE
                    SET NEW.Percentage = NULL;
                END IF;
            END
        """
        try:
            conn, cursor = get_conn_cursor()
            for stmt in (ddl_drop, ddl_create, ddl_drop2, ddl_create2):
                cursor.execute(stmt)
            conn.commit()
            messagebox.showinfo("Success", "Trigger(s) created")
        except Exception as e:
            messagebox.showerror("Error", f"Trigger creation failed: {e}")
        finally:
            try: conn.close()
            except: pass

    def drop_trigger(self):
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DROP TRIGGER IF EXISTS trg_marks_set_percentage")
            cursor.execute("DROP TRIGGER IF EXISTS trg_marks_set_percentage_upd")
            conn.commit()
            messagebox.showinfo("Success", "Trigger(s) dropped")
        except Exception as e:
            messagebox.showerror("Error", f"Dropping trigger failed: {e}")
        finally:
            try: conn.close()
            except: pass

    # ---------- Procedure DDL ----------
    def create_procedure(self):
        """
        Procedure: sp_recalc_percentage(eid INT)
        Recomputes Percentage for a given EvaluationID in Marks table.
        """
        ddl_drop = "DROP PROCEDURE IF EXISTS sp_recalc_percentage"
        ddl_create = """
            CREATE PROCEDURE sp_recalc_percentage(IN p_eid INT)
            BEGIN
                UPDATE Marks
                SET Percentage = CASE 
                                   WHEN MaxMarks IS NOT NULL AND MaxMarks <> 0 AND MarksObtained IS NOT NULL
                                   THEN (MarksObtained / MaxMarks) * 100
                                   ELSE NULL
                                 END
                WHERE EvaluationID = p_eid;
            END
        """
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute(ddl_drop)
            cursor.execute(ddl_create)
            conn.commit()
            messagebox.showinfo("Success", "Procedure created")
        except Exception as e:
            messagebox.showerror("Error", f"Procedure creation failed: {e}")
        finally:
            try: conn.close()
            except: pass

    def drop_procedure(self):
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DROP PROCEDURE IF EXISTS sp_recalc_percentage")
            conn.commit()
            messagebox.showinfo("Success", "Procedure dropped")
        except Exception as e:
            messagebox.showerror("Error", f"Dropping procedure failed: {e}")
        finally:
            try: conn.close()
            except: pass

    # ---------- Views DDL ----------
    def create_views(self):
        """
        Views used by Reports tab:
          1) vw_project_summary: join Project, Team, Grade to show a summary
          2) vw_top_projects: top projects ordered by FinalScore desc
        Adjust field names if your schema differs.
        """
        stmts = [
            "DROP VIEW IF EXISTS vw_project_summary",
            """CREATE VIEW vw_project_summary AS
               SELECT 
                 p.ProjectID, p.Title, p.Domain, p.Technology, p.Duration,
                 t.TeamName, t.Members,
                 g.Grade, g.FinalScore
               FROM Project p
               LEFT JOIN Team t ON p.TeamID = t.TeamID
               LEFT JOIN Grade g ON p.ProjectID = g.ProjectID""",
            "DROP VIEW IF EXISTS vw_top_projects",
            """CREATE VIEW vw_top_projects AS
               SELECT p.ProjectID, p.Title, g.FinalScore
               FROM Project p
               JOIN Grade g ON p.ProjectID = g.ProjectID
               ORDER BY g.FinalScore DESC"""
        ]
        try:
            conn, cursor = get_conn_cursor()
            for s in stmts:
                cursor.execute(s)
            conn.commit()
            messagebox.showinfo("Success", "Views created/replaced")
        except Exception as e:
            messagebox.showerror("Error", f"Creating views failed: {e}")
        finally:
            try: conn.close()
            except: pass

    def drop_views(self):
        try:
            conn, cursor = get_conn_cursor()
            cursor.execute("DROP VIEW IF EXISTS vw_project_summary")
            cursor.execute("DROP VIEW IF EXISTS vw_top_projects")
            conn.commit()
            messagebox.showinfo("Success", "Views dropped")
        except Exception as e:
            messagebox.showerror("Error", f"Dropping views failed: {e}")
        finally:
            try: conn.close()
            except: pass


# ==============================
# RUN APPLICATION
# ==============================
if __name__ == "__main__":
    ProjectEvalApp().mainloop()
