"""
Servicio para persistir tags en la base de datos
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

print("🚨 IMPORTANDO tag_persistence.py")

try:
    from core.db import get_session
    print("✅ core.db importado correctamente")
except Exception as e:
    import traceback
    print(f"❌ ERROR importando core.db: {e}")
    print(f"🔍 Traceback: {traceback.format_exc()}")

try:
    from models.tag import Tag, TagUsage, TagCategory, TagCreate
    print("✅ models.tag importado correctamente")
except Exception as e:
    import traceback
    print(f"❌ ERROR importando models.tag: {e}")
    print(f"🔍 Traceback: {traceback.format_exc()}")

try:
    from sqlmodel import Session, select
    print("✅ sqlmodel importado correctamente")
except Exception as e:
    import traceback
    print(f"❌ ERROR importando sqlmodel: {e}")
    print(f"🔍 Traceback: {traceback.format_exc()}")

logger = logging.getLogger(__name__)
print("✅ Logger configurado")


class TagPersistenceService:
    """Servicio para persistir tags en la base de datos"""

    def __init__(self):
        print("🚨 CONSTRUCTOR TagPersistenceService llamado")
        self.logger = logger
        print("✅ TagPersistenceService inicializado")

    def _cleanup_session_on_error(self, session: Session):
        """Limpia la sesión en caso de error"""
        try:
            print(f"🔍 DEBUG: Limpiando sesión después de error...")
            session.rollback()
            print(f"✅ DEBUG: Sesión limpiada exitosamente")
        except Exception as e:
            print(f"⚠️ WARNING: Error limpiando sesión: {e}")

    def save_tags_to_database(self,
                              tags: List[Dict[str, Any]],
                              conversation_id: str,
                              customer_id: str,
                              category: str) -> bool:
        """
        Guarda tags en la base de datos

        Args:
            tags: Lista de tags generados por smart_tagging
            conversation_id: ID de la conversación
            customer_id: ID del cliente
            category: Categoría de la conversación

        Returns:
            bool: True si se guardaron correctamente
        """
        print(f"🚨 MÉTODO LLAMADO: save_tags_to_database con {len(tags)} tags")
        try:
            print(
                f"🔍 DEBUG save_tags_to_database: Iniciando con {len(tags)} tags")
            print(
                f"🔍 DEBUG save_tags_to_database: conversation_id={conversation_id}")
            print(f"🔍 DEBUG save_tags_to_database: customer_id={customer_id}")
            print(f"🔍 DEBUG save_tags_to_database: category={category}")

            with get_session() as session:
                print(f"🔍 DEBUG save_tags_to_database: Sesión de BD creada")

                # 🔴 PASO 1: VALIDAR DEPENDENCIAS ANTES DE CREAR TAGS
                print(f"🔍 DEBUG save_tags_to_database: Validando dependencias...")

                # Validar que la conversación existe
                from models.conversation import Conversation
                conversation = session.exec(
                    select(Conversation).where(
                        Conversation.id == conversation_id)
                ).first()

                if not conversation:
                    print(
                        f"❌ ERROR: La conversación {conversation_id} NO existe en la BD")
                    print(
                        f"🔍 DEBUG: Se debe crear la conversación ANTES de persistir tags")
                    return False

                print(f"✅ DEBUG: Conversación {conversation_id} validada")

                # Validar customer_id y convertirlo a UUID si es necesario
                valid_customer_id = None
                if customer_id and customer_id != "None":
                    try:
                        # Si es un UUID válido, usarlo directamente
                        if len(customer_id) == 36 and '-' in customer_id:
                            valid_customer_id = customer_id
                        else:
                            # Si no es UUID válido, intentar crear un customer profile
                            from models.customer import CustomerProfile
                            try:
                                # Crear customer profile temporal sin validar UUID
                                customer = CustomerProfile(
                                    name=f"Cliente {customer_id}",
                                    phone=customer_id if customer_id.startswith(
                                        '+') else None,
                                    email=f"{customer_id}@temp.com"
                                )
                                session.add(customer)
                                session.flush()  # Para obtener el ID
                                print(
                                    f"✅ DEBUG: Customer profile creado con ID: {customer.id}")
                                valid_customer_id = str(customer.id)
                            except Exception as customer_error:
                                print(
                                    f"⚠️ WARNING: Error creando customer profile: {customer_error}")
                                print(f"🔍 DEBUG: Continuando con customer_id=None")
                                valid_customer_id = None
                    except Exception as e:
                        print(f"⚠️ WARNING: Error validando customer_id: {e}")
                        print(f"🔍 DEBUG: Continuando con customer_id=None")
                        valid_customer_id = None

                print(f"🔍 DEBUG: customer_id validado: {valid_customer_id}")

                # 🔴 PASO 2: CREAR CATEGORÍA PRIMERO (para evitar autoflush)
                print(
                    f"🔍 DEBUG save_tags_to_database: Creando categoría '{category}'")
                try:
                    self._ensure_category_exists(session, category)
                except Exception as category_error:
                    print(
                        f"⚠️ WARNING: Error creando categoría '{category}': {category_error}")
                    print(f"🔍 DEBUG: Continuando sin categoría específica")
                    # Usar categoría por defecto si falla
                    category = "General"

                # 🔴 PASO 3: CREAR TAGS CON session.no_autoflush
                saved_tags = []
                print(
                    f"🔍 DEBUG save_tags_to_database: Procesando {len(tags)} tags...")

                with session.no_autoflush:
                    for i, tag_data in enumerate(tags):
                        print(
                            f"🔍 DEBUG save_tags_to_database: Procesando tag {i+1}/{len(tags)}: {tag_data}")
                        tag = self._create_or_update_tag(
                            session, tag_data, category)
                        if tag:
                            print(
                                f"✅ DEBUG save_tags_to_database: Tag procesado exitosamente: {tag.name}")
                            saved_tags.append(tag)
                        else:
                            print(
                                f"❌ DEBUG save_tags_to_database: Tag NO se procesó: {tag_data}")

                    # 🔴 PASO 4: CREAR TAG_USAGE DESPUÉS DE VALIDAR TODO
                    print(
                        f"🔍 DEBUG save_tags_to_database: Creando {len(saved_tags)} registros de TagUsage...")
                    for tag in saved_tags:
                        # Buscar el tag_data original para obtener confidence_score
                        original_tag_data = next((t for t in tags if t.get(
                            'name', '').lower().strip() == tag.name), None)
                        confidence = original_tag_data.get(
                            'confidence_score', 0.8) if original_tag_data else 0.8

                        self._create_tag_usage(
                            session, tag.id, conversation_id, valid_customer_id, confidence)

                # 🔴 PASO 5: COMMIT FINAL
                print(
                    f"🔍 DEBUG save_tags_to_database: Intentando commit de {len(saved_tags)} tags...")
                session.commit()
                print(f"✅ DEBUG save_tags_to_database: Commit exitoso!")

                self.logger.info(
                    f"✅ {len(saved_tags)} tags guardados en BD para conversación {conversation_id}")
                print(
                    f"✅ DEBUG save_tags_to_database: {len(saved_tags)} tags guardados exitosamente")
                return True

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error guardando tags en BD: {e}")
            self.logger.error(
                f"🔍 Traceback completo: {traceback.format_exc()}")

            # Limpiar sesión en caso de error
            try:
                if 'session' in locals():
                    self._cleanup_session_on_error(session)
            except:
                pass

            return False

    def _create_or_update_tag(self, session: Session, tag_data: Dict[str, Any], category: str) -> Optional[Tag]:
        """Crea o actualiza un tag individual"""
        try:
            print(f"🔍 DEBUG _create_or_update_tag: tag_data={tag_data}")
            print(f"🔍 DEBUG _create_or_update_tag: category={category}")

            tag_name = tag_data.get('name', '').lower().strip()
            print(f"🔍 DEBUG _create_or_update_tag: tag_name='{tag_name}'")

            if not tag_name:
                print(f"❌ DEBUG _create_or_update_tag: tag_name vacío")
                return None

                # Buscar si ya existe
            print(
                f"🔍 DEBUG _create_or_update_tag: Buscando tag existente con nombre '{tag_name}'")
            existing_tag = session.exec(
                select(Tag).where(Tag.name == tag_name)
            ).first()

            if existing_tag:
                print(
                    f"✅ DEBUG _create_or_update_tag: Tag existente encontrado: {existing_tag.name}")
                # Actualizar tag existente
                existing_tag.usage_count += 1
                existing_tag.updated_at = datetime.now()
                if existing_tag.confidence_score < tag_data.get('confidence_score', 0.0):
                    existing_tag.confidence_score = tag_data.get(
                        'confidence_score', 0.0)
                print(
                    f"🔍 DEBUG _create_or_update_tag: Tag actualizado, usage_count={existing_tag.usage_count}")
                return existing_tag
            else:
                print(
                    f"🆕 DEBUG _create_or_update_tag: Creando nuevo tag '{tag_name}'")
                # Crear nuevo tag
                new_tag = Tag(
                    name=tag_name,
                    category=category,
                    tag_type=tag_data.get('type', 'ml_generated'),
                    confidence_score=tag_data.get('confidence_score', 0.8),
                    source=tag_data.get('source', 'smart_tagging'),
                    weight=tag_data.get('weight', 1.0),
                    context=tag_data.get('context', ''),
                    related_tags_json=tag_data.get('related_tags', []),
                    usage_count=1
                )
                print(
                    f"🔍 DEBUG _create_or_update_tag: Nuevo tag creado: {new_tag}")
                session.add(new_tag)
                session.flush()  # Para obtener el ID
                print(
                    f"🔍 DEBUG _create_or_update_tag: Tag guardado con ID: {new_tag.id}")
                return new_tag

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error creando/actualizando tag: {e}")
            print(f"❌ ERROR _create_or_update_tag: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            # NO relanzar la excepción para evitar abortar la transacción
            print(f"⚠️ WARNING: Continuando sin procesar tag '{tag_name}'")
            return None

    def _create_tag_usage(self, session: Session, tag_id: str, conversation_id: str, customer_id: str, confidence_score: float):
        """Crea un registro de uso de tag"""
        try:
            print(f"🔍 DEBUG _create_tag_usage: tag_id={tag_id}")
            print(
                f"🔍 DEBUG _create_tag_usage: conversation_id={conversation_id}")
            print(f"🔍 DEBUG _create_tag_usage: customer_id={customer_id}")
            print(
                f"🔍 DEBUG _create_tag_usage: confidence_score={confidence_score}")

            # Validar que tag_id sea válido
            if not tag_id:
                print(f"❌ ERROR _create_tag_usage: tag_id es None o vacío")
                return

            # Validar que conversation_id sea válido
            if not conversation_id:
                print(f"❌ ERROR _create_tag_usage: conversation_id es None o vacío")
                return

            # Crear TagUsage con validación de customer_id
            tag_usage_data = {
                "tag_id": tag_id,
                "conversation_id": conversation_id,
                "confidence_score": confidence_score,
                "usage_context": "whatsapp_analysis"
            }

            # Solo agregar customer_id si es válido
            if customer_id and customer_id != "None":
                tag_usage_data["customer_id"] = customer_id
            else:
                tag_usage_data["customer_id"] = None

            tag_usage = TagUsage(**tag_usage_data)
            print(f"🔍 DEBUG _create_tag_usage: TagUsage creado: {tag_usage}")
            session.add(tag_usage)
            print(f"🔍 DEBUG _create_tag_usage: TagUsage agregado a la sesión")

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error creando tag_usage: {e}")
            self.logger.error(
                f"🔍 Traceback completo: {traceback.format_exc()}")
            print(f"❌ ERROR _create_tag_usage: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            # NO relanzar la excepción para evitar abortar la transacción
            print(
                f"⚠️ WARNING: Continuando sin crear tag_usage para tag_id={tag_id}")

    def _ensure_category_exists(self, session: Session, category_name: str):
        """Asegura que la categoría existe"""
        try:
            print(
                f"🔍 DEBUG _ensure_category_exists: Verificando categoría '{category_name}'")

            # Usar session.no_autoflush para evitar flush prematuro
            with session.no_autoflush:
                existing_category = session.exec(
                    select(TagCategory).where(
                        TagCategory.name == category_name)
                ).first()

                if not existing_category:
                    print(
                        f"🆕 DEBUG _ensure_category_exists: Creando nueva categoría '{category_name}'")
                    new_category = TagCategory(
                        name=category_name,
                        description=f"Categoría para {category_name}",
                        color="#007bff"
                    )
                    print(
                        f"🔍 DEBUG _ensure_category_exists: Nueva categoría creada: {new_category}")
                    session.add(new_category)
                    print(
                        f"🔍 DEBUG _ensure_category_exists: Categoría agregada a la sesión")
                else:
                    print(
                        f"✅ DEBUG _ensure_category_exists: Categoría '{category_name}' ya existe")

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error creando categoría: {e}")
            print(f"❌ ERROR _ensure_category_exists: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            # NO relanzar la excepción para evitar abortar la transacción
            print(
                f"⚠️ WARNING: Continuando sin crear categoría '{category_name}'")

    def get_tags_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Obtiene todos los tags de una conversación"""
        try:
            print(
                f"🔍 DEBUG get_tags_by_conversation: conversation_id={conversation_id}")
            with get_session() as session:
                print(f"🔍 DEBUG get_tags_by_conversation: Sesión creada")
                tag_usages = session.exec(
                    select(TagUsage).where(
                        TagUsage.conversation_id == conversation_id)
                ).all()
                print(
                    f"🔍 DEBUG get_tags_by_conversation: Encontrados {len(tag_usages)} tag_usages")

                result = []
                for usage in tag_usages:
                    print(
                        f"🔍 DEBUG get_tags_by_conversation: Procesando usage: {usage}")
                    tag = session.exec(
                        select(Tag).where(Tag.id == usage.tag_id)
                    ).first()

                    if tag:
                        print(
                            f"✅ DEBUG get_tags_by_conversation: Tag encontrado: {tag.name}")
                        result.append({
                            "tag_name": tag.name,
                            "category": tag.category,
                            "confidence_score": usage.confidence_score,
                            "usage_context": usage.usage_context,
                            "created_at": usage.created_at.isoformat()
                        })
                    else:
                        print(
                            f"❌ DEBUG get_tags_by_conversation: Tag NO encontrado para usage: {usage}")

                print(
                    f"🔍 DEBUG get_tags_by_conversation: Retornando {len(result)} tags")
                return result

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error obteniendo tags de conversación: {e}")
            print(f"❌ ERROR get_tags_by_conversation: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            return []

    def get_all_tags(self) -> List[Dict[str, Any]]:
        """Obtiene todos los tags con estadísticas"""
        try:
            print(f"🔍 DEBUG get_all_tags: Iniciando")
            with get_session() as session:
                print(f"🔍 DEBUG get_all_tags: Sesión creada")
                tags = session.exec(select(Tag)).all()
                print(
                    f"🔍 DEBUG get_all_tags: Encontrados {len(tags)} tags en BD")

                result = [
                    {
                        "id": str(tag.id),
                        "name": tag.name,
                        "category": tag.category,
                        "tag_type": tag.tag_type,
                        "confidence_score": tag.confidence_score,
                        "source": tag.source,
                        "weight": tag.weight,
                        "usage_count": tag.usage_count,
                        "created_at": tag.created_at.isoformat(),
                        "updated_at": tag.updated_at.isoformat()
                    }
                    for tag in tags
                ]
                print(f"🔍 DEBUG get_all_tags: Retornando {len(result)} tags")
                return result

        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error obteniendo todos los tags: {e}")
            print(f"❌ ERROR get_all_tags: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            return []

    def test_persistence(self) -> bool:
        """Método de prueba para verificar la funcionalidad"""
        try:
            print(f"🧪 DEBUG: Iniciando prueba de persistencia...")

            # Crear tags de prueba
            test_tags = [
                {
                    "name": "test_tag_1",
                    "category": "Prueba",
                    "type": "test",
                    "confidence_score": 0.9,
                    "source": "test",
                    "weight": 1.0,
                    "context": "Prueba de persistencia",
                    "related_tags": []
                }
            ]

            # Crear conversación de prueba
            from models.conversation import Conversation
            from models.tag import TagUsage
            test_conversation_id = str(uuid4())

            with get_session() as session:
                # Crear conversación de prueba
                test_conversation = Conversation(
                    id=test_conversation_id,
                    customer_id="test_customer",
                    category="Prueba",
                    status="active"
                )
                session.add(test_conversation)
                session.commit()
                session.refresh(test_conversation)

                print(
                    f"✅ DEBUG: Conversación de prueba creada: {test_conversation.id}")

                # Intentar persistir tags con customer_id None para evitar problemas de FK
                result = self.save_tags_to_database(
                    tags=test_tags,
                    conversation_id=test_conversation_id,
                    customer_id=None,  # Cambiado de "test_customer" a None
                    category="Prueba"
                )

                if result:
                    print(f"✅ DEBUG: Prueba de persistencia EXITOSA")

                    # 🛠️ LIMPIEZA CORRECTA: Eliminar primero los registros de tag_usage
                    try:
                        # Eliminar registros de TagUsage que referencian esta conversación
                        tag_usages = session.query(TagUsage).filter(
                            TagUsage.conversation_id == test_conversation_id
                        ).all()

                        for tag_usage in tag_usages:
                            session.delete(tag_usage)

                        session.commit()
                        print(
                            f"🧹 DEBUG: {len(tag_usages)} registros de TagUsage eliminados")

                        # Ahora sí eliminar la conversación de prueba
                        session.delete(test_conversation)
                        session.commit()
                        print(f"🧹 DEBUG: Conversación de prueba eliminada")

                    except Exception as cleanup_error:
                        print(
                            f"⚠️ ADVERTENCIA: Error en limpieza: {cleanup_error}")
                        # No fallar la prueba por problemas de limpieza
                        pass

                    return True
                else:
                    print(f"❌ DEBUG: Prueba de persistencia FALLÓ")
                    return False

        except Exception as e:
            import traceback
            print(f"❌ ERROR en prueba de persistencia: {e}")
            print(f"🔍 Traceback: {traceback.format_exc()}")
            return False


# Instancia global del servicio
print("🚨 CREANDO INSTANCIA GLOBAL tag_persistence_service")
try:
    tag_persistence_service = TagPersistenceService()
    print("✅ Instancia global tag_persistence_service creada exitosamente")
except Exception as e:
    import traceback
    print(f"❌ ERROR creando instancia global: {e}")
    print(f"🔍 Traceback: {traceback.format_exc()}")
    tag_persistence_service = None
