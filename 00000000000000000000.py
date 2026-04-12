import os
import shutil
import ollama
import json
import zipfile

# --- CONFIGURACIÓN ---
# Directorio que quieres organizar (Ejemplo: tu Home)
ORIGEN = os.path.expanduser("~") 
# Carpeta donde se moverá todo lo clasificado
DESTINO_MAESTRO = os.path.join(ORIGEN, "MI_LAPTOP_ORGANIZADA")
MODELO = "gemma4" # O gemma:2b / llama3.2 según lo que tengas en 'ollama list'

# Carpetas que la IA NO debe tocar para no romper el sistema
IGNORAR = {'.cache', '.local', '.config', '.ssh', '.git', 'node_modules', 'MI_LAPTOP_ORGANIZADA', 'snap'}

def obtener_contexto(ruta):
    """Extrae pistas del interior del archivo para Gemma 4"""
    ext = os.path.splitext(ruta)[1].lower()
    try:
        if ext in ['.json', '.txt', '.py', '.js', '.sh', '.yml', '.sql']:
            with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                return f"Contenido: {f.read(400)}"
        elif ext == '.zip':
            with zipfile.ZipFile(ruta, 'r') as z:
                return f"Contenido del ZIP: {z.namelist()[:10]}"
    except:
        return "Archivo binario o sin acceso."
    return "Sin contexto extra."

def clasificar_con_gemma(nombre, ruta_full):
    """Gemma 4 decide el proyecto y un nombre mejor"""
    contexto = obtener_contexto(ruta_full)
    
    prompt = f"""
    Analiza este archivo:
    Nombre: {nombre}
    Contexto: {contexto}

    Instrucciones:
    1. Determina a qué PROYECTO o CATEGORÍA pertenece (ej: Web_Ventas, Scripts_Python, Finanzas, Fotos_Viaje).
    2. Si el nombre es genérico (ej: 'data.json'), crea un NUEVO_NOMBRE descriptivo.
    
    Responde estrictamente en formato JSON:
    {{"proyecto": "Nombre_Proyecto", "nuevo_nombre": "nombre_mejorado.ext"}}
    """
    
    try:
        response = ollama.generate(model=MODELO, prompt=prompt, format="json")
        return json.loads(response['response'])
    except:
        return {"proyecto": "Otros", "nuevo_nombre": nombre}

# --- PROCESO PRINCIPAL ---
if not os.path.exists(DESTINO_MAESTRO):
    os.makedirs(DESTINO_MAESTRO)

print(f"🚀 Gemma 4 iniciando organización total en: {ORIGEN}...")

for raiz, dirs, archivos in os.walk(ORIGEN):
    # Evitar carpetas críticas y ocultas
    dirs[:] = [d for d in dirs if d not in IGNORAR and not d.startswith('.')]
    
    for archivo in archivos:
        if archivo.startswith('.'): continue # Saltar archivos ocultos
        
        ruta_actual = os.path.join(raiz, archivo)
        
        # 1. La IA analiza
        resultado = clasificar_con_gemma(archivo, ruta_actual)
        proyecto = resultado.get("proyecto", "Otros").replace(" ", "_")
        nuevo_nombre = resultado.get("nuevo_nombre", archivo)
        
        # 2. Crear carpeta del proyecto
        ruta_proyecto = os.path.join(DESTINO_MAESTRO, proyecto)
        os.makedirs(ruta_proyecto, exist_ok=True)
        
        # 3. Mover y Renombrar
        try:
            destino_final = os.path.join(ruta_proyecto, nuevo_nombre)
            # Si el archivo ya existe, añade un prefijo para no sobrescribir
            if os.path.exists(destino_final):
                destino_final = os.path.join(ruta_proyecto, f"copia_{archivo}")
                
            shutil.move(ruta_actual, destino_final)
            print(f"✅ [{proyecto}] -> {nuevo_nombre}")
        except Exception as e:
            print(f"❌ Error con {archivo}: {e}")

print(f"\n✨ ¡Hecho! Revisa la carpeta: {DESTINO_MAESTRO}")
