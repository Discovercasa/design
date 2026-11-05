import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: '.',
  testMatch: /.*\.spec\.mjs/,
  timeout: 30000,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'relatorio' }]],
  use: { baseURL: 'http://localhost:4321', trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  webServer: { command: 'node servidor.mjs', url: 'http://localhost:4321/', reuseExistingServer: true },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'telemovel', use: { ...devices['Pixel 7'] } },
  ],
});
