import { Anchor, Group, Menu, Text, Tooltip } from '@mantine/core';
import {
  IconBeta,
  IconBrandGithub,
  IconBrandSlack,
  IconBug,
  IconHome,
  IconLogout,
  IconStack2Filled,
} from '@tabler/icons-react';
import { ExternalUrls } from '../lib/routes.ts';
import { useAppMode } from '../hooks/useAppMode.ts';

export function MainMenu() {
  const iconProps = { size: 20, color: 'var(--mantine-color-kolena-light-color)' };
  const { isCloudMode } = useAppMode();
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
        <Anchor href="/" underline="never">
          <Menu.Item leftSection={<IconHome {...iconProps} />}>Home</Menu.Item>
        </Anchor>
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
            <Anchor underline="never">
              <Menu.Item leftSection={<IconLogout {...iconProps} />}>Log out</Menu.Item>
            </Anchor>
          </>
        )}
      </Menu.Dropdown>
    </Menu>
  );
}
