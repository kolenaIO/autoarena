import { Paper } from '@mantine/core';
import { Result } from '../../hooks/useModelResults.ts';

type Props = {
  extra?: Result['extra'];
};
export function ExtraResultData({ extra }: Props) {
  return Object.keys(extra ?? {}).length > 0 ? (
    <Paper fz="sm" withBorder p="sm" flex={1} style={{ overflow: 'auto' }}>
      <ul>
        {Object.entries(extra ?? {}).map(([key, value]) => (
          <li key={key}>
            <b>{key}</b>: {value}
          </li>
        ))}
      </ul>
    </Paper>
  ) : (
    <></>
  );
}
