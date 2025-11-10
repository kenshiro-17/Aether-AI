import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-black text-[#00fff2] p-8 font-mono flex flex-col items-center justify-center">
          <h1 className="text-2xl font-bold mb-4">SYSTEM_FAILURE // CRITICAL ERROR</h1>
          <div className="border border-red-500 p-4 rounded bg-red-900/20 max-w-2xl w-full overflow-auto">
            <p className="text-red-400 mb-2">Error detected in neural link:</p>
            <pre className="text-xs text-red-300 whitespace-pre-wrap">
              {this.state.error?.toString()}
            </pre>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="mt-8 px-6 py-2 border border-[#00fff2] hover:bg-[#00fff2]/20 transition-all uppercase tracking-widest"
          >
            Reboot System
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
