import { Anchor, Group, Menu, Title, Tooltip, UnstyledButton } from '@mantine/core';
import { IconBeta, IconBrandGithub, IconBrandSlack, IconBug, IconHome, IconStack2Filled } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { ReactNode } from 'react';
import { ExternalUrls, usePropOverrides } from '../lib';
import { useAppRoutes } from '../hooks';

type Props = {
  extraMenuItems?: ReactNode[];
};
export function MainMenu(props: Props) {
  const { extraMenuItems } = usePropOverrides('MainMenu', props);
  const { appRoutes } = useAppRoutes();

  const iconProps = { size: 20, color: 'var(--mantine-color-kolena-light-color)' };
  return (
    <Menu>
      <Menu.Target>
        <UnstyledButton>
          <Group gap={4}>
            <IconStack2Filled {...iconProps} />
            <Title order={5} c="black">
              AutoArena
            </Title>
            <Tooltip label="Beta Release" fz="xs">
              <IconBeta size={14} color="var(--mantine-color-ice-8)" />
            </Tooltip>
          </Group>
        </UnstyledButton>
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
        {extraMenuItems}
      </Menu.Dropdown>
    </Menu>
  );
}
