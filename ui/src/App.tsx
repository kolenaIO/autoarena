import '@mantine/core/styles.layer.css';
import 'mantine-datatable/styles.layer.css';
import '@mantine/notifications/styles.css';
import '@mantine/charts/styles.css';
import './global.css';
import { Accordion, Button, createTheme, MantineProvider, Modal, Popover, Tooltip } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Notifications } from '@mantine/notifications';
import { PageNotFound, Page, Tab, UnhandledError } from './components';
import { AppConfigContext, DEFAULT_APP_CONFIG } from './lib';

const theme = createTheme({
  primaryColor: 'kolena',
  focusRing: 'auto',
  defaultRadius: 'md',
  cursorType: 'pointer',
  components: {
    Modal: Modal.extend({ defaultProps: { transitionProps: { transition: 'fade', duration: 100 } } }),
    Tooltip: Tooltip.extend({ defaultProps: { openDelay: 200 } }),
    Popover: Popover.extend({ defaultProps: { shadow: 'sm' } }),
    Accordion: Accordion.extend({ defaultProps: { bg: 'white' } }),
    Button: Button.extend({ defaultProps: { style: { backdropFilter: 'blur(4px)' } } }),
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

const errorElement = <UnhandledError />;
const router = createBrowserRouter([
  { path: `/`, element: <Page tab={Tab.LEADERBOARD} />, errorElement },
  { path: `/project/:projectSlug`, element: <Page tab={Tab.LEADERBOARD} />, errorElement },
  { path: `/project/:projectSlug/compare`, element: <Page tab={Tab.COMPARISON} />, errorElement },
  { path: `/project/:projectSlug/judges`, element: <Page tab={Tab.JUDGES} />, errorElement },
  { path: '*', element: <PageNotFound />, errorElement },
]);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider forceColorScheme="light" defaultColorScheme="light" theme={theme}>
        <AppConfigContext.Provider value={DEFAULT_APP_CONFIG}>
          <Notifications />
          <RouterProvider router={router} />
        </AppConfigContext.Provider>
      </MantineProvider>
    </QueryClientProvider>
  );
}

export default App;
