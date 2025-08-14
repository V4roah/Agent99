"""
Agent 99 - Inicialización de Datos
==================================

Script para insertar datos iniciales en la base de datos
Siguiendo el patrón de milla99-backend
"""

from sqlmodel import Session, select
from datetime import datetime
import pytz
from .db import engine

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


def init_customer_profiles():
    """Inicializa perfiles de clientes de ejemplo"""
    try:
        from models import CustomerProfile

        with Session(engine) as session:
            # Verificar si ya existen clientes
            existing_customers = session.exec(select(CustomerProfile)).all()
            if existing_customers:
                print(
                    f"✅ Ya existen {len(existing_customers)} perfiles de clientes")
                return

            # Clientes de ejemplo
            customers = [
                CustomerProfile(
                    name="María González",
                    phone="+57 300 123 4567",
                    preferences={"colores": [
                        "negro", "azul"], "tallas": ["M", "L"]},
                    total_conversations=2
                ),
                CustomerProfile(
                    name="Carlos Rodríguez",
                    phone="+57 310 987 6543",
                    preferences={"colores": [
                        "rojo", "verde"], "tallas": ["S", "XL"]},
                    total_conversations=1
                ),
                CustomerProfile(
                    name="Ana Martínez",
                    phone="+57 315 555 1234",
                    preferences={"colores": [
                        "rosa", "morado"], "tallas": ["XS", "M"]},
                    total_conversations=3
                )
            ]

            for customer in customers:
                session.add(customer)

            session.commit()
            print(f"✅ {len(customers)} perfiles de clientes creados exitosamente")

    except Exception as e:
        print(f"❌ Error creando perfiles de clientes: {e}")


def init_product_inventory():
    """Inicializa inventario de productos de ejemplo"""
    try:
        from models import ProductInventory

        with Session(engine) as session:
            # Verificar si ya existen productos
            existing_products = session.exec(select(ProductInventory)).all()
            if existing_products:
                print(
                    f"✅ Ya existen {len(existing_products)} productos en inventario")
                return

            # Productos de ejemplo
            products = [
                ProductInventory(
                    name="Leggings Negros",
                    description="Leggings deportivos de alta calidad",
                    category="Ropa Deportiva",
                    price=45.99,
                    stock_quantity=25,
                    attributes={"color": "negro",
                                "talla": "M", "material": "lycra"}
                ),
                ProductInventory(
                    name="Camiseta Azul",
                    description="Camiseta deportiva transpirable",
                    category="Ropa Deportiva",
                    price=32.50,
                    stock_quantity=40,
                    attributes={"color": "azul",
                                "talla": "L", "material": "poliéster"}
                ),
                ProductInventory(
                    name="Zapatillas Running",
                    description="Zapatillas para correr con amortiguación",
                    category="Calzado",
                    price=89.99,
                    stock_quantity=15,
                    attributes={"color": "blanco",
                                "talla": "42", "material": "malla"}
                )
            ]

            for product in products:
                session.add(product)

            session.commit()
            print(f"✅ {len(products)} productos creados exitosamente")

    except Exception as e:
        print(f"❌ Error creando productos: {e}")


def init_agent_learnings():
    """Inicializa aprendizajes de agentes de ejemplo"""
    try:
        from models import AgentLearning

        with Session(engine) as session:
            # Verificar si ya existen aprendizajes
            existing_learnings = session.exec(select(AgentLearning)).all()
            if existing_learnings:
                print(
                    f"✅ Ya existen {len(existing_learnings)} aprendizajes de agentes")
                return

            # Aprendizajes de ejemplo
            learnings = [
                AgentLearning(
                    agent_type="sales",
                    learning_type="product_preference",
                    content="Los clientes prefieren leggings negros en talla M",
                    confidence_score=0.85,
                    context={"category": "ropa_deportiva", "color": "negro"}
                ),
                AgentLearning(
                    agent_type="support",
                    learning_type="common_issue",
                    content="Los clientes preguntan frecuentemente sobre tallas",
                    confidence_score=0.90,
                    context={"issue_type": "sizing", "frequency": "high"}
                ),
                AgentLearning(
                    agent_type="complaint",
                    learning_type="resolution_pattern",
                    content="Los reclamos por tallas se resuelven ofreciendo cambio gratuito",
                    confidence_score=0.95,
                    context={"resolution": "free_exchange",
                             "category": "sizing"}
                )
            ]

            for learning in learnings:
                session.add(learning)

            session.commit()
            print(
                f"✅ {len(learnings)} aprendizajes de agentes creados exitosamente")

    except Exception as e:
        print(f"❌ Error creando aprendizajes: {e}")


def init_data():
    """Función principal para inicializar todos los datos"""
    print("🚀 Inicializando datos de ejemplo...")

    try:
        # Crear datos iniciales
        init_customer_profiles()
        init_product_inventory()
        init_agent_learnings()

        print("✅ Todos los datos iniciales creados exitosamente")

    except Exception as e:
        print(f"❌ Error en la inicialización de datos: {e}")
        raise


def get_data_summary():
    """Obtiene un resumen de los datos en la base de datos"""
    try:
        from models import CustomerProfile, ProductInventory, AgentLearning

        with Session(engine) as session:
            customers_count = len(session.exec(select(CustomerProfile)).all())
            products_count = len(session.exec(select(ProductInventory)).all())
            learnings_count = len(session.exec(select(AgentLearning)).all())

            summary = {
                "customers": customers_count,
                "products": products_count,
                "learnings": learnings_count,
                "total": customers_count + products_count + learnings_count
            }

            return summary

    except Exception as e:
        print(f"❌ Error obteniendo resumen: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    init_data()
    summary = get_data_summary()
    print(f"\n📊 Resumen de datos: {summary}")
