// import '@mantine/core/styles.css';
import '@mantine/core/styles.layer.css';
import 'mantine-datatable/styles.layer.css';
import '@mantine/notifications/styles.css';
import './App.module.css';
import { createTheme, MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Notifications } from '@mantine/notifications';
import { Page, TAB_COMPARISON, TAB_JUDGES, TAB_LEADERBOARD, TAB_STATISTICS } from './components/Page.tsx';
import { PageNotFound } from './components/PageNotFound.tsx';

const theme = createTheme({
  primaryColor: 'kolena',
  focusRing: 'auto',
  defaultRadius: 'md',
  cursorType: 'pointer',
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
    ice: ['#deffff', '#cafeff', '#99faff', '#64f8ff', '#3df5fe', '#26f4fe', '#09f3ff', '#00d8e4', '#00c1cb', '#00a7b1'],
  },
});

const queryClient = new QueryClient({});

const router = createBrowserRouter([
  { path: '/', element: <Page tab={TAB_LEADERBOARD} /> },
  { path: '/project/:projectId', element: <Page tab={TAB_LEADERBOARD} /> },
  { path: '/project/:projectId/compare', element: <Page tab={TAB_COMPARISON} /> },
  { path: '/project/:projectId/statistics', element: <Page tab={TAB_STATISTICS} /> },
  { path: '/project/:projectId/judges', element: <Page tab={TAB_JUDGES} /> },
  { path: '*', element: <PageNotFound /> },
]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider forceColorScheme="light" defaultColorScheme="light" theme={theme}>
        <Notifications />
        <RouterProvider router={router} />
      </MantineProvider>
    </QueryClientProvider>
  );
}

export default App;
