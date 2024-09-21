import { Anchor, Group, Menu, Stack, Text, Tooltip } from '@mantine/core';
import {
  IconBeta,
  IconBrandGithub,
  IconBrandSlack,
  IconBug,
  IconHome,
  IconLogout,
  IconStack2Filled,
} from '@tabler/icons-react';
import { useAuth0 } from '@auth0/auth0-react';
import { Link } from 'react-router-dom';
import { useContext } from 'react';
import { AppConfigContext, ExternalUrls, ROUTES } from '../lib';

export function MainMenu() {
  const { user, logout } = useAuth0();
  const { mode } = useContext(AppConfigContext);
  const isCloudMode = mode === 'cloud';

  const iconProps = { size: 20, color: 'var(--mantine-color-kolena-light-color)' };
  return (
    <Menu>
      <Menu.Target>
        <Group gap={4}>
          <IconStack2Filled {...iconProps} />
          <Text fw="bold" c="black">
            AutoArena
          </Text>
          <Tooltip label="Beta Release" fz="xs">
            <IconBeta size={14} color="var(--mantine-color-ice-8)" />
          </Tooltip>
        </Group>
      </Menu.Target>

      <Menu.Dropdown>
        <Link to={ROUTES.home()} style={{ textDecoration: 'none' }}>
          <Menu.Item leftSection={<IconHome {...iconProps} />}>Home</Menu.Item>
        </Link>
        <Anchor href={ExternalUrls.AUTOARENA_GITHUB} underline="never" target="_blank">
          <Menu.Item leftSection={<IconBrandGithub {...iconProps} />}>Repository</Menu.Item>
        </Anchor>
        <Anchor href={ExternalUrls.AUTOARENA_GITHUB_ISSUES} underline="never" target="_blank">
          <Menu.Item leftSection={<IconBug {...iconProps} />}>Report a Bug</Menu.Item>
        </Anchor>
        <Anchor href={ExternalUrls.AUTOARENA_SLACK_COMMUNITY} underline="never" target="_blank">
          <Menu.Item leftSection={<IconBrandSlack {...iconProps} />}>Slack Community</Menu.Item>
        </Anchor>
        {isCloudMode && (
          <>
            <Menu.Divider />
            <Menu.Item
              leftSection={<IconLogout {...iconProps} />}
              onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            >
              <Stack gap={0}>
                <Text inherit>Sign Out</Text>
                {user != null && (
                  <Text size="xs" c="dimmed">
                    {user.email}
                  </Text>
                )}
              </Stack>
            </Menu.Item>
          </>
        )}
      </Menu.Dropdown>
    </Menu>
  );
}
