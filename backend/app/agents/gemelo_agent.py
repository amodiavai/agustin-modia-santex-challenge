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
    token_usage: Dict[str, int]  # Conteo de tokens

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
    
    def _load_prompts(self):
        """
        Carga los prompts desde archivos externos
        
        Returns:
            Diccionario con los prompts cargados
        """
        prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        prompts = {}
        
        for prompt_file in ["classify.txt", "rag.txt", "router.txt"]:
            path = os.path.join(prompts_dir, prompt_file)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    prompts[os.path.splitext(prompt_file)[0]] = f.read()
            else:
                logger.warning(f"Archivo de prompt no encontrado: {path}")
        
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
    
    def export_workflow_svg(self, filename="langgraph_workflow.svg"):
        """
        Exporta el grafo de nodos de LangGraph como SVG.
        
        Args:
            filename: Nombre del archivo de salida
            
        Returns:
            Ruta del archivo SVG generado
        """
        try:
            # Crear directorio temporal si no existe
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
            os.makedirs(output_dir, exist_ok=True)
            
            # Ruta completa del archivo
            output_path = os.path.join(output_dir, filename)
            
            # Crear SVG manual del workflow
            svg_content = self._create_manual_svg()
            
            # Escribir el SVG
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            logger.info(f"Grafo exportado como {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error exportando grafo: {str(e)}")
            raise
    
    def _create_manual_svg(self):
        """
        Crea un SVG manual del flujo de trabajo del agente
        
        Returns:
            Contenido SVG como string
        """
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .node { fill: #e1f5fe; stroke: #01579b; stroke-width: 2; }
      .start { fill: #c8e6c9; stroke: #2e7d32; }
      .end { fill: #ffcdd2; stroke: #c62828; }
      .text { font-family: Arial, sans-serif; font-size: 14px; text-anchor: middle; }
      .edge { stroke: #333; stroke-width: 2; fill: none; marker-end: url(#arrowhead); }
      .condition { fill: #fff9c4; stroke: #f57f17; }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
    </marker>
  </defs>
  
  <!-- START node -->
  <rect x="350" y="50" width="100" height="40" rx="20" class="start" />
  <text x="400" y="75" class="text">START</text>
  
  <!-- Search Knowledge node -->
  <rect x="300" y="150" width="200" height="60" rx="10" class="node" />
  <text x="400" y="175" class="text">Search Knowledge</text>
  <text x="400" y="195" class="text" style="font-size: 12px;">(Buscar en vectores)</text>
  
  <!-- Decision diamond -->
  <polygon points="400,280 480,320 400,360 320,320" class="condition" />
  <text x="400" y="320" class="text" style="font-size: 12px;">¿Datos</text>
  <text x="400" y="335" class="text" style="font-size: 12px;">relevantes?</text>
  
  <!-- Generate Response node -->
  <rect x="150" y="450" width="180" height="60" rx="10" class="node" />
  <text x="240" y="475" class="text">Generate Response</text>
  <text x="240" y="495" class="text" style="font-size: 12px;">(Con contexto RAG)</text>
  
  <!-- No Data Response node -->
  <rect x="470" y="450" width="180" height="60" rx="10" class="node" />
  <text x="560" y="475" class="text">No Data Response</text>
  <text x="560" y="495" class="text" style="font-size: 12px;">(Sin información)</text>
  
  <!-- END node -->
  <rect x="350" y="550" width="100" height="40" rx="20" class="end" />
  <text x="400" y="575" class="text">END</text>
  
  <!-- Edges -->
  <!-- START to Search Knowledge -->
  <line x1="400" y1="90" x2="400" y2="150" class="edge" />
  
  <!-- Search Knowledge to Decision -->
  <line x1="400" y1="210" x2="400" y2="280" class="edge" />
  
  <!-- Decision to Generate Response (YES) -->
  <line x1="350" y1="330" x2="240" y2="450" class="edge" />
  <text x="280" y="380" class="text" style="font-size: 12px; fill: green;">Sí</text>
  
  <!-- Decision to No Data Response (NO) -->
  <line x1="450" y1="330" x2="560" y2="450" class="edge" />
  <text x="520" y="380" class="text" style="font-size: 12px; fill: red;">No</text>
  
  <!-- Generate Response to END -->
  <line x1="240" y1="510" x2="380" y2="550" class="edge" />
  
  <!-- No Data Response to END -->
  <line x1="560" y1="510" x2="420" y2="550" class="edge" />
  
  <!-- Title -->
  <text x="400" y="30" class="text" style="font-size: 18px; font-weight: bold;">Gemelo Digital - Flujo de Agente LangGraph</text>
</svg>'''
        return svg_content
            
    def _create_visualization_graph(self):
        """
        Crea una versión del grafo de estados específicamente para visualización
        (sin compilar)
        
        Returns:
            StateGraph: Grafo de estados sin compilar para visualización
        """
        # Crear el grafo
        graph = StateGraph(AgentState)
        
        # Definir nodos (los mismos que en _create_agent_workflow)
        graph.add_node("search_knowledge", self._search_knowledge)
        graph.add_node("generate_response", self._generate_response)
        graph.add_node("no_data_response", self._no_data_response)
        
        # Definir flujo - SIEMPRE buscar en la base de conocimientos primero
        graph.add_edge(START, "search_knowledge")
        
        # Basado en si se encontró información relevante, decidir qué respuesta dar
        graph.add_conditional_edges(
            "search_knowledge",
            lambda state: "generate_response" if state.get("has_relevant_data", False) else "no_data_response"
        )
        
        graph.add_edge("generate_response", END)
        graph.add_edge("no_data_response", END)
        
        # Devolver el grafo SIN compilar
        return graph
    
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
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
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
            
            # Extraer respuesta y conteo de tokens
            response_text = response.choices[0].message.content.strip()
            
            # Obtener información de uso de tokens
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Actualizar estado
            return {
                **state,
                "response": response_text,
                "messages": messages,
                "token_usage": token_usage,
                "thought_process": thought_process + f"\n\nRespuesta generada ({len(response_text)} caracteres) - Tokens: {token_usage['total_tokens']}"
            }
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return {
                **state,
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
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
            "has_relevant_data": False,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        
        # Ejecutar el workflow del agente
        try:
            # Usamos ainvoke en lugar de arun (que no existe en LangGraph 0.0.54)
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "response": final_state["response"],
                "sources": final_state.get("sources", []),
                "thought_process": final_state.get("thought_process", ""),
                "token_usage": final_state.get("token_usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            }
        except Exception as e:
            logger.error(f"Error en ejecución del workflow: {str(e)}")
            return {
                "response": "Lo siento, ocurrió un error al procesar tu mensaje.",
                "sources": [],
                "thought_process": f"Error: {str(e)}",
                "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
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
            "has_relevant_data": False,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
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
