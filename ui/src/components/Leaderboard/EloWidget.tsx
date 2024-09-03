type Props = {
  elo: number;
  qLo: number;
  qHi: number;
  globalLo: number;
  globalHi: number;
};

export function EloWidget({ elo, qLo, qHi, globalLo, globalHi }: Props) {
  const range = globalHi - globalLo;
  const pct = (100 * (elo - globalLo)) / range;
  const pctLo = (100 * (qLo - globalLo)) / range;
  const pctHi = (100 * (qHi - globalLo)) / range;
  const height = 12;
  return (
    <div style={{ position: 'relative', minWidth: 200, height }}>
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-4)',
          left: `calc(${pctLo.toFixed(1)}% - 1px)`,
          right: `calc(100% - ${pctHi.toFixed(1)}% - 1px)`,
          borderRadius: height / 2,
          height: 2,
          marginTop: (height - 2) / 2,
          marginBottom: (height - 2) / 2,
        }}
      />
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-4)',
          left: `calc(${pctLo.toFixed(1)}% - 1px)`,
          borderRadius: 1,
          width: 2,
          height,
        }}
      />
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-4)',
          left: `calc(${pctHi.toFixed(1)}% - 1px)`,
          borderRadius: 1,
          width: 2,
          height,
        }}
      />
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-kolena-8)',
          left: `calc(${pct.toFixed(1)}% - ${(height - 6) / 2}px - 1px)`,
          width: height - 6,
          height: height - 6,
          transform: 'rotate(45deg)',
          margin: 3,
        }}
      />
    </div>
  );
}
