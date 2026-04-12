python
import os
import shutil
import ollama

# --- CONFIGURACIÓN ---
CARPETA_ORIGEN = "./proyectos_desordenados" # La carpeta con tus .zip, .json, etc.
DESTINO_BASE = "./proyectos_ordenados"      # Donde se crearán las carpetas de proyecto
MODELO = "llama3.2"

def analizar_con_llama(nombre, contenido_previo):
    prompt = f"""
    Eres un experto en gestión de proyectos de software. 
    Analiza este archivo:
    Nombre: {nombre}
    Primeras líneas/contexto: {contenido_previo[:300]}
    
    ¿A qué categoría de proyecto pertenece? (Ejemplos: Frontend, Backend, Datos, Configuración, Documentación).
    Responde SOLO con UNA PALABRA que sea el nombre de la categoría.
    """
    
    response = ollama.generate(model=MODELO, prompt=prompt)
    return response['response'].strip().replace(".", "").split()[0]

# --- EJECUCIÓN ---
if not os.path.exists(DESTINO_BASE): os.makedirs(DESTINO_BASE)

for archivo in os.listdir(CARPETA_ORIGEN):
    ruta_full = os.path.join(CARPETA_ORIGEN, archivo)
    
    if os.path.isfile(ruta_full):
        print(f"🧐 Analizando: {archivo}...")
        
        # Leer un poco del archivo para dar contexto a la IA (si es texto)
        contexto = ""
        if archivo.endswith(('.json', '.txt', '.js', '.py')):
            try:
                with open(ruta_full, 'r') as f: contexto = f.read(500)
            except: contexto = "Archivo binario o no legible"

        # Preguntar a Llama 3.2
        categoria = analizar_con_llama(archivo, contexto)
        
        # Mover archivo
        ruta_destino = os.path.join(DESTINO_BASE, categoria)
        os.makedirs(ruta_destino, exist_ok=True)
        shutil.move(ruta_full, os.path.join(ruta_destino, archivo))
        print(f"✅ Movido a: {categoria}/")

print("\n🚀 ¡Organización completada!")