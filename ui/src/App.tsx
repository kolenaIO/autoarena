import '@mantine/core/styles.layer.css';
import 'mantine-datatable/styles.layer.css';
import '@mantine/notifications/styles.css';
import '@mantine/charts/styles.css';
import './global.css';
import { createTheme, MantineProvider, Modal, Popover, Tooltip } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Notifications } from '@mantine/notifications';
import { Page, TAB_COMPARISON, TAB_JUDGES, TAB_LEADERBOARD } from './components/Page.tsx';
import { PageNotFound } from './components/PageNotFound.tsx';
import { getAppMode } from './hooks/useAppMode.ts';

const theme = createTheme({
  primaryColor: 'kolena',
  focusRing: 'auto',
  defaultRadius: 'md',
  cursorType: 'pointer',
  components: {
    Modal: Modal.extend({ defaultProps: { transitionProps: { transition: 'fade', duration: 100 } } }),
    Tooltip: Tooltip.extend({ defaultProps: { openDelay: 200 } }),
    Popover: Popover.extend({ defaultProps: { shadow: 'sm' } }),
  },
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

const pathPrefix = getAppMode().isCloudMode ? '/:tenant' : '';
const router = createBrowserRouter([
  { path: `${pathPrefix}/`, element: <Page tab={TAB_LEADERBOARD} /> },
  { path: `${pathPrefix}/project/:projectSlug`, element: <Page tab={TAB_LEADERBOARD} /> },
  { path: `${pathPrefix}/project/:projectSlug/compare`, element: <Page tab={TAB_COMPARISON} /> },
  { path: `${pathPrefix}/project/:projectSlug/judges`, element: <Page tab={TAB_JUDGES} /> },
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
