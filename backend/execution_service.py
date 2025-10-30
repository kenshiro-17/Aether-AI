import sys
import io
import contextlib
import multiprocessing
import time
import traceback
import ast

class SecurityError(Exception):
    pass

class SafeVisitor(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in ['os', 'sys', 'subprocess', 'shutil', 'socket', 'requests', 'urllib']:
                raise SecurityError(f"Importing '{alias.name}' is forbidden.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in ['os', 'sys', 'subprocess', 'shutil', 'socket', 'requests', 'urllib']:
            raise SecurityError(f"Importing from '{node.module}' is forbidden.")
        self.generic_visit(node)

class ExecutionService:
    def __init__(self):
        self.timeout = 5  # 5 seconds execution limit

    def validate_code(self, code: str):
        """Perform static analysis to block dangerous imports."""
        try:
            tree = ast.parse(code)
            visitor = SafeVisitor()
            visitor.visit(tree)
        except SecurityError as e:
            return str(e)
        except Exception as e:
            return f"Syntax Error: {e}"
        return None

    def execute_code(self, code: str) -> dict:
        """
        Executes Python code in a separate process with time limit.
        Returns {"status": "success"|"error", "output": str, "error": str}
        """
        # 1. Static Security Check
        security_error = self.validate_code(code)
        if security_error:
             return {"status": "error", "output": "", "error": f"Security Violation: {security_error}"}

        # Create a queue to get results from the process
        queue = multiprocessing.Queue()
        
        # Run in a separate process for isolation and timeout management
        process = multiprocessing.Process(target=self._run_isolated, args=(code, queue))
        process.start()
        
        process.join(self.timeout)
        
        if process.is_alive():
            process.terminate()
            process.join()
            return {"status": "error", "output": "", "error": "TimeoutError: Code execution exceeded 5 seconds."}
            
        if not queue.empty():
            return queue.get()
        else:
            return {"status": "error", "output": "", "error": "Process crashed without returning result."}

    def _run_isolated(self, code: str, queue: multiprocessing.Queue):
        """Internal function running inside the separate process."""
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            # Redirect stdout/stderr
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                # Execute the code
                exec_globals = {}
                exec(code, exec_globals)
            
            queue.put({
                "status": "success",
                "output": output_buffer.getvalue(),
                "error": error_buffer.getvalue()
            })
            
        except Exception:
            # Capture tracebacks
            queue.put({
                "status": "error",
                "output": output_buffer.getvalue(),
                "error": traceback.format_exc()
            })
            
execution_service = ExecutionService()
