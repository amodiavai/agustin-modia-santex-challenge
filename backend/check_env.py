#!/usr/bin/env python3
"""
Script para verificar que todas las variables de entorno necesarias estén configuradas
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variables requeridas
REQUIRED_VARS = {
    'OPENAI_API_KEY': 'API Key de OpenAI (sk-proj-...)',
    'ADMIN_USER': 'Usuario administrador',
    'ADMIN_PASSWORD': 'Contraseña administrador',
    'SECRET_KEY': 'Clave secreta para JWT (mínimo 32 caracteres)',
}

# Variables opcionales pero recomendadas
OPTIONAL_VARS = {
    'QDRANT_URL': 'URL de Qdrant Cloud (https://...)',
    'QDRANT_API_KEY': 'API Key de Qdrant Cloud',
    'QDRANT_HOST': 'Host de Qdrant (para Docker)',
    'QDRANT_PORT': 'Puerto de Qdrant (para Docker)',
    'OPENAI_MODEL': 'Modelo de OpenAI a usar',
    'COLLECTION_NAME': 'Nombre de la colección en Qdrant',
    'ACCESS_TOKEN_EXPIRE_MINUTES': 'Minutos de expiración del token',
}

def check_environment():
    """Verifica las variables de entorno"""
    print("🔍 Verificando configuración de variables de entorno...\n")
    
    missing_required = []
    warnings = []
    
    # Verificar variables requeridas
    print("✅ Variables Requeridas:")
    for var, description in REQUIRED_VARS.items():
        value = os.getenv(var)
        if not value:
            missing_required.append(var)
            print(f"❌ {var}: NO CONFIGURADA - {description}")
        else:
            # Validaciones específicas
            if var == 'SECRET_KEY' and len(value) < 32:
                warnings.append(f"⚠️  SECRET_KEY es muy corta (debe tener al menos 32 caracteres)")
                print(f"⚠️  {var}: CONFIGURADA pero muy corta - {description}")
            elif var == 'OPENAI_API_KEY' and not value.startswith('sk-'):
                warnings.append(f"⚠️  OPENAI_API_KEY no parece válida (debe empezar con 'sk-')")
                print(f"⚠️  {var}: CONFIGURADA pero formato inválido - {description}")
            else:
                print(f"✅ {var}: CONFIGURADA - {description}")
    
    print()
    
    # Verificar variables opcionales
    print("📋 Variables Opcionales:")
    qdrant_config_type = None
    
    for var, description in OPTIONAL_VARS.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: CONFIGURADA - {description}")
            if var == 'QDRANT_URL':
                qdrant_config_type = 'cloud'
            elif var in ['QDRANT_HOST', 'QDRANT_PORT'] and not qdrant_config_type:
                qdrant_config_type = 'docker'
        else:
            print(f"⚪ {var}: NO CONFIGURADA - {description}")
    
    print()
    
    # Verificar configuración de Qdrant
    print("🗄️  Configuración de Qdrant:")
    if qdrant_config_type == 'cloud':
        if os.getenv('QDRANT_API_KEY'):
            print("✅ Configuración Qdrant Cloud completa")
        else:
            warnings.append("⚠️  QDRANT_URL configurada pero falta QDRANT_API_KEY")
            print("⚠️  QDRANT_URL configurada pero falta QDRANT_API_KEY")
    elif qdrant_config_type == 'docker':
        print("✅ Configuración Qdrant Docker local")
    else:
        warnings.append("⚠️  No hay configuración de Qdrant (se usará localhost:6333)")
        print("⚠️  No hay configuración de Qdrant (se usará localhost:6333)")
    
    print()
    
    # Resumen
    if missing_required:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("Variables requeridas faltantes:")
        for var in missing_required:
            print(f"  - {var}")
        print("\nEl sistema NO puede funcionar sin estas variables.")
        return False
    
    if warnings:
        print("⚠️  CONFIGURACIÓN CON ADVERTENCIAS")
        for warning in warnings:
            print(f"  {warning}")
        print("\nEl sistema puede funcionar pero se recomienda revisar estas configuraciones.")
    else:
        print("✅ CONFIGURACIÓN COMPLETA")
        print("Todas las variables están configuradas correctamente.")
    
    return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)