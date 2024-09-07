import { Model } from '../../hooks/useModels.ts';

export type RankedModel = Model & {
  rank: number;
  globalLo: number;
  globalHi: number;
};
