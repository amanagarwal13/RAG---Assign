import re
import logging
import sympy
from typing import Any

logger = logging.getLogger(__name__)

class CalculatorTool:
    """
    Tool for evaluating mathematical expressions in natural language queries.
    """
    
    def __init__(self):
        """Initialize the calculator tool."""
        pass
    
    def execute(self, query: str) -> str:
        """
        Extract and evaluate mathematical expressions from the query.
        
        Args:
            query: The user query containing a mathematical expression
            
        Returns:
            String containing the result of the calculation
        """
        logger.info(f"Calculator processing query: {query}")
        
        # First, try to extract a mathematical expression using regex
        expression = self._extract_expression(query)
        
        if not expression:
            raise ValueError("No valid mathematical expression found in the query")
        
        logger.info(f"Extracted expression: {expression}")
        
        # Evaluate the expression
        try:
            result = self._evaluate_expression(expression)
            return f"The result of {expression} is {result}"
        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}", exc_info=True)
            raise ValueError(f"Error evaluating the expression: {str(e)}")
    
    def _extract_expression(self, query: str) -> str:
        """
        Extract a mathematical expression from the query.
        
        Args:
            query: The user query
            
        Returns:
            The extracted mathematical expression or None if not found
        """
        # Common patterns for mathematical expressions
        patterns = [
            # Pattern for calculations with different operations
            r'calculate\s+([\d\s+\-*/^().,]+)',
            r'compute\s+([\d\s+\-*/^().,]+)',
            r'evaluate\s+([\d\s+\-*/^().,]+)',
            # Pattern for equations with equals sign
            r'solve\s+([\d\s+\-*/^().,=x]+)',
            # More general pattern to catch expressions
            r'((?:\d+\s*[-+*/^]\s*)+\d+)',
            # Pattern for standalone numbers with operators
            r'(\d+\s*[-+*/^]\s*\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Clean up the expression
                expr = match.group(1).strip()
                # Replace common word operators with symbols
                expr = expr.replace('plus', '+')
                expr = expr.replace('minus', '-')
                expr = expr.replace('times', '*')
                expr = expr.replace('multiplied by', '*')
                expr = expr.replace('divided by', '/')
                expr = expr.replace('over', '/')
                expr = expr.replace('squared', '**2')
                expr = expr.replace('cubed', '**3')
                expr = expr.replace('^', '**')
                return expr
        
        # If no match with patterns, try a simple approach for basic arithmetic
        # Look for numbers separated by operators
        simplified_expr = re.search(r'(\d+\s*[+\-*/]\s*\d+)', query)
        if simplified_expr:
            return simplified_expr.group(1).strip()
        
        return None
    
    def _evaluate_expression(self, expression: str) -> Any:
        """
        Safely evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            The result of the evaluation
        """
        # Replace common mathematical functions with their sympy equivalents
        expression = expression.replace('sqrt', 'sympy.sqrt')
        expression = expression.replace('sin', 'sympy.sin')
        expression = expression.replace('cos', 'sympy.cos')
        expression = expression.replace('tan', 'sympy.tan')
        expression = expression.replace('log', 'sympy.log')
        expression = expression.replace('ln', 'sympy.log')
        
        # Remove any unnecessary whitespace
        expression = re.sub(r'\s+', '', expression)
        
        # Use sympy for evaluation (safer than eval)
        try:
            result = sympy.sympify(expression).evalf()
            
            # Format the result
            if result.is_integer:
                return int(result)
            else:
                return float(result)
        except Exception as e:
            logger.error(f"Error in sympy evaluation: {str(e)}", exc_info=True)
            raise ValueError(f"Could not evaluate the expression: {str(e)}")