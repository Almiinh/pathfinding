/**
 * Auteur: Minh-Hoang HUYNH
 */

package org.jsonconverter;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.*;
import java.nio.file.Paths;

/**
 * Convertit les fichiers trajectoire JSON à KML
 * */
public class JSONConverter {
    public static void main(String[] args) {
        // Lecture d'entrée du chemin vers le fichier JSON stocké dans inputPath
        System.out.println(
                "\n===============================================\n" +
                "Convertisseur de fichier trajectoire JSON à KML\n" +
                "===============================================\n");
        String inputPath = readInput();

        try {
            // Lecture du fichier JSON : jsonData stocke toutes les lignes sous la forme de String
            StringBuilder jsonData = new StringBuilder();
            BufferedReader reader = new BufferedReader(new FileReader(inputPath));
            String line;
            while ((line = reader.readLine()) != null)          // Lit le fichier jusqu'à la fin
                jsonData.append(line);                          // Stocke les ligne dans jsonData
            reader.close();

            // Écriture en fichier KML
            String outputPath = inputPath.replace("json", "kml");
            writeOutput(outputPath, jsonData);
            System.out.println("Le fichier trajectoire a été converti en fichier KML et sauvegardé ici : \n" +
                    Paths.get(outputPath).toRealPath().toString());

        } catch (IOException | JSONException e ) {
            System.out.println("Erreur: Impossible de lire le fichier");
            e.printStackTrace();
        }
    }
    /**
     * Lis l'entrée dans le terminal. Réessaie jusqu'à avoir un fichier bon.
     * Retourne le chemin vers le fichier.
     */
    private static String readInput() {
        BufferedReader cmdReader = new BufferedReader(new InputStreamReader(System.in));
        String input = "";
        while (input.isEmpty() || !input.endsWith(".json") || !new File(input).isFile()) try {
            System.out.println("Entrer le chemin du fichier JSON : \n");
            System.out.flush();
            input = cmdReader.readLine().replaceAll("^\"|\"$", "");
        } catch (IOException e) {
            System.out.println("Fichier invalide. Veuillez réessayer.");
        }
        return input;
    }

    /**
     * Écrit dans le fichier trajectoire KML sortant
     */
    private static void writeOutput(String outputPath, StringBuilder jsonData) throws IOException, JSONException {
        // Writing kml header
        FileWriter writer = null;

        writer = new FileWriter(outputPath);
        writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        writer.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n");
        writer.write("    <Document>\n");
        writer.write("        <name>"+ Paths.get(outputPath).getFileName().toString() +"</name>\n");

        // Writing points
        JSONArray jsonArray = new JSONArray(jsonData.toString());
        JSONObject point;
        for (int i = 0; i < jsonArray.length(); i++) {
            point = jsonArray.getJSONObject(i);
            String kmlPoint = "        <Placemark>\n" +
                    "            <name>" + point.getInt("id") + "</name>\n" +
                    "            <ExtendedData>\n" +
                    "                <Data name=\"origin\">\n" +
                    "                    <value>" + point.getInt("origin") + "</value>\n" +
                    "                </Data>\n" +
                    "                <Data name=\"id\">\n" +
                    "                    <value>" + point.getInt("id") + "</value>\n" +
                    "                </Data>\n" +
                    "                <Data name=\"confiance\">\n" +
                    "                    <value>" + point.getDouble("confiance")+"</value>\n" +
                    "                </Data>\n" +
                    "            </ExtendedData>\n"+
                    "            <Point>\n" +
                    "                <coordinates>" + point.getDouble("lng") + "," + point.getDouble("lat") + ",0.0</coordinates>\n" +
                    "            </Point>\n" +
                    "        </Placemark>\n";
            writer.write(kmlPoint);
        }
        writer.write("    </Document>\n");
        writer.write("</kml>\n");
        writer.close();
    }
}
