import { Model } from '../../hooks';

export type RankedModel = Model & {
  rank: number;
  globalLo: number;
  globalHi: number;
};
