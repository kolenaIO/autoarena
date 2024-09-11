import { Code, Group, Loader, Text } from '@mantine/core';
import { IconCheck, IconX } from '@tabler/icons-react';
import { useCanAccessJudgeType } from '../../hooks/useCanAccessJudgeType.ts';
import { useUrlState } from '../../hooks/useUrlState.ts';
import { JudgeType, judgeTypeToApiKeyName, judgeTypeToHumanReadableName } from './types.ts';

type Props = {
  judgeType: JudgeType;
};
export function CanAccessJudgeStatusIndicator({ judgeType }: Props) {
  const { projectSlug = '' } = useUrlState();
  const { data: canAccess, isLoading } = useCanAccessJudgeType({ projectSlug, judgeType });
  const judgeTypeName = judgeTypeToHumanReadableName(judgeType);
  const apiKeyName = judgeTypeToApiKeyName(judgeType);
  const iconProps = { size: 20, style: { flexShrink: 0 } };
  return (
    <Group gap="sm" wrap="nowrap">
      {isLoading ? (
        <Loader color="gray" {...iconProps} />
      ) : canAccess ? (
        <IconCheck color="green" {...iconProps} />
      ) : (
        <IconX color="red" {...iconProps} />
      )}
      {isLoading ? (
        <Text c="dimmed" fs="italic" size="sm">
          Checking ability to access {judgeTypeName} API...
        </Text>
      ) : canAccess ? (
        <Text size="sm">
          Able to access {judgeTypeName} API
          {apiKeyName != null ? (
            <>
              {' '}
              using <Code>{apiKeyName}</Code>
            </>
          ) : (
            ''
          )}
        </Text>
      ) : (
        <Text size="sm">
          Unable to access {judgeTypeName} API.{' '}
          {apiKeyName != null ? (
            <>
              Ensure that you have the <Code>{apiKeyName}</Code> variable set in the environment running AutoArena.
            </>
          ) : (
            `Ensure that you have the relevant configuration for the ${judgeTypeName} \
API in the environment running AutoArena.`
          )}
        </Text>
      )}
    </Group>
  );
}
