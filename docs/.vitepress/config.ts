import { defineConfig } from 'vitepress';

export default defineConfig({
  title: 'Assets',
  description: 'Documentation for the McGuire Technology, LLC - Assets workspace',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Frontend', link: '/frontend' },
      { text: 'Backend', link: '/backend' },
      { text: 'API', link: '/api' },
      { text: 'Stories', link: '/stories/' },
      { text: 'Changelog', link: '/changelog/' },
    ],
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Frontend', link: '/frontend' },
          { text: 'Backend', link: '/backend' },
          { text: 'API', link: '/api' },
          { text: 'Stories', link: '/stories/' },
        ],
      },
      {
        text: 'Stories',
        items: [
          { text: 'House of Systems', link: '/stories/house_of_systems/' },
        ],
      },
      {
        text: 'Releases',
        items: [
          { text: 'Changelog', link: '/changelog/' },
          { text: '26.6.0', link: '/changelog/26.6.0' },
        ],
      },
    ],
  },
});
