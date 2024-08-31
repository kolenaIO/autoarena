import { Card, Divider, Group, Image, Stack, Text, UnstyledButton } from '@mantine/core';
import { Judge } from '../../hooks/useJudges.ts';
import { judgeTypeIconComponent, judgeTypeToCoverImageUrl, judgeTypeToHumanReadableName } from './types.ts';

type Props = {
  judgeType: Judge['judge_type'];
  description: string;
};
export function ConfigureJudgeCard({ judgeType, description }: Props) {
  const IconComponent = judgeTypeIconComponent(judgeType);
  const imageUrl = judgeTypeToCoverImageUrl(judgeType);
  return (
    <UnstyledButton onClick={() => console.log('configure me!')}>
      <Card withBorder h="100%">
        {imageUrl != null && (
          <Card.Section>
            <Image src={imageUrl} alt={judgeTypeToHumanReadableName(judgeType)} height={120} />
          </Card.Section>
        )}
        <Card.Section h="100%">
          <Divider />
          <Group wrap="nowrap" p="md" align="center" h="100%">
            <IconComponent size={36} color="var(--mantine-color-gray-8)" />
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
