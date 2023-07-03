from flask import Flask, request, jsonify, render_template, redirect, send_file, url_for
import pandas as pd
import json
import os
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Vérifier si le fichier est présent dans la requête
    if 'file' not in request.files:
        return jsonify({'error': 'No file found'})

    file = request.files['file']
    
    # Vérifier si un fichier a été sélectionné
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    # Vérifier si le fichier est au format CSV
    if file.filename.endswith('.csv'):
        # Lire le fichier CSV avec pandas
        df = pd.read_csv(file)
        
        # Effectuer les opérations souhaitées sur les données
        # Ici, nous convertissons toutes les valeurs en majuscules
        df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
        
        # Convertir les résultats en format JSON
        results = df.to_dict(orient='records')
        
        # Générer un nom de fichier unique
        filename = str(uuid.uuid4()) + '.json'
        
        # Chemin d'accès au répertoire de résultats
        results_dir = os.path.join(app.root_path, 'results')
        
        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Chemin d'accès complet au fichier JSON
        results_path = os.path.join(results_dir, filename)
        
        # Écrire les résultats dans un fichier JSON
        with open(results_path, 'w') as f:
            json.dump(results, f)
        
        # Rediriger vers la page de résultats
        return redirect(url_for('show_results'))
    
    return jsonify({'error': 'Invalid file format'})

@app.route('/results')
def show_results():
    # Chemin d'accès au répertoire de résultats
    results_dir = os.path.join(app.root_path, 'results')
    
    # Obtenir la liste des fichiers JSON dans le répertoire
    result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
    
    # Vérifier si des fichiers JSON existent
    if not result_files:
        return jsonify({'error': 'No results found'})
    
    # Lire les résultats depuis chaque fichier JSON
    results = []
    for file in result_files:
        file_path = os.path.join(results_dir, file)
        with open(file_path) as f:
            result_data = json.load(f)
            results.append(result_data)
    
    # Retourner les résultats sous forme de liste de dictionnaires
    return jsonify(results)

if __name__ == '__main__':
    app.run()
