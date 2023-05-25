import os
import json             
import simplekml        # pip install simplekml

# Chargement des données JSON depuis le fichier
print('===============================================')
print('Convertisseur de fichier trajectoire JSON à KML')
print('===============================================')
print('Entrer le chemin du fichier JSON : ')
while not os.path.isfile(input_path := input('> ').strip('"')):
    print('Fichier invalide. Veuillez réessayer.')
output_path = input_path.replace('json','kml')

# Sauvgarde des données JSON dans la variable str 'data'
with open(input_path, 'r') as f:
    data = json.load(f)

# Créer un document KML
kml = simplekml.Kml()
kml.document.name = (output_path.split('\\')[-1])

for feature in data :
    # Extraction des propriétés 
    id = feature['id']
    lng = feature['lng']
    lat = feature['lat']
    origin = feature['origin']
    confiance = feature['confiance']
    
    # Création d'un Placemark pour chaque point et ajout des propriétés
    placemark = kml.newpoint(name=str(id), coords=[(lng, lat),])
    placemark.extendeddata.newdata('origin', str(origin))
    placemark.extendeddata.newdata('id', str(id))
    placemark.extendeddata.newdata('confiance', str(confiance))
    
# Sauvegarde du fichier KML
kml.save(output_path)
print("Le fichier trajectoire a été converti en fichier KML et sauvegardé ici : ")
print("> "+output_path)
