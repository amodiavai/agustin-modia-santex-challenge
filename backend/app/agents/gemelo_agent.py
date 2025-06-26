import os
import logging
from typing import Dict, List, Any, AsyncGenerator, Optional, Tuple, TypedDict, cast
import json
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from openai import OpenAI, AsyncOpenAI

from app.services.qdrant_service import QdrantService
from app.services.embeddings_service import EmbeddingsService

logger = logging.getLogger(__name__)

# Definir tipos para el estado del agente
class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    query: str
    history: List[Dict[str, str]]
    needs_rag: bool
    context: List[str]
    sources: List[Dict[str, Any]]
    thought_process: str
    response: str
    has_relevant_data: bool

class GemeloAgent:
    def __init__(self):
        """
        Inicializa el agente LangGraph para el gemelo digital
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no encontrada en variables de entorno")
            
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info(f"Utilizando modelo OpenAI: {self.model}")
        
        # Inicializar servicios externos
        self.qdrant_service = QdrantService()
        self.embeddings_service = EmbeddingsService()
        
        # Inicializar el grafo de agente
        self.workflow = self._create_agent_workflow()
        
        # Cargar los system prompts
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """
        Carga los prompts del sistema desde archivos
        
        Returns:
            Diccionario con los prompts
        """
        prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        prompts = {}
        
        # Verificar si existe el directorio de prompts
        if not os.path.exists(prompts_dir):
            logger.warning(f"El directorio de prompts {prompts_dir} no existe")
            os.makedirs(prompts_dir, exist_ok=True)
            
            # Crear prompts por defecto
            return {
                "system": "Eres el gemelo digital de Agustín Modia. Responde como si fueras Agustín.",
                "classify": "Determina si la consulta necesita información específica de los documentos.",
                "router": "Selecciona la mejor ruta para responder a la consulta.",
                "rag": "Genera una respuesta basada en el contexto proporcionado."
            }
        
        # Cargar prompts desde archivos
        for prompt_file in os.listdir(prompts_dir):
            if prompt_file.endswith(".txt"):
                prompt_name = prompt_file.replace(".txt", "")
                with open(os.path.join(prompts_dir, prompt_file), "r", encoding="utf-8") as f:
                    prompts[prompt_name] = f.read()
        
        # Asegurarse de que existan los prompts básicos
        default_prompts = {
            "system": "Eres el gemelo digital de Agustín Modia. Responde como si fueras Agustín.",
            "classify": "Determina si la consulta necesita información específica de los documentos.",
            "router": "Selecciona la mejor ruta para responder a la consulta.",
            "rag": "Genera una respuesta basada en el contexto proporcionado."
        }
        
        for key, value in default_prompts.items():
            if key not in prompts:
                prompts[key] = value
        
        return prompts
    
    def _create_agent_workflow(self) -> StateGraph:
        """
        Crea el flujo de trabajo del agente usando LangGraph
        
        Returns:
            Grafo de estados del agente
        """
        # Crear el grafo
        workflow = StateGraph(AgentState)
        
        # Definir nodos
        workflow.add_node("search_knowledge", self._search_knowledge)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("no_data_response", self._no_data_response)
        
        # Definir flujo - SIEMPRE buscar en la base de conocimientos primero
        workflow.add_edge(START, "search_knowledge")
        
        # Basado en si se encontró información relevante, decidir qué respuesta dar
        workflow.add_conditional_edges(
            "search_knowledge",
            lambda state: "generate_response" if state.get("has_relevant_data", False) else "no_data_response"
        )
        
        workflow.add_edge("generate_response", END)
        workflow.add_edge("no_data_response", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    async def _no_data_response(self, state: AgentState) -> AgentState:
        """
        Genera una respuesta cuando no hay datos suficientes en la base de conocimientos
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con la respuesta estándar
        """
        response = "Hola, soy el gemelo de Agustín Modia. Estoy preparado y entrenado para responder solo con la información contenida en su base de conocimientos. Actualmente no tengo datos suficientes para responder esa consulta."
        
        return {
            **state,
            "response": response,
            "thought_process": state.get("thought_process", "") + "\n\nNo se encontró información relevante en la base de conocimientos."
        }
    
    async def _search_knowledge(self, state: AgentState) -> AgentState:
        """
        Busca información relevante en la base de conocimiento
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con flag de relevancia
        """
        query = state["query"]
        thought_process = state.get("thought_process", "")
        
        try:
            # Inicializar colección si no existe
            await self.qdrant_service.initialize_collection()
            
            # Generar embedding para la consulta
            query_embeddings = await self.embeddings_service.create_embeddings([query])
            if not query_embeddings:
                raise ValueError("No se pudo generar embedding para la consulta")
                
            query_vector = query_embeddings[0]
            
            # Buscar documentos relevantes - Incrementamos el límite para tener más opciones a filtrar
            search_results = await self.qdrant_service.search(
                query_vector=query_vector,
                limit=10  # Aumentamos el límite para tener más opciones
            )
            
            # Extraer texto y fuentes
            context = []
            sources = []
            
            # Identificar si hay documentos del CV oficial
            cv_results = []
            other_results = []
            
            # Clasificar los resultados por tipo
            for result in search_results:
                file_name = result["metadata"].get("file_name", "").lower()
                
                # Si el nombre del archivo contiene 'resume' o 'cv', es parte del CV oficial
                if "resume" in file_name or "cv" in file_name:
                    cv_results.append(result)
                else:
                    other_results.append(result)
            
            # Priorizar el CV oficial - máximo 3 fragmentos del CV
            prioritized_results = cv_results[:3]
            
            # Agregar otros resultados hasta completar 5 en total
            remaining_slots = 5 - len(prioritized_results)
            if remaining_slots > 0 and other_results:
                prioritized_results.extend(other_results[:remaining_slots])
                
            # Procesar los resultados priorizados
            for result in prioritized_results:
                context.append(result["text"])
                sources.append({
                    "text": result["text"][:150] + "..." if len(result["text"]) > 150 else result["text"],
                    "source": result["metadata"].get("source", ""),
                    "file_name": result["metadata"].get("file_name", ""),
                    "document_summary": result["metadata"].get("document_summary", ""),
                    "document_type": result["metadata"].get("document_type", "general"),
                    "relevance": result["score"],
                    "is_cv": "resume" in result["metadata"].get("file_name", "").lower() or "cv" in result["metadata"].get("file_name", "").lower()
                })
            
            # Determinar si hay información relevante suficiente
            # Ser muy permisivo: si hay cualquier resultado, intentar responder
            has_relevant_data = False
            if prioritized_results:
                highest_score = max(result["score"] for result in prioritized_results)
                
                # Si hay al menos un resultado con score > 0.2, considerar que hay información relevante
                if highest_score > 0.2:
                    has_relevant_data = True
            
            # Actualizar el proceso de pensamiento con información detallada
            new_thought = thought_process + f"\n\nBúsqueda RAG: Encontrados {len(search_results)} documentos relevantes."
            new_thought += f"\nRelevancia suficiente: {'Sí' if has_relevant_data else 'No'}"
            
            # Agregar información de los resúmenes de documentos si están disponibles
            if sources:
                # Obtener nombres de archivos de las fuentes principales
                main_sources = [s['file_name'] for s in sources[:2]]
                new_thought += f"\nFuentes principales: {', '.join(main_sources)}"
                
                # Agregar resúmenes de documentos
                doc_summaries = []
                for s in sources:
                    if "document_summary" in s and s["document_summary"]:
                        summary = s["document_summary"]
                        # Tomar solo los primeros 100 caracteres del resumen para el proceso de pensamiento
                        short_summary = f"{summary[:100]}..." if len(summary) > 100 else summary
                        doc_summaries.append(f"{s['file_name']}: {short_summary}")
                
                # Agregar resúmenes únicos (sin duplicados)
                unique_summaries = list(set(doc_summaries))[:2]  # Limitar a 2 resúmenes
                if unique_summaries:
                    new_thought += f"\nResúmenes de documentos:\n- {' '.join(unique_summaries)}"
            
            return {
                **state,
                "context": context,
                "sources": sources,
                "has_relevant_data": has_relevant_data,
                "thought_process": new_thought
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda de conocimiento: {str(e)}")
            return {
                **state,
                "context": [],
                "sources": [],
                "has_relevant_data": False,
                "thought_process": thought_process + f"\n\nError en búsqueda RAG: {str(e)}"
            }
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """
        Genera una respuesta basada en el contexto y la personalidad del gemelo
        
        Args:
            state: Estado actual del agente
            
        Returns:
            Estado actualizado con la respuesta
        """
        query = state["query"]
        history = state.get("history", [])
        context = state.get("context", [])
        thought_process = state.get("thought_process", "")
        
        try:
            # Preparar el prompt con o sin contexto
            system_prompt = self.prompts.get("system", "Eres el gemelo digital de Agustín Modia.")
            
            # Construir messages para la API
            messages = [{"role": "system", "content": system_prompt}]
            
            # Agregar historial de conversación
            for msg in history[-5:]:  # Últimos 5 mensajes para mantener contexto
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Si hay contexto de RAG, agregarlo
            if context:
                context_text = "\n\n".join(context)
                messages.append({
                    "role": "user", 
                    "content": (
                        f"Por favor, responde la siguiente pregunta utilizando el contexto proporcionado. "
                        f"Responde como si fueras Agustín Modia, en primera persona.\n\n"
                        f"CONTEXTO:\n{context_text}\n\n"
                        f"PREGUNTA: {query}"
                    )
                })
            else:
                # Si no hay contexto, usar solo la pregunta
                messages.append({"role": "user", "content": query})
            
            # Generar respuesta con la API
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # Extraer respuesta
            response_text = response.choices[0].message.content.strip()
            
            # Actualizar estado
            return {
                **state,
                "response": response_text,
                "messages": messages,
                "thought_process": thought_process + f"\n\nRespuesta generada ({len(response_text)} caracteres)"
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return {
                **state,
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "thought_process": thought_process + f"\n\nError generando respuesta: {str(e)}"
            }
    
    async def process_message(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y devuelve una respuesta
        
        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            
        Returns:
            Diccionario con la respuesta y datos adicionales
        """
        if history is None:
            history = []
            
        # Estado inicial
        initial_state = {
            "messages": [],
            "query": message,
            "history": history,
            "needs_rag": False,
            "context": [],
            "sources": [],
            "thought_process": "Iniciando procesamiento de consulta",
            "response": "",
            "has_relevant_data": False
        }
        
        # Ejecutar el workflow del agente
        try:
            # Usamos ainvoke en lugar de arun (que no existe en LangGraph 0.0.54)
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "response": final_state["response"],
                "sources": final_state.get("sources", []),
                "thought_process": final_state.get("thought_process", "")
            }
        except Exception as e:
            logger.error(f"Error en ejecución del workflow: {str(e)}")
            return {
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "sources": [],
                "thought_process": f"Error: {str(e)}"
            }
    
    async def process_message_streaming(
        self,
        message: str,
        history: List[Dict[str, str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Procesa un mensaje con respuesta en streaming usando RAG obligatorio
        
        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            
        Yields:
            Chunks de la respuesta para streaming
        """
        if history is None:
            history = []
            
        # Estado inicial - SIEMPRE buscar en la base de conocimientos
        initial_state = {
            "messages": [],
            "query": message,
            "history": history,
            "needs_rag": True,  # Siempre necesita RAG
            "context": [],
            "sources": [],
            "thought_process": "Iniciando procesamiento de consulta",
            "response": "",
            "has_relevant_data": False
        }
        
        try:
            # SIEMPRE buscar contexto en la base de conocimientos
            state_with_context = await self._search_knowledge(initial_state)
                
            # Si no hay datos relevantes, devolver mensaje estándar
            if not state_with_context.get("has_relevant_data", False):
                fallback_message = "Hola, soy el gemelo de Agustín Modia. Estoy preparado y entrenado para responder solo con la información contenida en su base de conocimientos. Actualmente no tengo datos suficientes para responder esa consulta."
                yield fallback_message
                return
                
            # Si hay datos relevantes, preparar prompt para streaming
            system_prompt = self.prompts.get("system", "Eres el gemelo digital de Agustín Modia.")
            
            # Construir mensajes
            messages = [{"role": "system", "content": system_prompt}]
            
            # Agregar historial
            for msg in history[-5:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Agregar contexto (siempre hay contexto si llegamos aquí)
            context_text = "\n\n".join(state_with_context["context"])
            messages.append({
                "role": "user", 
                "content": (
                    f"Por favor, responde la siguiente pregunta utilizando el contexto proporcionado. "
                    f"Responde como si fueras Agustín Modia, en primera persona.\n\n"
                    f"CONTEXTO:\n{context_text}\n\n"
                    f"PREGUNTA: {message}"
                )
            })
            
            # Generar streaming con la API
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            # Devolver chunks de texto
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
            
        except Exception as e:
            logger.error(f"Error en streaming: {str(e)}")
            yield f"Lo siento, ocurrió un error: {str(e)}"
