import { createTheme, MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Home } from './components/Home';
import '@mantine/core/styles.css';

const theme = createTheme({
  primaryColor: 'kolena',
  focusRing: 'auto',
  defaultRadius: 'xl',
  colors: {
    kolena: [
      '#f4eeff',
      '#e3daf7',
      '#c4b1ea',
      '#a485dd',
      '#8861d2',
      '#764acc',
      '#6e3dca',
      '#5d30b3',
      '#522aa1',
      '#46238e',
    ],
    ice: [
      '#deffff',
      '#cafeff',
      '#99faff',
      '#64f8ff',
      '#3df5fe',
      '#26f4fe',
      '#09f3ff',
      '#00d8e4',
      '#00c1cb',
      '#00a7b1',
    ],
  },
});

const queryClient = new QueryClient({});

const router = createBrowserRouter([{ path: '/', element: <Home /> }]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider forceColorScheme="light" defaultColorScheme="light" theme={theme}>
        <RouterProvider router={router} />
      </MantineProvider>
    </QueryClientProvider>
  );
}

export default App;
