#!/usr/bin/env python3
"""
Script para ejecutar la aplicación facial-landmarks-app
"""
import os
import sys
import subprocess

def main():
    # Configurar entorno
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

    # Ejecutar streamlit
    try:
        import streamlit.web.cli as st_cli
        sys.argv = ['streamlit', 'run', 'app.py', '--server.port', '8505']
        st_cli.main()
    except Exception as e:
        print(f"Error al ejecutar Streamlit: {e}")
        input("Presiona Enter para continuar...")

if __name__ == "__main__":
    main()