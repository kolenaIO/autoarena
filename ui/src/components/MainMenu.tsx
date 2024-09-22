import { Anchor, Group, Menu, Text, Tooltip } from '@mantine/core';
import { IconBeta, IconBrandGithub, IconBrandSlack, IconBug, IconHome, IconStack2Filled } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { ExternalUrls, useAppConfig } from '../lib';
import { useRoutes } from '../hooks';

export function MainMenu() {
  const { menuExtras } = useAppConfig();
  const { appRoutes } = useRoutes();

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
        <Link to={appRoutes.home()} style={{ textDecoration: 'none' }}>
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
        {menuExtras}
      </Menu.Dropdown>
    </Menu>
  );
}
