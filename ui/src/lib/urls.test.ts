/*
 * @jest-environment node // required to get fetch working properly
 */

import { ExternalUrls } from './urls';

describe('external link integrity', () => {
  const externalLinks: string[] = Object.values(ExternalUrls);

  test.each(externalLinks)('%s', async url => {
    expect((await fetch(url)).status).toEqual(200);
  });
});
