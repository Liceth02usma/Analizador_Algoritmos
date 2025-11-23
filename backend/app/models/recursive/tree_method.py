from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re
import math

from ...external_services.Agentes.Agent import AgentBase
from .strategy_resolve import RecurrenceStrategy

# **********************************************
# 1. Schema de Respuesta del Agente
# **********************************************

class TreeMethodAgentOutput(BaseModel):
    """Schema estructurado para la respuesta del agente."""
    
    tree_depth: str = Field(
        ..., 
        description="Profundidad del árbol (ej: 'log₂(n)', 'n')"
    )
    levels_expansion: List[str] = Field(
        default_factory=list,
        description="Expansión nivel por nivel del árbol"
    )
    work_per_level: List[str] = Field(
        default_factory=list,
        description="Trabajo calculado en cada nivel"
    )
    total_sum: str = Field(
        ...,
        description="Suma total de todos los niveles"
    )
    sum_simplification: str = Field(
        ...,
        description="Simplificación de la suma (serie geométrica, etc.)"
    )
    complexity: str = Field(
        ...,
        description="Complejidad final en notación Big-O"
    )
    detailed_explanation: str = Field(
        ...,
        description="Explicación completa del proceso paso a paso"
    )


# **********************************************
# 2. Analizador de Ecuaciones (Reglas Rápidas)
# **********************************************

class EquationAnalyzer:
    """
    Analiza la ecuación y extrae parámetros básicos usando reglas.
    Identifica casos triviales que no necesitan agente.
    """
    
    @staticmethod
    def parse_equation(equation: str) -> Dict[str, Any]:
        """Extrae componentes básicos de la ecuación."""
        eq = equation.replace(" ", "").lower()
        
        params = {
            'original': equation,
            'normalized': eq,
            'a': None,              # Número de subproblemas
            'b': None,              # Factor de división
            'k': None,              # Constante de resta
            'f_n': None,            # Función de trabajo
            'type': None,           # Tipo de recurrencia
            'is_trivial': False,    # Si es caso trivial
            'trivial_result': None, # Resultado directo si es trivial
            'has_summation': False, # Si contiene sumatoria
            'summation_params': {}  # Parámetros de la sumatoria
        }
        
        # Detectar sumatorias
        summation_symbols = ['σ', '∑', 'sum', 'Σ']
        has_summation = any(symbol in equation for symbol in summation_symbols)
        
        if has_summation:
            params['has_summation'] = True
            params['type'] = 'summation'
            summation_result = EquationAnalyzer._parse_summation(equation)
            if summation_result:
                params['summation_params'] = summation_result
                params['is_trivial'] = False
                # Las sumatorias no son triviales, necesitan expansión completa
                return params
        
        # Detectar T(n) = aT(n/b) + f(n)
        div_pattern = r'(\d*)t\(n/(\d+)\)'
        div_matches = re.findall(div_pattern, eq)
        
        if div_matches:
            params['type'] = 'divide_conquer'
            
            # Contar cuántas veces aparece el patrón T(n/b) para obtener 'a'
            coef = div_matches[0][0]
            if coef:
                params['a'] = int(coef)
            else:
                # Si no hay coeficiente explícito, contar las ocurrencias
                params['a'] = len(div_matches)
            
            params['b'] = int(div_matches[0][1])
            
            # Extraer f(n) - todo lo que no es T(n/b)
            work = re.sub(r'\d*t\([^)]+\)', '', eq)
            work = work.replace('t(n)=', '').replace('+', '').replace('-','').strip()
            
            # Si f(n) está vacío, es trabajo constante
            params['f_n'] = work if work else '1'
        
        # Detectar T(n) = T(n-k) + f(n)
        sub_pattern = r't\(n-(\d+)\)'
        sub_matches = re.findall(sub_pattern, eq)
        
        if sub_matches and not div_matches:
            params['type'] = 'linear'
            params['k'] = int(sub_matches[0])
            
            work = re.sub(r't\([^)]+\)', '', eq)
            work = work.replace('t(n)=', '').replace('+', '').strip()
            params['f_n'] = work if work else '1'
        
        # Detectar casos TRIVIALES (que no necesitan agente)
        params['is_trivial'] = EquationAnalyzer._check_trivial_case(params)
        if params['is_trivial']:
            params['trivial_result'] = EquationAnalyzer._solve_trivial(params)
        
        return params
    
    @staticmethod
    def _parse_summation(equation: str) -> Optional[Dict[str, Any]]:
        """
        Parsea ecuaciones con sumatorias.
        Formato esperado: T_avg(n) = (1/k) × Σ[i=a to b] T(i), donde T(i) = T(i-1) + c
        """
        try:
            # Buscar factor multiplicativo (1/k)
            factor_pattern = r'\(1/\(?([^)]+)\)?\)'
            factor_match = re.search(factor_pattern, equation)
            multiplicative_factor = None
            if factor_match:
                multiplicative_factor = factor_match.group(1).strip()
            
            # Buscar límites de la sumatoria: Σ[i=a to b]
            summation_pattern = r'[Σ∑σsum]\s*\[i=(\d+)\s+to\s+([^\]]+)\]'
            summation_match = re.search(summation_pattern, equation, re.IGNORECASE)
            
            if not summation_match:
                return None
            
            lower_bound = summation_match.group(1).strip()
            upper_bound = summation_match.group(2).strip()
            
            # Buscar la recurrencia interna T(i) = ...
            inner_pattern = r'donde\s+t\(i\)\s*=\s*([^,]+)'
            inner_match = re.search(inner_pattern, equation, re.IGNORECASE)
            
            inner_recurrence = None
            if inner_match:
                inner_recurrence = inner_match.group(1).strip()
            
            # Buscar caso base
            base_pattern = r't\((\d+)\)\s*=\s*(\d+)'
            base_match = re.search(base_pattern, equation, re.IGNORECASE)
            
            base_case = None
            base_value = None
            if base_match:
                base_case = base_match.group(1)
                base_value = base_match.group(2)
            
            return {
                'original': equation,
                'multiplicative_factor': multiplicative_factor,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'inner_recurrence': inner_recurrence,
                'base_case': base_case,
                'base_value': base_value
            }
        except Exception:
            return None
    
    @staticmethod
    def _check_trivial_case(params: Dict[str, Any]) -> bool:
        """Identifica si es un caso trivial que puede resolverse con reglas."""
        # Caso 1: T(n) = T(n-1) + c (trabajo constante)
        if (params['type'] == 'linear' and 
            params['k'] == 1 and 
            params['f_n'] in ['1', 'c', '']):
            return True
        
        # Caso 2: T(n) = c (ya es constante)
        eq = params['normalized']
        if re.match(r't\(n\)=\d+', eq):
            return True
        
        return False
    
    @staticmethod
    def _solve_trivial(params: Dict[str, Any]) -> Dict[str, Any]:
        """Resuelve casos triviales directamente."""
        if params['type'] == 'linear' and params['k'] == 1:
            # T(n) = T(n-1) + c → O(n)
            return {
                'complexity': 'O(n)',
                'steps': [
                    f"Nivel 0: T(n) → Trabajo: {params['f_n']}",
                    f"Nivel 1: T(n-1) → Trabajo: {params['f_n']}",
                    "...",
                    f"Nivel n: T(0) → Trabajo: {params['f_n']}",
                    f"Total: {params['f_n']} × n niveles = O(n)"
                ],
                'explanation': (
                    f"Recurrencia lineal simple con trabajo constante {params['f_n']} por nivel. "
                    "El árbol tiene profundidad n, cada nivel realiza trabajo constante. "
                    "Suma total: O(n)."
                ),
                'applicable': True,
                'method': 'Método del Árbol (trivial)'
            }
        
        return None


# **********************************************
# 3. Agente de Resolución Compleja
# **********************************************

class TreeMethodAgent(AgentBase[TreeMethodAgentOutput]):
    """
    Agente especializado en resolver recurrencias por el método del árbol.
    Se usa para casos NO triviales que requieren análisis profundo.
    """
    
    def __init__(self, model_type: str = "Modelo_Codigo", enable_verbose: bool = False):
        self.enable_verbose = enable_verbose
        super().__init__(model_type)
    
    def _configure(self) -> None:
        """Configura el agente según AgentBase."""
        self.response_format = TreeMethodAgentOutput
        self.tools = []
        self.context_schema = None
        
        self.SYSTEM_PROMPT = """Eres un experto en Análisis de Algoritmos especializado en el MÉTODO DEL ÁRBOL de recursión.

**OBJETIVO:** Resolver ecuaciones de recurrencia expandiendo el árbol nivel por nivel y sumando los costos.

**PROCESO OBLIGATORIO (5 PASOS):**

---
**PASO 1: DETERMINAR PROFUNDIDAD DEL ÁRBOL**

- Para T(n) = aT(n/b) + f(n): profundidad = log_b(n)
- Para T(n) = T(n-k) + f(n): profundidad = n/k
- Para T_avg(n) = (1/k) × Σ[i=a to b] T(i): profundidad = n (sumatoria de 0 a n)
- Para casos mixtos: analizar hasta el caso base

Ejemplo: T(n) = 2T(n/2) + n → profundidad = log₂(n)
Ejemplo sumatoria: T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i) → profundidad = n

---
**PASO 2: EXPANDIR ÁRBOL NIVEL POR NIVEL**

Formato requerido para cada nivel:
```
Nivel i: [número de nodos] × T([tamaño por nodo])
```

Ejemplo divide y conquista:
```
Nivel 0: 1 × T(n)
Nivel 1: 2 × T(n/2)
Nivel 2: 4 × T(n/4)
Nivel 3: 8 × T(n/8)
...
Nivel log₂(n): n × T(1)
```

Ejemplo sumatoria con T(i) = T(i-1) + c:
```
Nivel 0: T(0) = c (caso base)
Nivel 1: T(1) = T(0) + c = 2c
Nivel 2: T(2) = T(1) + c = 3c
Nivel 3: T(3) = T(2) + c = 4c
...
Nivel i: T(i) = (i+1)c
Nivel n: T(n) = (n+1)c
```

---
**PASO 3: CALCULAR TRABAJO POR NIVEL**

Para cada nivel, calcular: [número de nodos] × [trabajo por nodo]

Ejemplo para T(n) = 2T(n/2) + n:
```
Nivel 0: 1 × n = n
Nivel 1: 2 × (n/2) = n
Nivel 2: 4 × (n/4) = n
Nivel 3: 8 × (n/8) = n
...
```

Ejemplo para sumatoria T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i):
```
Si T(i) = (i+1)c, entonces:
Σ[i=0 to n] T(i) = Σ[i=0 to n] (i+1)c
                 = c × Σ[i=0 to n] (i+1)
                 = c × (1 + 2 + 3 + ... + (n+1))
```

---
**PASO 4: SUMAR TODOS LOS NIVELES**

Identificar el patrón:
- **Serie constante:** c + c + c + ... = c × h(n)
- **Serie geométrica:** c + cr + cr² + ... = c(r^h - 1)/(r - 1)
- **Serie decreciente:** n + n/2 + n/4 + ... ≈ 2n
- **Serie aritmética (sumatorias):** 1 + 2 + 3 + ... + n = n(n+1)/2

Ejemplo: n + n + n + ... (log₂(n) veces) = n × log₂(n)

Ejemplo sumatoria: c × (1 + 2 + 3 + ... + (n+1)) = c × (n+1)(n+2)/2

---
**PASO 5: EXPRESAR EN BIG-O**

Tomar el término dominante de la suma simplificada.

Ejemplo: n × log₂(n) → O(n log n)
Ejemplo sumatoria: Con factor (1/(n+1)), si suma es c(n+1)(n+2)/2:
  → T_avg(n) = (1/(n+1)) × c(n+1)(n+2)/2 = c(n+2)/2 → O(n)

---
**EJEMPLOS COMPLETOS:**

**Ejemplo 1: T(n) = 2T(n/2) + n**
- Profundidad: log₂(n)
- Expansión: 1→2→4→8→...→n nodos
- Trabajo por nivel: n (constante en cada nivel)
- Suma: n × log₂(n)
- Big-O: O(n log n)

**Ejemplo 2: T(n) = 2T(n/2) + 1**
- Profundidad: log₂(n)
- Expansión: 1→2→4→8→...→n nodos
- Trabajo por nivel: 1→2→4→...→n (serie geométrica)
- Suma: 2n - 1 ≈ 2n
- Big-O: O(n)

**Ejemplo 3: T(n) = T(n-1) + n**
- Profundidad: n
- Expansión: T(n)→T(n-1)→T(n-2)→...→T(1)
- Trabajo por nivel: n + (n-1) + (n-2) + ... + 1
- Suma: n(n+1)/2
- Big-O: O(n²)

**Ejemplo 4: T_avg(n) = (1/(n+1)) × Σ[i=0 to n] T(i), donde T(i) = T(i-1) + 1, T(0) = 1**
- Profundidad: n (desde i=0 hasta i=n)
- Expansión de T(i):
  * T(0) = 1
  * T(1) = T(0) + 1 = 2
  * T(2) = T(1) + 1 = 3
  * T(i) = i + 1
- Suma: Σ[i=0 to n] (i+1) = 1 + 2 + 3 + ... + (n+1) = (n+1)(n+2)/2
- Aplicar factor: T_avg(n) = (1/(n+1)) × (n+1)(n+2)/2 = (n+2)/2
- Big-O: O(n)

---
**FORMATO DE SALIDA:**

Debes responder con un objeto TreeMethodAgentOutput que contenga:

1. `tree_depth`: Fórmula de profundidad
2. `levels_expansion`: Lista con la expansión de cada nivel
3. `work_per_level`: Lista con el trabajo calculado por nivel
4. `total_sum`: Expresión de la suma total
5. `sum_simplification`: Simplificación de la suma (identificar tipo de serie)
6. `complexity`: Complejidad final en O(...)
7. `detailed_explanation`: Explicación completa en párrafos

---
**REGLAS IMPORTANTES:**

- SIEMPRE simplifica algebraicamente
- Identifica el tipo de serie (geométrica, aritmética, constante)
- Para sumatorias, expande la recurrencia interna T(i) primero
- Aplica fórmulas de series aritméticas: 1+2+...+n = n(n+1)/2
- Menciona supuestos si los hay
- Sé preciso con las notaciones matemáticas
- Usa subíndices correctamente (log₂, no log2)"""
    
    def solve_complex(self, equation: str, params: Dict[str, Any]) -> TreeMethodAgentOutput:
        """
        Resuelve ecuaciones complejas usando el agente.
        
        Args:
            equation: Ecuación original
            params: Parámetros pre-parseados
            
        Returns:
            TreeMethodAgentOutput con la solución
        """
        try:
            if self.enable_verbose:
                print(f"\n[TreeMethodAgent] 🌳 Resolviendo con agente...")
                print(f"Ecuación: {equation}")
                print(f"Tipo: {params.get('type', 'desconocido')}")
            
            # Preparar contexto para el agente
            context_info = ""
            if params.get('type') == 'summation':
                summation_params = params.get('summation_params', {})
                context_info = f"""
INFORMACIÓN DETECTADA:
- Tipo: Sumatoria
- Factor multiplicativo: 1/{summation_params.get('multiplicative_factor', '?')}
- Límites: i = {summation_params.get('lower_bound', '?')} hasta {summation_params.get('upper_bound', '?')}
- Recurrencia interna: T(i) = {summation_params.get('inner_recurrence', '?')}
- Caso base: T({summation_params.get('base_case', '?')}) = {summation_params.get('base_value', '?')}
- Profundidad esperada: n

INSTRUCCIONES ESPECÍFICAS:
1. Expande la recurrencia interna T(i) nivel por nivel desde el caso base
2. Calcula Σ[i={summation_params.get('lower_bound', 0)} to {summation_params.get('upper_bound', 'n')}] T(i) usando fórmula de serie aritmética
3. Aplica el factor multiplicativo (1/{summation_params.get('multiplicative_factor', '?')})
4. Simplifica y determina complejidad Big-O
"""
            elif params.get('type') == 'divide_conquer':
                context_info = f"""
INFORMACIÓN DETECTADA:
- Tipo: Divide y Conquista
- Subproblemas (a): {params.get('a', '?')}
- Factor de división (b): {params.get('b', '?')}
- Trabajo adicional f(n): {params.get('f_n', '?')}
- Profundidad esperada: log_{params.get('b', '?')}(n)
"""
            elif params.get('type') == 'linear':
                context_info = f"""
INFORMACIÓN DETECTADA:
- Tipo: Recurrencia Lineal
- Constante de resta (k): {params.get('k', '?')}
- Trabajo adicional f(n): {params.get('f_n', '?')}
- Profundidad esperada: n
"""
            
            content = f"""Resuelve esta ecuación de recurrencia usando el MÉTODO DEL ÁRBOL:

**Ecuación:** {equation}

{context_info}

Sigue los 5 pasos del proceso:
1. Determinar profundidad
2. Expandir árbol nivel por nivel
3. Calcular trabajo por nivel
4. Sumar todos los niveles
5. Expresar en Big-O

Responde con el objeto TreeMethodAgentOutput completo."""
            
            thread_id = f"tree_{abs(hash(equation))}"
            result = self.invoke_simple(content=content, thread_id=thread_id)
            output = self.extract_response(result)
            
            if output is None:
                raise ValueError("El agente no retornó una solución válida")
            
            if self.enable_verbose:
                print(f"[TreeMethodAgent] ✅ Solución obtenida")
                print(f"Complejidad: {output.complexity}")
            
            return output
            
        except Exception as e:
            if self.enable_verbose:
                print(f"[TreeMethodAgent] ❌ ERROR: {str(e)}")
            
            # Retornar solución de error
            return TreeMethodAgentOutput(
                tree_depth="Desconocida",
                levels_expansion=["Error en expansión"],
                work_per_level=["Error en cálculo"],
                total_sum="No calculada",
                sum_simplification="Error en simplificación",
                complexity="O(?)",
                detailed_explanation=f"Error al resolver la ecuación: {str(e)}"
            )


# **********************************************
# 4. Estrategia Principal (Implementa RecurrenceStrategy)
# **********************************************

class TreeMethodStrategy(RecurrenceStrategy):
    """
    Estrategia híbrida para resolver recurrencias por el método del árbol.
    
    **Flujo de trabajo:**
    1. Analiza la ecuación con reglas (rápido)
    2. Si es trivial → resuelve directamente
    3. Si es complejo → usa agente IA
    4. Formatea resultado en diccionario estándar
    
    **Uso:**
    ```python
    strategy = TreeMethodStrategy(enable_verbose=True)
    result = strategy.solve("T(n) = 2T(n/2) + n")
    print(result['complexity'])      # "O(n log n)"
    print(result['steps'])           # Lista de pasos
    print(result['explanation'])     # Explicación completa
    ```
    """
    
    def __init__(self, enable_verbose: bool = False):
        super().__init__()
        self.name = "Método del Árbol"
        self.description = (
            "Resuelve recurrencias expandiendo el árbol de recursión nivel por nivel "
            "y sumando los costos de todos los niveles."
        )
        self.enable_verbose = enable_verbose
        self.agent: Optional[TreeMethodAgent] = None
    
    def _get_agent(self) -> TreeMethodAgent:
        """Lazy loading del agente (solo se crea cuando se necesita)."""
        if self.agent is None:
            if self.enable_verbose:
                print("[TreeMethodStrategy] Inicializando agente...")
            self.agent = TreeMethodAgent(
                model_type="Modelo_Codigo",
                enable_verbose=self.enable_verbose
            )
        return self.agent
    
    def solve(self, recurrenceEquation: str) -> Dict[str, Any]:
        """
        Resuelve la ecuación de recurrencia usando el método del árbol.
        
        Args:
            recurrenceEquation: Ecuación en formato "T(n) = ..."
            
        Returns:
            Diccionario con:
            {
                'complexity': str,           # "O(n log n)"
                'steps': List[str],          # Pasos detallados
                'explanation': str,          # Explicación completa
                'applicable': bool,          # True si se pudo resolver
                'method': str,               # "Método del Árbol"
                'tree_depth': str,           # Profundidad del árbol
                'levels_detail': List[str]   # Detalle de cada nivel
            }
        """
        try:
            if self.enable_verbose:
                print(f"\n{'='*70}")
                print(f"[TreeMethodStrategy] Resolviendo ecuación")
                print(f"{'='*70}")
                print(f"Ecuación: {recurrenceEquation}")
            
            # ==========================================
            # PASO 1: Analizar ecuación con reglas
            # ==========================================
            if self.enable_verbose:
                print(f"\n[Paso 1/3] Analizando ecuación con reglas...")
            
            params = EquationAnalyzer.parse_equation(recurrenceEquation)
            
            if self.enable_verbose:
                print(f"Parámetros parseados:")
                print(f"  - Tipo: {params.get('type')}")
                print(f"  - a (subproblemas): {params.get('a')}")
                print(f"  - b (división): {params.get('b')}")
                print(f"  - f(n) (trabajo): {params.get('f_n')}")
                print(f"  - Es trivial: {params.get('is_trivial')}")
                print(f"  - Resultado trivial: {params.get('trivial_result')}")
            
            # ==========================================
            # PASO 2: Resolver caso trivial (si aplica)
            # ==========================================
            if params['is_trivial'] and params['trivial_result'] is not None:
                if self.enable_verbose:
                    print(f"[Paso 2/3] ✅ Caso trivial detectado, resolviendo con reglas...")
                
                trivial_result = params['trivial_result']
                trivial_result['tree_depth'] = 'n' if params['type'] == 'linear' else '1'
                trivial_result['levels_detail'] = trivial_result['steps']
                
                if self.enable_verbose:
                    print(f"✅ Complejidad: {trivial_result['complexity']}")
                
                return trivial_result
            
            # ==========================================
            # PASO 3: Resolver con agente IA
            # ==========================================
            if self.enable_verbose:
                print(f"[Paso 2/3] Caso complejo, delegando al agente...")
            
            agent = self._get_agent()
            agent_output = agent.solve_complex(recurrenceEquation, params)
            
            # ==========================================
            # PASO 4: Formatear resultado
            # ==========================================
            if self.enable_verbose:
                print(f"[Paso 3/3] Formateando resultado...")
            
            result = {
                'complexity': agent_output.complexity,
                'steps': self._format_steps(agent_output),
                'explanation': agent_output.detailed_explanation,
                'applicable': True,
                'method': self.name,
                'tree_depth': agent_output.tree_depth,
                'levels_detail': agent_output.levels_expansion,
                'work_per_level': agent_output.work_per_level,
                'sum_formula': agent_output.total_sum,
                'sum_simplification': agent_output.sum_simplification
            }
            
            if self.enable_verbose:
                print(f"\n{'='*70}")
                print(f"✅ SOLUCIÓN COMPLETADA")
                print(f"{'='*70}")
                print(f"Complejidad: {result['complexity']}")
                print(f"Profundidad: {result['tree_depth']}")
            
            return result
            
        except Exception as e:
            if self.enable_verbose:
                print(f"\n❌ ERROR en TreeMethodStrategy: {str(e)}")
            
            return {
                'complexity': 'O(?)',
                'steps': [f"Error al resolver: {str(e)}"],
                'explanation': f"No se pudo resolver la ecuación usando el método del árbol. Error: {str(e)}",
                'applicable': False,
                'method': self.name
            }
    
    def _format_steps(self, agent_output: TreeMethodAgentOutput) -> List[str]:
        """Formatea la salida del agente en pasos legibles."""
        steps = []
        
        # Paso 1: Profundidad
        steps.append(f"**Paso 1 - Determinar profundidad del árbol:**")
        steps.append(f"   Profundidad = {agent_output.tree_depth}")
        steps.append("")
        
        # Paso 2: Expansión
        steps.append(f"**Paso 2 - Expandir árbol nivel por nivel:**")
        for level in agent_output.levels_expansion:
            steps.append(f"   {level}")
        steps.append("")
        
        # Paso 3: Trabajo por nivel
        steps.append(f"**Paso 3 - Calcular trabajo por nivel:**")
        for work in agent_output.work_per_level:
            steps.append(f"   {work}")
        steps.append("")
        
        # Paso 4: Suma
        steps.append(f"**Paso 4 - Sumar todos los niveles:**")
        steps.append(f"   Suma total: {agent_output.total_sum}")
        steps.append(f"   Simplificación: {agent_output.sum_simplification}")
        steps.append("")
        
        # Paso 5: Big-O
        steps.append(f"**Paso 5 - Complejidad final:**")
        steps.append(f"   {agent_output.complexity}")
        
        return steps


# NOTA: este debe retornar un arbol