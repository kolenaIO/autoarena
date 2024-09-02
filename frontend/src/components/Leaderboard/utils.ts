import { prop, sortBy } from 'ramda';

export function rankBy<T extends object>(
  key: keyof T,
  objs: Array<T>,
  direction: 'asc' | 'desc' = 'asc'
): Array<T & { rank: number }> {
  const sortedByKey = sortBy(prop(key))(objs); // note that this doesn't play so nicely with nulls
  const sortedByKeyWithDirection = direction === 'asc' ? sortedByKey : sortedByKey.reverse();
  return sortedByKeyWithDirection.reduce<{ objs: (T & { rank: number })[]; prev: T | null; rank: number; run: number }>(
    ({ objs, prev, rank, run }, obj) => {
      if (prev == null) {
        return { objs: [{ ...obj, rank: 1 }], prev: obj, rank: 1, run: 0 };
      }
      const isSame = obj[key] === prev[key];
      const newRank = rank + (isSame ? 0 : 1 + run);
      return { objs: [...objs, { ...obj, rank: newRank }], prev: obj, rank: newRank, run: isSame ? run + 1 : 0 };
    },
    { objs: [], prev: null, rank: 1, run: 0 }
  ).objs;
}
