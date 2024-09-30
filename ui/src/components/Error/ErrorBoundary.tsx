import { ReactNode, Component, ErrorInfo } from 'react';

type Props = {
  children?: ReactNode;
  errorContents: ReactNode;
};
type State = {
  hasError: boolean;
};
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error({ error, errorInfo });
  }

  render() {
    return this.state.hasError ? this.props.errorContents : this.props.children;
  }
}

export { ErrorBoundary };
