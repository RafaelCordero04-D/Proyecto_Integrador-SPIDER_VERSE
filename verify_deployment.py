"""
Script de verificación pre-despliegue para Render
Verifica que todos los archivos y configuraciones necesarias estén presentes
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Verifica si un archivo existe"""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "REQUERIDO" if required else "OPCIONAL"
    print(f"{status} {filepath} ({req_text})")
    return exists

def check_env_vars():
    """Verifica variables de entorno en .env"""
    print("\n📋 Verificando variables de entorno en .env:")
    
    required_vars = [
        "POSTGRESQL_ADDON_USER",
        "POSTGRESQL_ADDON_PASSWORD",
        "POSTGRESQL_ADDON_HOST",
        "POSTGRESQL_ADDON_PORT",
        "POSTGRESQL_ADDON_DB"
    ]
    
    optional_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    if not Path(".env").exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    try:
        with open(".env", "r", encoding="utf-8") as f:
            env_content = f.read()
    except UnicodeDecodeError:
        try:
            with open(".env", "r", encoding="utf-16") as f:
                env_content = f.read()
        except:
            with open(".env", "r", encoding="latin-1") as f:
                env_content = f.read()
    
    all_found = True
    for var in required_vars:
        if var in env_content:
            print(f"✅ {var} (REQUERIDO)")
        else:
            print(f"❌ {var} (REQUERIDO) - FALTANTE")
            all_found = False
    
    for var in optional_vars:
        if var in env_content:
            print(f"✅ {var} (OPCIONAL)")
        else:
            print(f"⚠️ {var} (OPCIONAL) - No encontrado")
    
    return all_found

def check_requirements():
    """Verifica que requirements.txt tenga las dependencias necesarias"""
    print("\n📦 Verificando requirements.txt:")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlmodel",
        "asyncpg",
        "python-dotenv",
        "python-multipart",
        "jinja2"
    ]
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt no encontrado")
        return False
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            requirements = f.read().lower()
    except UnicodeDecodeError:
        try:
            with open("requirements.txt", "r", encoding="utf-16") as f:
                requirements = f.read().lower()
        except:
            with open("requirements.txt", "r", encoding="latin-1") as f:
                requirements = f.read().lower()
    
    all_found = True
    for package in required_packages:
        if package in requirements:
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - FALTANTE")
            all_found = False
    
    return all_found

def check_render_config():
    """Verifica la configuración de render.yaml"""
    print("\n⚙️ Verificando render.yaml:")
    
    if not Path("render.yaml").exists():
        print("❌ render.yaml no encontrado")
        return False
    
    with open("render.yaml", "r", encoding="utf-8") as f:
        config = f.read()
    
    checks = [
        ("type: web", "Tipo de servicio"),
        ("env: python", "Entorno Python"),
        ("uvicorn main:app", "Comando de inicio"),
        ("pip install -r requirements.txt", "Comando de build")
    ]
    
    all_found = True
    for check, description in checks:
        if check in config:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - FALTANTE")
            all_found = False
    
    return all_found

def main():
    """Función principal"""
    print("🚀 Verificación Pre-Despliegue para Render\n")
    print("=" * 60)
    
    # Verificar archivos requeridos
    print("\n📁 Verificando archivos del proyecto:")
    files_ok = all([
        check_file_exists("main.py", required=True),
        check_file_exists("db.py", required=True),
        check_file_exists("models.py", required=True),
        check_file_exists("requirements.txt", required=True),
        check_file_exists("render.yaml", required=True),
        check_file_exists(".gitignore", required=True),
        check_file_exists("Procfile", required=False),
    ])
    
    # Verificar variables de entorno
    env_ok = check_env_vars()
    
    # Verificar requirements.txt
    req_ok = check_requirements()
    
    # Verificar render.yaml
    render_ok = check_render_config()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("\n📊 RESUMEN:")
    print(f"{'✅' if files_ok else '❌'} Archivos del proyecto")
    print(f"{'✅' if env_ok else '❌'} Variables de entorno")
    print(f"{'✅' if req_ok else '❌'} Dependencias (requirements.txt)")
    print(f"{'✅' if render_ok else '❌'} Configuración de Render")
    
    if all([files_ok, env_ok, req_ok, render_ok]):
        print("\n✅ ¡Todo listo para desplegar en Render!")
        print("\n📝 Próximos pasos:")
        print("1. Asegúrate de que tu código esté en un repositorio Git")
        print("2. Ve a https://dashboard.render.com/")
        print("3. Crea un nuevo Web Service")
        print("4. Conecta tu repositorio")
        print("5. Configura las variables de entorno en Render")
        print("6. ¡Despliega!")
        return 0
    else:
        print("\n❌ Hay problemas que resolver antes de desplegar")
        print("\n📝 Revisa los errores marcados con ❌ arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
