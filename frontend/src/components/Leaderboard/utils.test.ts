import { rankBy } from './utils';

describe('rankBy', () => {
  type Obj = { a: number; b: number };
  const objA: Obj = { a: 1, b: 3 };
  const objB: Obj = { a: 1, b: 1 };
  const objC: Obj = { a: 10, b: -10 };
  it.each([
    [
      'a',
      [objA, objB, objC],
      [
        { ...objA, rank: 1 },
        { ...objB, rank: 1 },
        { ...objC, rank: 3 },
      ],
    ],
    [
      'b',
      [objA, objB, objC],
      [
        { ...objC, rank: 1 },
        { ...objB, rank: 2 },
        { ...objA, rank: 3 },
      ],
    ],
  ])('properly sorts and ranks by field', (key: keyof Obj, objs: Obj[], expected: ReturnType<typeof rankBy>) => {
    expect(rankBy(key, objs)).toEqual(expected);
  });
});
