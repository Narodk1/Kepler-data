import tkinter as tk
import re
from tkinter import ttk
import pandas as pd
from tkinter.font import Font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from connect_mysql import connect_database
from tkinter import filedialog

class ExoplanetApp:
    def __init__(self, root, data_frame):
        self.root = root
        self.root.title("Kepler Data")
        # Connexion à la base de données en utilisant la fonction importée
        conn = connect_database()
        cursor = conn.cursor()

        # Interface graphique
        self.kepler_label = ttk.Label(
            root, text="Kepler Data", font=("Helvetica", 16, "bold"))
        self.label = ttk.Label(root, text="Nom de Kepler:")
        self.entry = ttk.Entry(root)
        self.search_button = ttk.Button(
            root, text="Rechercher", command=self.search_exoplanet)
        self.telecharger_button = ttk.Button(
            root, text="Telecharger", command=self.telecharger)
        self.precedent_button = ttk.Button(
            root, text="Précédent", command=self.precedent_exoplanet)
        self.suivant_button = ttk.Button(
            root, text="Suivant", command=self.suivant_exoplanet)


        # Columns for Treeview
        colonne = ('Kepler Identification', 'KOI Name', 'Nom Kepler', 'Disposition des archives Kepler', 'Score de disposition',
                   'Période orbitale ', 'Rayon planétaire', 'Température d\'équilibre', 'Numéro de planète TCE', 'Masse stellaire')
        self.tree = ttk.Treeview(root, columns=colonne, show='headings')
        
        for col in colonne:
            self.tree.heading(
                col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=Font().measure(col))  # Mesurer la largeur du texte de l'en-tête
          
        mapping_col_treeview = {
            'kepid': 'Kepler Identification',
            'kepoi_name': 'KOI Name',
            'kepler_name': 'Nom Kepler',
            'koi_disposition': 'Disposition des archives Kepler',
            'koi_score': 'Score de disposition',
            'koi_period': 'Période orbitale',
            'koi_prad': 'Rayon planétaire',
            'koi_teq': 'Température d\'équilibre',
            'koi_tce_plnt_num': 'Numéro de planète TCE',
            'koi_smass': 'Masse stellaire'
        }

        # Renommer les colonnes du DataFrame en fonction du mapping
        data_frame.rename(columns=mapping_col_treeview, inplace=True)

        self.data_frame = data_frame
        self.load_dataframe()

        self.kepler_label.grid(row=0, column=0, columnspan=3, pady=10)
        self.label.grid(row=1, column=0, padx=10, pady=10)
        self.entry.grid(row=1, column=1, padx=10, pady=10)
        self.search_button.grid(row=1, column=2, padx=10, pady=10)
        self.tree.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.precedent_button.grid(row=3, column=0, padx=10, pady=10)
        self.suivant_button.grid(row=3, column=1, padx=10, pady=10)
        self.telecharger_button.grid(row=3, column=2, padx=10, pady=10)
        self.etiquette_score = ttk.Label(root, text="Score de disposition:")
        self.combobox_score = ttk.Combobox(root, values=[], state="readonly")
        self.etiquette_score.grid(row=5, column=0, padx=10, pady=10)
        self.combobox_score.grid(row=5, column=1, padx=10, pady=10)
        self.plot_button = ttk.Button(root, text="Afficher les Graphiques", command=self.affichage_plots)
        self.plot_button.grid(row=5, column=2, columnspan=3, pady=10)
        self.combobox_score.bind('<<ComboboxSelected>>', lambda event: self.filtrer_par_score())

        # Radio btn
        self.filter_var = tk.StringVar()
        self.filter_var.set("All")
        self.all_radio = ttk.Radiobutton(
            root, text="Tous les donnees", variable=self.filter_var, value="All", command=self.filter_exoplanets)
        self.confirmed_radio = ttk.Radiobutton(
            root, text="Confirmed", variable=self.filter_var, value="Confirmed", command=self.filter_exoplanets)
        self.false_radio = ttk.Radiobutton(
            root, text="False Positive", variable=self.filter_var, value="False", command=self.filter_exoplanets)
        self.all_radio.grid(row=4, column=0, pady=10)
        self.confirmed_radio.grid(row=4, column=1, pady=10)
        self.false_radio.grid(row=4, column=2, pady=10)
        self.charger_scores_bd()
        # print(self.data_frame.columns) pour debugger 

        try:
                  
            # Insérer des données dans la table uniquement si elles n'existent pas déjà
            for i, exoplanet in self.data_frame.iterrows():
                kepid = exoplanet['Kepler Identification']

            # Vérifier si l'enregistrement existe déjà dans la base de données
                cursor.execute(
                    'SELECT COUNT(*) FROM keplerdata WHERE kepid = %s', (kepid,))
                count = cursor.fetchone()[0]

                # Si l'enregistrement n'existe pas, l'insérer dans la base de données
                if count == 0:
                #    print(f"Insertion des données pour kepid={kepid}, koi_score={exoplanet['koi_score']}") debug 
                   cursor.execute('''
                        INSERT INTO kepler_projet.keplerdata (kepid, kepoi_name, kepler_name, koi_disposition, koi_score, koi_period, koi_prad, koi_teq, koi_tce_plnt_num, koi_smass)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (kepid, exoplanet['KOI Name'], exoplanet['Nom Kepler'], exoplanet['Disposition des archives Kepler'], exoplanet['Score de disposition'], exoplanet['Période orbitale'], exoplanet['Rayon planétaire'], exoplanet['Température d\'équilibre'], exoplanet['Numéro de planète TCE'], exoplanet['Masse stellaire']))

                # Validation des changements et fermeture de la connexion  
            conn.commit()
            conn.close()
            print("Données insérées dans la base de données avec succès!")

        except Exception as e:
            print(f"Erreur SQL lors de l'insertion dans la base de données: {str(e)}")

        self.current_index = 0
        self.curseur_exoplanet()

    def affichage_plots(self):
        # Créer une nouvelle fenêtre pour les graphiques
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Graphiques Exoplanètes")

        # Créer un cadre pour les graphiques
        graph_frame = ttk.Frame(graph_window)
        graph_frame.pack(fill=tk.BOTH, expand=True)

        # Créer des graphiques en utilisant la bibliothèque Matplotlib
        self.temperature_chart(graph_frame)
        self.planet_rayon_chart(graph_frame)

    def temperature_chart(self, frame):
        # Créer un graphique de la distribution de la température d'équilibre
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.hist(self.data_frame['Température d\'équilibre'], bins=20, edgecolor='black')
        ax.set_title('Distribution de la Température d\'équilibre des Exoplanètes')
        ax.set_xlabel('Température d\'équilibre')
        ax.set_ylabel('Nombre d\'Exoplanètes')
        # Ajouter le graphique à la fenêtre
        canvas = FigureCanvasTkAgg(figure, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def planet_rayon_chart(self, frame):
        # Créer un graphique de la distribution des rayons planétaires
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.hist(self.data_frame['Rayon planétaire'], bins=20, edgecolor='black')
        ax.set_title('Distribution des Rayons Planétaires')
        ax.set_xlabel('Rayon Planétaire')
        ax.set_ylabel('Nombre d\'Exoplanètes')

        # Ajouter le graphique à la fenêtre
        canvas = FigureCanvasTkAgg(figure, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def reset_radio_buttons(self):
        self.filter_var.set("All")
        self.all_radio.state(['!selected'])
        self.confirmed_radio.state(['!selected'])
        self.false_radio.state(['!selected'])
        
    def filter_exoplanets(self):
        filter_value = self.filter_var.get()
        
        if filter_value == "All":
            result_df = self.data_frame
        elif filter_value == "Confirmed":
            result_df = self.data_frame[self.data_frame['Disposition des archives Kepler'] == 'CONFIRMED']
        elif filter_value == "False":
            result_df = self.data_frame[self.data_frame['Disposition des archives Kepler']== 'FALSE POSITIVE']
        else:
            result_df = pd.DataFrame()
            
        self.update_treeview(result_df)

    def charger_scores_bd(self):
        try:
            conn = connect_database()
            curseur = conn.cursor()
            # Sélectionnez les scores de disposition distincts depuis la base de données
            curseur.execute('SELECT DISTINCT koi_score FROM keplerdata')
            scores = curseur.fetchall()

            # Mettez à jour la Combobox avec les scores récupérés
            self.combobox_score['values'] = scores

            # Fermez la connexion à la base de données
            conn.close()

        except Exception as e:
            print(f"Erreur lors du chargement des scores depuis la base de données : {str(e)}")

    def filtrer_par_score(self):
        score_selectionne = self.combobox_score.get()
        # print("Score sélectionné :", score_selectionne) Pour Debugger
        if score_selectionne:
            try:
                conn = connect_database(    )
                curseur = conn.cursor()

                # Utilisez une requête SQL pour récupérer les données filtrées
                query = f"SELECT  kepid , kepoi_name ,kepler_name,koi_disposition ,koi_score,koi_period ,koi_prad ,koi_teq , koi_tce_plnt_num,koi_smass FROM keplerdata WHERE koi_score = '{score_selectionne}'"
                curseur.execute(query)
                resultat = curseur.fetchall()
                colonnes = [desc[0] for desc in curseur.description]

                # Créez un DataFrame à partir des résultats de la requête
                resultat_dataframe = pd.DataFrame(resultat, columns=colonnes)

                # Mettez à jour le Treeview avec les données filtrées
                self.update_treeview(resultat_dataframe)
                self.reset_radio_buttons()
                #Vider la combobox apres la mise à jour des données 
                self.combobox_score.set('')

                # Fermez la connexion à la base de données
                conn.close()

            except Exception as e:
                print(f"Erreur lors de la récupération des données filtrées : {str(e)}")
        else:
            self.update_treeview(self.data_frame)

    def update_treeview(self, new_data):
        # Nettoyer les donnees existe
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Inserer des nouvelle donnes
        for i, exoplanet in new_data.iterrows():
            self.tree.insert('', 'end', values=exoplanet.tolist())

    def search_exoplanet(self):
        #renvoie true si la fct est appelé
        if hasattr(self, 'label_non_trouver'):
            self.label_non_trouver.destroy()

        search_text = self.entry.get()

        if search_text:
            search_text = "".join(search_text.split())
            # Recherche par Kepler Name (case-insensitive, ignore spaces)
            pattern = re.compile(re.escape(search_text), re.IGNORECASE) 
            result_df = self.data_frame[self.data_frame['Nom Kepler'].str.replace(" ", "").str.contains(pattern, na=False)]
        else:
            # Afficher toutes les données si la barre de recherche est vide
            result_df = self.data_frame
        self.update_treeview(result_df)

        if not result_df.empty:
            # self.clear_fields()
            self.current_index = self.data_frame.index.get_loc( result_df.index[0])
            self.curseur_exoplanet()
        else:
            self.label_exo_non_trouve()
            
    def clear_fields(self):
        self.entry.delete(0, 'end')

    def label_exo_non_trouve(self):
        self.label_non_trouver = ttk.Label(
            self.root, text="Le Kepler  n'existe pas!!", foreground='red')
        self.label_non_trouver.grid(row=4, column=0, columnspan=3, pady=10)

    # btn de telecharge
    def telecharger(self):
            # Sélectionnez l'emplacement du fichier pour sauvegarder les données
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichiers Excel", "*.xlsx"), ("Tous les fichiers", "*.*")],
            title="Enregistrer les données dans un fichier Excel"
        )

        # Si l'utilisateur n'a pas annulé la boîte de dialogue
        if file_path:
            # Sauvegardez les données actuelles du DataFrame dans un fichier Excel
            self.data_frame.to_excel(file_path, index=False)
            print(f"Les données ont été sauvegardées dans {file_path}")



    # btn precedent
    def precedent_exoplanet(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.curseur_exoplanet()

    # btn suivant
    def suivant_exoplanet(self):
        if self.current_index < len(self.data_frame) - 1:
            self.current_index += 1
            self.curseur_exoplanet()

    # affichage de la ligne ou se retrouve le curseur
    def curseur_exoplanet(self):
        children = self.tree.get_children()
        if self.current_index < len(children):
            item = children[self.current_index]
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)  # Faire défiler jusqu'à l'élément sélectionné
        else:
            self.current_index = 0
            print("Indice Hors Table!!")

    # Charge les données depuis le DataFrame dans le tableau de l'interface graphique
    
    def load_dataframe(self):                        #trier par masse stellaire
        sorted_data = self.data_frame.sort_values(by='Masse stellaire', ascending=False)
        # Effacer les anciennes données du tableau
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Charger les nouvelles données triées dans le tableau
        for i, exoplanet in sorted_data.iterrows():
            self.tree.insert('', 'end', values=exoplanet.tolist())


    def __del__(self):
        pass

if __name__ == "__main__":
    # Charger les données depuis le fichier CSV
    csv_file = './Kepler_Data_Vf.csv'
    df = pd.read_csv(csv_file)
    root = tk.Tk()
    app = ExoplanetApp(root, df.fillna(""))
    root.mainloop()
