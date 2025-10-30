"""
Script de Demostración del Sistema Multiagente
Versión rápida con tema personalizable
"""

from MultiAgente import SistemaMultiagente
import os
from dotenv import load_dotenv

def main():
    # Cargar variables de entorno
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: Configure GEMINI_API_KEY en el archivo .env")
        return
    
    print("\n" + "="*80)
    print("  SISTEMA MULTIAGENTE - DEMOSTRACIÓN")
    print("  Generación Automática de Contenido para Blog")
    print("="*80 + "\n")
    
    # Temas disponibles para demostración
    temas_disponibles = [
        "Inteligencia Artificial y Machine Learning en 2025: Tendencias y Aplicaciones",
        "Blockchain y Web3: El Futuro de Internet Descentralizado",
        "Computación Cuántica: La Próxima Revolución Tecnológica",
        "Ciberseguridad en la Era Digital: Desafíos y Soluciones",
        "Internet de las Cosas (IoT): Conectando el Mundo Real"
    ]
    
    print("Temas Sugeridos:")
    for i, tema in enumerate(temas_disponibles, 1):
        print(f"   {i}. {tema}")
    
    print("\n" + "─"*80)
    
    # Solicitar tema al usuario
    print("\nOpciones:")
    print("   - Ingrese un número (1-5) para seleccionar un tema sugerido")
    print("   - O escriba su propio tema personalizado")
    print()
    
    entrada_usuario = input("Su elección: ").strip()
    
    # Determinar el tema seleccionado
    if entrada_usuario.isdigit():
        indice = int(entrada_usuario)
        if 1 <= indice <= len(temas_disponibles):
            tema_seleccionado = temas_disponibles[indice - 1]
        else:
            print(f"\nNúmero inválido. Usando tema por defecto.")
            tema_seleccionado = temas_disponibles[0]
    elif entrada_usuario:
        tema_seleccionado = entrada_usuario
    else:
        print(f"\nNo se ingresó tema. Usando tema por defecto.")
        tema_seleccionado = temas_disponibles[0]
    
    print(f"\nTema seleccionado: {tema_seleccionado}\n")
    
    # Crear sistema y generar artículo
    sistema = SistemaMultiagente(api_key)
    resultados = sistema.generar_articulo(tema_seleccionado)
    
    # Guardar artículo
    if resultados['articulo_final']:
        archivo = sistema.guardar_articulo(resultados)
        print(f"\nProceso completado exitosamente!")
        print(f"Revisa el archivo: {archivo}")
    else:
        print("\nNo se pudo completar el proceso")

if __name__ == "__main__":
    main()
