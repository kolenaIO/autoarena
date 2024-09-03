import { rankBy } from './utils';

describe('rankBy', () => {
  type Obj = { name: string; value: number };
  const objA: Obj = { name: 'objA', value: 1 };
  const objB: Obj = { name: 'objB', value: 1 };
  const objC: Obj = { name: 'objC', value: 10 };
  const objs = [objA, objB, objC];

  function withRank(o: Obj, rank: number) {
    return { ...o, rank };
  }

  it.each([
    ['name', undefined, [withRank(objA, 1), withRank(objB, 2), withRank(objC, 3)]],
    ['name', 'desc', [withRank(objC, 1), withRank(objB, 2), withRank(objA, 3)]],
    ['value', undefined, [withRank(objA, 1), withRank(objB, 1), withRank(objC, 3)]],
    ['value', 'asc', [withRank(objA, 1), withRank(objB, 1), withRank(objC, 3)]],
    ['value', 'desc', [withRank(objC, 1), withRank(objB, 2), withRank(objA, 2)]],
  ] as [keyof Obj, 'asc' | 'desc' | undefined, ReturnType<typeof rankBy>][])(
    "properly sorts and ranks by field '%s' in desired direction '%s'",
    (key, direction, expected) => {
      expect(rankBy(key, objs, direction)).toEqual(expected);
    }
  );
});
