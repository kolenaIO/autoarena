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
  const diamondSize = height - 6;
  return (
    <div style={{ position: 'relative', minWidth: 200, height }}>
      <div
        style={{
          position: 'absolute',
          background: 'var(--mantine-color-gray-4)',
          left: `calc(${pctLo.toFixed(1)}%)`,
          right: `calc(100% - ${pctHi.toFixed(1)}%)`,
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
          left: `calc(${pct.toFixed(1)}% - ${height / 2}px)`,
          width: diamondSize,
          height: diamondSize,
          transform: 'rotate(45deg)',
          margin: 3,
        }}
      />
    </div>
  );
}
