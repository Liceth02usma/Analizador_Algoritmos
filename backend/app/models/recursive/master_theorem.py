from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy

class MasterTheoremAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente del Teorema Maestro."""
    
    a: int = Field(..., description="Parámetro 'a': número de subproblemas.")
    b: int = Field(..., description="Parámetro 'b': factor de división de n.")
    f_n: str = Field(..., description="Función de trabajo adicional f(n).")
    log_b_a: str = Field(..., description="Valor de n^(log_b(a)).")
    comparison: str = Field(
        ..., 
        description="Comparación entre f(n) y n^log_b(a) (ej: 'f(n) = n es Θ(n^log₂(n))')."
    )
    case_id: str = Field(
        ..., 
        description="Caso del Teorema Maestro que aplica (Caso 1, Caso 2 o Caso 3)."
    )
    complexity: str = Field(
        ..., 
        description="Complejidad final en notación Big-O (ej: 'O(n log n)')."
    )
    detailed_explanation: str = Field(
        ..., 
        description="Explicación completa del proceso paso a paso."
    )


# **********************************************
# 2. Analizador de Ecuaciones (Para Teorema Maestro)
# **********************************************

class MasterEquationAnalyzer:
    """
    Analiza la ecuación y extrae los parámetros a, b, f(n).
    Identifica si es aplicable al Teorema Maestro.
    """
    
    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """Extrae a, b, y f(n) de ecuaciones de la forma T(n) = aT(n/b) + f(n)."""
        eq = equation.replace(" ", "").lower()
        
        params = {
            'original': equation,
            'normalized': eq,
            'a': None, 
            'b': None, 
            'f_n': None, 
            'is_master_form': False, 
            'is_trivial': False,
            'trivial_result': None 
        }
        
        # Patrón para T(n) = aT(n/b) + f(n)
        master_pattern = r't\(n\)=(\d*)t\(n/(\d+)\)\s*(?:\+)?\s*(.*)'
        master_matches = re.findall(master_pattern, eq)
        
        if master_matches:
            match = master_matches[0]
            a_str, b_str, f_n_raw = match
            
            # a: Coeficiente de T(n/b), por defecto 1 si no está explícito
            params['a'] = int(a_str) if a_str else 1
            # b: Divisor de n
            params['b'] = int(b_str)
            # f(n): El trabajo restante. Quitar el = de T(n)= y el término de recursión
            f_n = f_n_raw.replace('t(n)=', '').replace('+', '').strip()
            
            # Asegurar que f(n) no esté vacío
            params['f_n'] = f_n if f_n else '1'
            
            # El Teorema Maestro requiere a >= 1, b > 1.
            if params['a'] >= 1 and params['b'] > 1:
                params['is_master_form'] = True
        
        # El Teorema Maestro no tiene casos triviales resueltos por reglas simples
        # como en el método del árbol, todo se delega al agente/algoritmo del teorema.
        
        return params


# **********************************************
# 3. Agente de Resolución Compleja (Teorema Maestro)
# **********************************************

class MasterTheoremAgent(AgentBase[MasterTheoremAgentOutput]):
    """
    Agente especializado en resolver recurrencias usando el Teorema Maestro.
    Se usa para ecuaciones de la forma T(n) = aT(n/b) + f(n).
    """
    
    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        # Simulación de la inicialización de AgentBase
        self.response_format = MasterTheoremAgentOutput
        self.tools = []
        self.context_schema = None
        self.SYSTEM_PROMPT = "" 
        super().__init__(model_type)
    
    def _configure(self) -> None:
        """Configura el agente según AgentBase."""
        self.response_format = MasterTheoremAgentOutput
        self.tools = []
        self.context_schema = None
        
        # Usando raw string (r"...") para evitar problemas con \
        self.SYSTEM_PROMPT = r"""Eres un experto en Análisis de Algoritmos especializado en el **TEOREMA MAESTRO**.

**OBJETIVO:** Resolver ecuaciones de recurrencia de la forma $T(n) = aT(n/b) + f(n)$ aplicando las reglas del Teorema Maestro y justificando el Caso aplicado.

---
**REGLAS DEL TEOREMA MAESTRO (Comparar $f(n)$ con $\theta(n^{\log_b a})$):**

1.  **Caso 1:** Si $f(n) = O(n^{\log_b a - \epsilon})$ para algún $\epsilon > 0$ (es decir, $f(n)$ es polinomialmente *más pequeña*).
    * **Resultado:** $T(n) = \Theta(n^{\log_b a})$

2.  **Caso 2:** Si $f(n) = \Theta(n^{\log_b a})$ (son del *mismo orden*).
    * **Resultado:** $T(n) = \Theta(n^{\log_b a} \log n)$

3.  **Caso 3:** Si $f(n) = \Omega(n^{\log_b a + \epsilon})$ para algún $\epsilon > 0$ (es decir, $f(n)$ es polinomialmente *más grande*) **Y** se cumple la **condición de regularidad**: $a f(n/b) \leq c f(n)$ para alguna constante $c < 1$ y $n$ suficientemente grande.
    * **Resultado:** $T(n) = \Theta(f(n))$

---
**PROCESO OBLIGATORIO (5 PASOS):**

**PASO 1: EXTRAER PARÁMETROS**
Identificar $a$, $b$, y $f(n)$.

**PASO 2: CALCULAR LA CLASE CRÍTICA**
Calcular el valor de $\log_b a$. El término crítico para comparar es $n^{\log_b a}$.

**PASO 3: COMPARAR $f(n)$ con $n^{\log_b a}$**
Determinar la relación asintótica usando notaciones $O$, $\Theta$, $\Omega$.

**PASO 4: IDENTIFICAR EL CASO APLICABLE**
Seleccionar el Caso 1, 2 o 3 basado en la comparación. Si es Caso 3, verificar la Condición de Regularidad.

**PASO 5: OBTENER COMPLEJIDAD FINAL**
Aplicar la fórmula del caso seleccionado y expresar el resultado en notación $O$ (Big-O).

---
**FORMATO DE SALIDA:**
Debes responder con un objeto MasterTheoremAgentOutput que contenga todos los campos solicitados, siendo preciso en la notación matemática (ej: $\log_2 n$)."""
    
    def solve_complex(self, equation: str, params: Dict[str, Any]) -> MasterTheoremAgentOutput:
        """
        Resuelve la ecuación usando el agente del Teorema Maestro.
        """
        if not params['is_master_form']:
            raise ValueError("La ecuación no está en la forma T(n) = aT(n/b) + f(n) requerida por el Teorema Maestro.")
        
        # Preparar contexto para el agente
        context_info = f"""
        INFORMACIÓN DETECTADA:
        - Ecuación: {equation}
        - Subproblemas (a): {params.get('a', '?')}
        - Factor de división (b): {params.get('b', '?')}
        - Trabajo adicional f(n): {params.get('f_n', '?')}
        """
        content = f"""Resuelve esta ecuación de recurrencia usando el **TEOREMA MAESTRO**:

            **Ecuación:** {equation}

            {context_info}

            Sigue los 5 pasos obligatorios:
            1. Extraer Parámetros (a, b, f(n)).
            2. Calcular la Clase Crítica $n^{{\\log_b a}}$.
            3. Comparar $f(n)$ con $n^{{\\log_b a}}$.
            4. Identificar el Caso (1, 2, o 3).
            5. Obtener Complejidad Final.

            Responde con el objeto MasterTheoremAgentOutput completo.
        """
        
        # SIMULACIÓN: En un entorno real, esto invocaría el LLM.
        # Aquí se usa el método base simulado.
        result = self.invoke_simple(content=content, thread_id=f"master_{abs(hash(equation))}")
        output = self.extract_response(result)
        
        if output is None:
            # En caso de que la simulación falle (o el LLM en la realidad)
            return MasterTheoremAgentOutput.parse_obj({
                'a': params['a'] or 0, 
                'b': params['b'] or 0, 
                'f_n': params['f_n'] or 'Error', 
                'log_b_a': 'Error de cálculo', 
                'case_id': 'No resuelto', 
                'comparison': 'No se pudo obtener la comparación',
                'complexity': 'O(?)', 
                'detailed_explanation': "El agente falló al retornar el formato estructurado."
            })
            
        return output


# **********************************************
# 4. Estrategia Principal (Implementa RecurrenceStrategy)
# **********************************************

class MasterTheoremStrategy(RecurrenceStrategy):
    """
    Estrategia híbrida para resolver recurrencias usando el Teorema Maestro.
    """
    
    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Teorema Maestro"
        self.description = (
            "Resuelve recurrencias de la forma T(n) = aT(n/b) + f(n) "
            "comparando f(n) con el término crítico n^(log_b(a))."
        )
        self.enable_verbose = enable_verbose
        self.agent: Optional[MasterTheoremAgent] = None
    
    def _get_agent(self) -> MasterTheoremAgent:
        """Lazy loading del agente."""
        if self.agent is None:
            if self.enable_verbose:
                print("[MasterTheoremStrategy] Inicializando agente...")
            self.agent = MasterTheoremAgent(
                model_type="Modelo_Codigo",
                enable_verbose=self.enable_verbose
            )
        return self.agent
    
    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """
        Resuelve la ecuación de recurrencia usando el Teorema Maestro.
        """
        try:
            params = MasterEquationAnalyzer.parse_equation(recurrenceEquation)
            
            if not params['is_master_form']:
                raise ValueError(
                    "La ecuación no sigue el formato $T(n) = aT(n/b) + f(n)$ con $a \\geq 1$ y $b > 1$, "
                    "por lo que el Teorema Maestro no es aplicable."
                )

            # Usar agente para el proceso de resolución (no hay casos triviales con reglas simples)
            agent = self._get_agent()
            agent_output = agent.solve_complex(recurrenceEquation, params)
            
            # Formatear resultado
            result = {
                'complexity': agent_output.complexity,
                'steps': self._format_steps(agent_output),
                'explanation': agent_output.detailed_explanation,
                'applicable': True,
                'method': self.name,
                'a': agent_output.a,
                'b': agent_output.b,
                'f_n': agent_output.f_n,
                'log_b_a': agent_output.log_b_a,
                'case': agent_output.case_id
            }
            
            return result
            
        except ValueError as e:
            return {
                'complexity': 'O(?)',
                'steps': [str(e)],
                'explanation': f"El Teorema Maestro no pudo aplicarse. Razón: {str(e)}",
                'applicable': False,
                'method': self.name
            }
        except Exception as e:
            return {
                'complexity': 'O(?)',
                'steps': [f"Error interno: {str(e)}"],
                'explanation': f"Error inesperado durante la resolución: {str(e)}",
                'applicable': False,
                'method': self.name
            }
    
    def _format_steps(self, agent_output: MasterTheoremAgentOutput) -> List[str]:
        """Formatea la salida del agente en pasos legibles."""
        steps = []
        
        # Paso 1: Parámetros
        steps.append("**Paso 1 - Extraer Parámetros:**")
        steps.append(f"  a = {agent_output.a}")
        steps.append(f"  b = {agent_output.b}")
        steps.append(f"  f(n) = {agent_output.f_n}")
        steps.append("")
        
        # Paso 2: Clase Crítica
        steps.append(r"**Paso 2 - Clase Crítica $\mathbf{n^{\log_b a}}$:**")
        steps.append(f"   $n^{{\\log_{agent_output.b} {agent_output.a}}} = {agent_output.log_b_a}$")
        steps.append("")
        
        # Paso 3: Comparación
        steps.append(r"**Paso 3 - Comparar $\mathbf{f(n)}$ con $\mathbf{n^{\log_b a}}$:**")
        steps.append(f"   Comparación: {agent_output.comparison}")
        steps.append("")
        
        # Paso 4: Caso Aplicable
        steps.append("**Paso 4 - Identificar Caso:**")
        steps.append(f"   Aplica el **{agent_output.case_id}** del Teorema Maestro.")
        steps.append("")
        
        # Paso 5: Complejidad Final
        steps.append("**Paso 5 - Complejidad Final:**")
        steps.append(f"   Complejidad: {agent_output.complexity}")
        
        return steps