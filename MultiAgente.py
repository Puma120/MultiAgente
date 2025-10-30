"""
Sistema Multiagente para Generación de Contenido de Blog
Arquitectura Horizontal (Colaboración entre Pares)
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
from typing import Dict, List, Any

# Cargar variables de entorno
load_dotenv()

class MensajeAgente:
    """Clase para manejar mensajes entre agentes"""
    def __init__(self, remitente: str, destinatario: str, contenido: str, timestamp: datetime = None):
        self.remitente = remitente
        self.destinatario = destinatario
        self.contenido = contenido
        self.timestamp = timestamp or datetime.now()
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.remitente} → {self.destinatario}: {self.contenido[:100]}..."

class SistemaMensajeria:
    """Sistema de mensajería para comunicación entre agentes"""
    def __init__(self):
        self.mensajes: List[MensajeAgente] = []
    
    def enviar_mensaje(self, remitente: str, destinatario: str, contenido: str):
        """Enviar mensaje de un agente a otro"""
        mensaje = MensajeAgente(remitente, destinatario, contenido)
        self.mensajes.append(mensaje)
        print(f"\n{'='*80}")
        print(f"MENSAJE ENVIADO")
        print(f"   De: {remitente}")
        print(f"   Para: {destinatario}")
        print(f"   Hora: {mensaje.timestamp.strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")
        return mensaje
    
    def obtener_ultimo_mensaje(self, destinatario: str) -> MensajeAgente:
        """Obtener el último mensaje para un agente específico"""
        mensajes_para_agente = [m for m in self.mensajes if m.destinatario == destinatario]
        return mensajes_para_agente[-1] if mensajes_para_agente else None

class AgenteInvestigador:
    """
    Agente Investigador (ResearchAgent)
    Rol: Experto en búsqueda de información
    Modelo: gemini-2.5-flash (Rápido y eficiente para investigación)
    """
    def __init__(self, api_key: str, sistema_mensajeria: SistemaMensajeria):
        self.nombre = "Agente Investigador"
        self.rol = "Experto en búsqueda de información"
        self.modelo_nombre = "gemini-2.5-flash"
        self.sistema_mensajeria = sistema_mensajeria
        
        # Configurar Gemini con parámetros de generación
        genai.configure(api_key=api_key)
        self.generation_config = genai.GenerationConfig(
            temperature=0.3,  # Baja temperatura para respuestas más precisas y menos creativas
            top_p=0.8,
            top_k=40
        )
        self.modelo = genai.GenerativeModel(
            model_name=self.modelo_nombre,
            generation_config=self.generation_config
        )
        
        print(f"{self.nombre} inicializado con modelo {self.modelo_nombre}")
    
    def investigar(self, tema: str) -> str:
        """
        Acción: investigar(tema)
        Ejecución: Buscar información relevante sobre el tema
        """
        print(f"\n{self.nombre} está investigando sobre: '{tema}'")
        print(f"   Modelo utilizado: {self.modelo_nombre}")
        
        prompt = f"""
        Eres un experto investigador de tecnología. Tu tarea es investigar y recopilar información relevante 
        sobre el siguiente tema: {tema}
        
        INSTRUCCIONES ESTRICTAS:
        - Proporciona SOLO la información de investigación, sin introducción ni comentarios meta
        - NO escribas frases como "Aquí tienes...", "A continuación...", "He investigado...", etc.
        - Comienza directamente con el contenido de la investigación
        
        Proporciona:
        1. Una descripción clara del tema
        2. Datos y estadísticas importantes (si aplica)
        3. Tendencias actuales relacionadas
        4. Casos de uso o aplicaciones prácticas
        5. Fuentes de información confiables (puedes simular referencias)
        
        La información debe ser precisa, actualizada, objetiva y estructurada para que un redactor pueda 
        crear un artículo de blog profesional.
        """
        
        try:
            response = self.modelo.generate_content(prompt)
            datos_encontrados = response.text
            
            print(f"Investigación completada. {len(datos_encontrados)} caracteres de información recopilados.")
            
            # Enviar mensaje al Agente Redactor
            self.sistema_mensajeria.enviar_mensaje(
                self.nombre,
                "Agente Redactor",
                datos_encontrados
            )
            
            return datos_encontrados
            
        except Exception as e:
            error_msg = f"Error en la investigación: {str(e)}"
            print(f"{error_msg}")
            return error_msg

class AgenteRedactor:
    """
    Agente Redactor (WriterAgent)
    Rol: Experto en redacción creativa y técnica
    Modelo: gemini-2.5-pro (Mejor para tareas creativas y complejas)
    """
    def __init__(self, api_key: str, sistema_mensajeria: SistemaMensajeria):
        self.nombre = "Agente Redactor"
        self.rol = "Experto en redacción creativa y técnica"
        self.modelo_nombre = "gemini-2.5-pro"
        self.sistema_mensajeria = sistema_mensajeria
        
        # Configurar Gemini con parámetros de generación
        genai.configure(api_key=api_key)
        self.generation_config = genai.GenerationConfig(
            temperature=0.5,  # Temperatura moderada para balance entre creatividad y precisión
            top_p=0.85,
            top_k=40
        )
        self.modelo = genai.GenerativeModel(
            model_name=self.modelo_nombre,
            generation_config=self.generation_config
        )
        
        print(f"{self.nombre} inicializado con modelo {self.modelo_nombre}")
    
    def redactar(self) -> str:
        """
        Acción: redactar(datos)
        Ejecución: Crear un borrador de artículo basado en los datos del investigador
        """
        # Obtener datos del Agente Investigador
        mensaje = self.sistema_mensajeria.obtener_ultimo_mensaje(self.nombre)
        
        if not mensaje:
            print(f"{self.nombre}: No hay datos del investigador")
            return ""
        
        datos = mensaje.contenido
        
        print(f"\n{self.nombre} está redactando el artículo...")
        print(f"   Modelo utilizado: {self.modelo_nombre}")
        print(f"   Datos recibidos de: {mensaje.remitente}")
        
        prompt = f"""
        Eres un redactor experto en tecnología. Has recibido la siguiente información de investigación:
        
        {datos}
        
        INSTRUCCIONES ESTRICTAS:
        - Escribe SOLO el artículo, sin introducción meta ni comentarios personales
        - NO escribas frases como "Aquí tienes el artículo...", "He creado...", "A continuación presento...", etc.
        - Comienza directamente con el TÍTULO del artículo
        - Mantén un tono serio, profesional y objetivo
        - Evita lenguaje demasiado casual o expresiones exageradas
        
        Crea un artículo de blog con:
        1. Un título claro y relevante (sin asteriscos ni símbolos especiales)
        2. Una introducción profesional que presente el tema
        3. Desarrollo del contenido en secciones claras con subtítulos
        4. Ejemplos prácticos o casos de uso
        5. Una conclusión que resuma los puntos clave
        6. Tono profesional y técnico, apropiado para un blog empresarial
        
        Extensión: Entre 800-1200 palabras
        Estilo: Blog de tecnología profesional y serio
        
        Escribe el artículo completo ahora:
        """
        
        try:
            response = self.modelo.generate_content(prompt)
            borrador_articulo = response.text
            
            print(f"Borrador completado. {len(borrador_articulo)} caracteres generados.")
            
            # Enviar mensaje al Agente Editor
            self.sistema_mensajeria.enviar_mensaje(
                self.nombre,
                "Agente Editor",
                borrador_articulo
            )
            
            return borrador_articulo
            
        except Exception as e:
            error_msg = f"Error en la redacción: {str(e)}"
            print(f"{error_msg}")
            return error_msg

class AgenteEditor:
    """
    Agente Editor (EditorAgent)
    Rol: Experto en cumplimiento de estilo y gramática
    Modelo: gemini-2.0-flash (Rápido para revisión y edición)
    """
    def __init__(self, api_key: str, sistema_mensajeria: SistemaMensajeria):
        self.nombre = "Agente Editor"
        self.rol = "Experto en cumplimiento de estilo y gramática"
        self.modelo_nombre = "gemini-2.0-flash"
        self.sistema_mensajeria = sistema_mensajeria
        
        # Configurar Gemini con parámetros de generación
        genai.configure(api_key=api_key)
        self.generation_config = genai.GenerationConfig(
            temperature=0.2,  # Temperatura muy baja para edición precisa y conservadora
            top_p=0.75,
            top_k=30
        )
        self.modelo = genai.GenerativeModel(
            model_name=self.modelo_nombre,
            generation_config=self.generation_config
        )
        
        print(f"{self.nombre} inicializado con modelo {self.modelo_nombre}")
    
    def revisar(self) -> str:
        """
        Acción: revisar(borrador)
        Ejecución: Revisar y corregir el borrador del redactor
        """
        # Obtener borrador del Agente Redactor
        mensaje = self.sistema_mensajeria.obtener_ultimo_mensaje(self.nombre)
        
        if not mensaje:
            print(f"❌ {self.nombre}: No hay borrador para revisar")
            return ""
        
        borrador = mensaje.contenido
        
        print(f"\n{self.nombre} está revisando el artículo...")
        print(f"   Modelo utilizado: {self.modelo_nombre}")
        print(f"   Borrador recibido de: {mensaje.remitente}")
        
        prompt = f"""
        Eres un editor profesional experto en contenido tecnológico. Has recibido el siguiente borrador:
        
        {borrador}
        
        INSTRUCCIONES ESTRICTAS:
        - Devuelve SOLO el artículo editado, sin comentarios meta ni introducciones
        - NO escribas frases como "Aquí está el artículo editado...", "He revisado...", "A continuación...", etc.
        - Comienza directamente con el artículo editado
        - Si el borrador contiene introducciones meta, elimínalas completamente
        - Mantén un tono serio, profesional y objetivo
        
        Tu tarea es:
        1. Eliminar cualquier texto meta o introductorio que no sea parte del artículo
        2. Corregir errores ortográficos y gramaticales
        3. Mejorar la coherencia y fluidez del texto
        4. Asegurar que el estilo sea consistente y profesional
        5. Verificar que la estructura sea clara y lógica
        6. Optimizar el título y subtítulos para SEO (sin asteriscos ni símbolos especiales)
        7. Asegurar que el tono sea serio y apropiado para un blog de tecnología profesional
        8. Añadir transiciones naturales si es necesario
        
        IMPORTANTE: Mantén el contenido original, solo mejora la presentación, corrección y elimina comentarios meta.
        
        Devuelve el artículo editado ahora:
        """
        
        try:
            response = self.modelo.generate_content(prompt)
            articulo_final = response.text
            
            print(f"Revisión completada. Artículo final con {len(articulo_final)} caracteres.")
            
            return articulo_final
            
        except Exception as e:
            error_msg = f"Error en la revisión: {str(e)}"
            print(f"{error_msg}")
            return error_msg

class SistemaMultiagente:
    """
    Sistema Multiagente con Arquitectura Horizontal
    Coordina la colaboración entre agentes especializados
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sistema_mensajeria = SistemaMensajeria()
        
        print("\n" + "="*80)
        print("INICIALIZANDO SISTEMA MULTIAGENTE")
        print("   Arquitectura: Horizontal (Colaboración entre Pares)")
        print("="*80 + "\n")
        
        # Inicializar agentes con diferentes modelos de Gemini
        self.agente_investigador = AgenteInvestigador(api_key, self.sistema_mensajeria)
        self.agente_redactor = AgenteRedactor(api_key, self.sistema_mensajeria)
        self.agente_editor = AgenteEditor(api_key, self.sistema_mensajeria)
        
        print("\n" + "="*80)
        print("SISTEMA MULTIAGENTE INICIALIZADO CORRECTAMENTE")
        print("="*80 + "\n")
    
    def generar_articulo(self, tema: str) -> Dict[str, Any]:
        """
        Flujo de trabajo completo para generar un artículo de blog
        """
        print("\n" + "#"*40)
        print(f"INICIANDO FLUJO DE TRABAJO")
        print(f"   Tema: {tema}")
        print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#"*40 + "\n")

        resultados = {
            'tema': tema,
            'investigacion': '',
            'borrador': '',
            'articulo_final': '',
            'timestamp': datetime.now()
        }
        
        try:
            # FASE 1: Investigación
            print("\n" + "─"*80)
            print("<>FASE 1: INVESTIGACIÓN")
            print("─"*80)
            resultados['investigacion'] = self.agente_investigador.investigar(tema)
            
            # FASE 2: Redacción
            print("\n" + "─"*80)
            print("<>FASE 2: REDACCIÓN")
            print("─"*80)
            resultados['borrador'] = self.agente_redactor.redactar()
            
            # FASE 3: Edición
            print("\n" + "─"*80)
            print("<>FASE 3: EDICIÓN Y REVISIÓN")
            print("─"*80)
            resultados['articulo_final'] = self.agente_editor.revisar()
            
            # TAREA COMPLETADA
            print("\n" + "#"*40)
            print("¡TAREA COMPLETADA! Artículo Finalizado.")
            print("#"*40 + "\n")

            return resultados
            
        except Exception as e:
            print(f"\nERROR EN EL FLUJO DE TRABAJO: {str(e)}")
            return resultados
    
    def guardar_articulo(self, resultados: Dict[str, Any], nombre_archivo: str = None):
        """Guardar el artículo final en un archivo"""
        if not nombre_archivo:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"articulo_{timestamp}.txt"
        
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("ARTÍCULO GENERADO POR SISTEMA MULTIAGENTE\n")
                f.write("="*80 + "\n\n")
                f.write(f"Tema: {resultados['tema']}\n")
                f.write(f"Fecha: {resultados['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(resultados['articulo_final'])

            print(f"Artículo guardado en: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al guardar el artículo: {str(e)}")
            return None

def main():
    """Función principal"""
    # Cargar API Key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: No se encontró GEMINI_API_KEY en el archivo .env")
        return
    
    # Crear sistema multiagente
    sistema = SistemaMultiagente(api_key)
    
    # Definir tema del artículo
    tema = "Inteligencia Artificial y Machine Learning en 2025: Tendencias y Aplicaciones"
    
    # Generar artículo
    resultados = sistema.generar_articulo(tema)
    
    # Guardar artículo
    if resultados['articulo_final']:
        sistema.guardar_articulo(resultados)
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DEL PROCESO")
    print("="*80)
    print(f"Tema: {resultados['tema']}")
    print(f"Investigación: {len(resultados['investigacion'])} caracteres")
    print(f"Borrador: {len(resultados['borrador'])} caracteres")
    print(f"Artículo Final: {len(resultados['articulo_final'])} caracteres")
    print(f"Mensajes intercambiados: {len(sistema.sistema_mensajeria.mensajes)}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
