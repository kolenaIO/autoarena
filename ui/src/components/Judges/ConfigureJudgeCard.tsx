import { Card, Divider, Group, Image, Stack, Text, UnstyledButton } from '@mantine/core';
import { ReactNode } from 'react';
import { JudgeType, judgeTypeIconComponent, judgeTypeToCoverImageUrl, judgeTypeToHumanReadableName } from './types.ts';
import styles from './ConfigureJudgeCard.module.css';

type Props = {
  judgeType: JudgeType;
  description: ReactNode;
  onClick: () => void;
};
export function ConfigureJudgeCard({ judgeType, description, onClick }: Props) {
  const IconComponent = judgeTypeIconComponent(judgeType);
  const imageUrl = judgeTypeToCoverImageUrl(judgeType);
  return (
    <UnstyledButton onClick={onClick}>
      <Card withBorder h="100%" className={styles.ConfigureJudgeCard}>
        {imageUrl != null && (
          <Card.Section>
            <Image src={imageUrl} alt={judgeTypeToHumanReadableName(judgeType)} height={120} />
          </Card.Section>
        )}
        <Card.Section h="100%">
          <Divider />
          <Group wrap="nowrap" p="md" align="center" h="100%">
            <IconComponent size={24} color="var(--mantine-color-gray-8)" style={{ flexShrink: 0 }} />
            <Stack gap={0}>
              <Text>{judgeTypeToHumanReadableName(judgeType)}</Text>
              <Text size="xs" c="dimmed">
                {description}
              </Text>
            </Stack>
          </Group>
        </Card.Section>
      </Card>
    </UnstyledButton>
  );
}
