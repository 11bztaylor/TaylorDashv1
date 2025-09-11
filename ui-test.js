const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function runComprehensiveUITests() {
  console.log('🚀 Starting comprehensive UI testing for TaylorDash...');
  
  const browser = await chromium.launch({ 
    headless: true, // Set to true for server environment
    args: ['--no-sandbox', '--disable-dev-shm-usage'] // Additional args for server environment
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  // Create screenshots directory
  const screenshotDir = path.join(__dirname, 'test-screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir);
  }
  
  const testResults = {
    passed: [],
    failed: [],
    screenshots: []
  };

  try {
    console.log('📍 Test 1: Application Access & Loading');
    
    // Navigate to the application
    console.log('   🔗 Navigating to http://localhost:5174/');
    await page.goto('http://localhost:5174/');
    
    // Wait for the page to load and take initial screenshot
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: path.join(screenshotDir, '01-initial-load.png'), fullPage: true });
    testResults.screenshots.push('01-initial-load.png');
    
    // Check for JavaScript errors in console
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Test if page loaded successfully
    const title = await page.title();
    console.log(`   ✅ Page title: "${title}"`);
    
    if (title.includes('TaylorDash') || title.includes('Vite')) {
      testResults.passed.push('Application loads successfully');
    } else {
      testResults.failed.push('Application title unexpected: ' + title);
    }
    
    console.log('📍 Test 2: Navigation Testing');
    
    // Test navigation tabs
    const navigationTests = [
      { name: 'Dashboard', selector: 'a[href="/"]', expectedUrl: 'http://localhost:5174/' },
      { name: 'Projects', selector: 'a[href="/projects"]', expectedUrl: 'http://localhost:5174/projects' },
      { name: 'Flow Canvas', selector: 'a[href="/flow"]', expectedUrl: 'http://localhost:5174/flow' },
      { name: 'Settings', selector: 'a[href="/settings"]', expectedUrl: 'http://localhost:5174/settings' }
    ];
    
    for (const navTest of navigationTests) {
      try {
        console.log(`   🔗 Testing navigation to ${navTest.name}`);
        
        const navLink = await page.locator(navTest.selector).first();
        if (await navLink.isVisible()) {
          await navLink.click();
          await page.waitForURL(navTest.expectedUrl, { timeout: 5000 });
          await page.waitForLoadState('networkidle');
          
          // Take screenshot of each page
          const screenshotName = `02-nav-${navTest.name.toLowerCase().replace(' ', '-')}.png`;
          await page.screenshot({ path: path.join(screenshotDir, screenshotName), fullPage: true });
          testResults.screenshots.push(screenshotName);
          
          // Check if page has actual content vs placeholder
          const pageContent = await page.textContent('body');
          const hasPlaceholder = pageContent.includes('coming soon') || pageContent.includes('placeholder') || pageContent.includes('TODO');
          
          if (hasPlaceholder) {
            testResults.failed.push(`${navTest.name} page shows placeholder content`);
          } else {
            testResults.passed.push(`${navTest.name} navigation works with real content`);
          }
          
          console.log(`   ✅ ${navTest.name} navigation successful`);
        } else {
          testResults.failed.push(`${navTest.name} navigation link not found or not visible`);
        }
      } catch (error) {
        console.log(`   ❌ ${navTest.name} navigation failed: ${error.message}`);
        testResults.failed.push(`${navTest.name} navigation failed: ${error.message}`);
      }
    }
    
    console.log('📍 Test 3: Critical "New Project" Button Test');
    
    // Navigate to Projects page specifically
    await page.goto('http://localhost:5174/projects');
    await page.waitForLoadState('networkidle');
    
    // Look for New Project button with various possible selectors
    const projectButtonSelectors = [
      'button:has-text("New Project")',
      'button:has-text("Create Project")', 
      'button:has-text("Add Project")',
      '[data-testid="new-project"]',
      '.new-project-btn',
      'button[aria-label*="project"]'
    ];
    
    let newProjectButton = null;
    let buttonFound = false;
    
    for (const selector of projectButtonSelectors) {
      try {
        newProjectButton = page.locator(selector).first();
        if (await newProjectButton.isVisible({ timeout: 1000 })) {
          buttonFound = true;
          console.log(`   🔘 Found "New Project" button with selector: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    if (buttonFound) {
      // Test button click behavior
      console.log('   🖱️  Clicking New Project button...');
      
      // Set up network monitoring
      const networkRequests = [];
      page.on('request', request => {
        networkRequests.push({
          url: request.url(),
          method: request.method(),
          postData: request.postData()
        });
      });
      
      // Click the button
      await newProjectButton.click();
      await page.waitForTimeout(2000); // Wait for any potential modal or action
      
      // Take screenshot after click
      await page.screenshot({ path: path.join(screenshotDir, '03-new-project-clicked.png'), fullPage: true });
      testResults.screenshots.push('03-new-project-clicked.png');
      
      // Check if modal/form appeared
      const modalSelectors = [
        '.modal',
        '[role="dialog"]',
        '.project-form',
        '.overlay',
        '.popup'
      ];
      
      let modalFound = false;
      for (const modalSelector of modalSelectors) {
        const modal = page.locator(modalSelector);
        if (await modal.isVisible()) {
          modalFound = true;
          console.log(`   ✅ Modal/form appeared with selector: ${modalSelector}`);
          testResults.passed.push('New Project button opens modal/form');
          
          // Test form interaction if found
          await page.screenshot({ path: path.join(screenshotDir, '04-project-modal.png'), fullPage: true });
          testResults.screenshots.push('04-project-modal.png');
          break;
        }
      }
      
      if (!modalFound) {
        // Check if URL changed or page content changed
        const currentUrl = page.url();
        const pageContent = await page.textContent('body');
        
        if (currentUrl !== 'http://localhost:5174/projects') {
          testResults.passed.push(`New Project button navigated to: ${currentUrl}`);
        } else if (networkRequests.length > 0) {
          testResults.passed.push(`New Project button triggered network requests: ${networkRequests.length}`);
          console.log('   📡 Network requests made:', networkRequests);
        } else {
          testResults.failed.push('New Project button appears to do nothing - no modal, navigation, or network requests');
          console.log('   ❌ New Project button appears non-functional');
        }
      }
    } else {
      testResults.failed.push('New Project button not found on Projects page');
      console.log('   ❌ New Project button not found');
    }
    
    console.log('📍 Test 4: Interactive Elements Testing');
    
    // Test various interactive elements across pages
    const pages = [
      'http://localhost:5174/',
      'http://localhost:5174/projects', 
      'http://localhost:5174/flow',
      'http://localhost:5174/settings'
    ];
    
    for (const pageUrl of pages) {
      console.log(`   🔍 Testing interactive elements on ${pageUrl}`);
      await page.goto(pageUrl);
      await page.waitForLoadState('networkidle');
      
      // Find all buttons and test them
      const buttons = await page.locator('button').all();
      console.log(`   Found ${buttons.length} buttons`);
      
      for (let i = 0; i < Math.min(buttons.length, 5); i++) { // Test max 5 buttons per page
        const button = buttons[i];
        try {
          const buttonText = await button.textContent();
          if (buttonText && buttonText.trim()) {
            console.log(`   🖱️  Testing button: "${buttonText.trim()}"`);
            await button.click({ timeout: 2000 });
            await page.waitForTimeout(1000);
            testResults.passed.push(`Button "${buttonText.trim()}" is clickable`);
          }
        } catch (error) {
          // Button might not be clickable or visible
        }
      }
    }
    
    console.log('📍 Test 5: Plugin System Testing');
    
    // Test plugin route
    try {
      console.log('   🔌 Testing /plugins/midnight-hud route');
      await page.goto('http://localhost:5174/plugins/midnight-hud');
      await page.waitForLoadState('networkidle');
      
      const statusCode = await page.evaluate(() => {
        return fetch(window.location.href).then(r => r.status);
      });
      
      if (statusCode === 404) {
        testResults.failed.push('Plugin route returns 404');
      } else {
        // Take screenshot of plugin page
        await page.screenshot({ path: path.join(screenshotDir, '05-plugin-page.png'), fullPage: true });
        testResults.screenshots.push('05-plugin-page.png');
        
        // Check for iframe or plugin content
        const iframe = await page.locator('iframe').first();
        if (await iframe.isVisible()) {
          testResults.passed.push('Plugin page contains iframe - plugin system functional');
        } else {
          const pageContent = await page.textContent('body');
          if (pageContent.includes('plugin') || pageContent.includes('midnight')) {
            testResults.passed.push('Plugin page loads with content');
          } else {
            testResults.failed.push('Plugin page loads but no clear plugin content found');
          }
        }
      }
    } catch (error) {
      testResults.failed.push(`Plugin route test failed: ${error.message}`);
    }
    
    console.log('📍 Test 6: Real-time Connectivity Testing');
    
    // Look for connection status indicators
    await page.goto('http://localhost:5174/');
    await page.waitForLoadState('networkidle');
    
    const connectionIndicators = [
      '.connection-status',
      '.status-indicator',
      '.online',
      '.offline',
      '[data-testid="connection"]'
    ];
    
    let connectionStatusFound = false;
    for (const indicator of connectionIndicators) {
      const element = page.locator(indicator);
      if (await element.isVisible()) {
        connectionStatusFound = true;
        const statusText = await element.textContent();
        testResults.passed.push(`Connection status indicator found: ${statusText}`);
        break;
      }
    }
    
    if (!connectionStatusFound) {
      testResults.failed.push('No connection status indicator found');
    }
    
    console.log('📍 Test 7: Console Errors Check');
    
    if (consoleErrors.length > 0) {
      testResults.failed.push(`Console errors found: ${consoleErrors.join(', ')}`);
    } else {
      testResults.passed.push('No console errors detected');
    }
    
  } catch (error) {
    testResults.failed.push(`Critical test failure: ${error.message}`);
    console.error('❌ Critical error during testing:', error);
  } finally {
    await browser.close();
  }
  
  // Generate comprehensive report
  console.log('\n' + '='.repeat(80));
  console.log('📊 COMPREHENSIVE UI TEST REPORT');
  console.log('='.repeat(80));
  
  console.log(`\n✅ PASSED TESTS (${testResults.passed.length}):`);
  testResults.passed.forEach((test, index) => {
    console.log(`   ${index + 1}. ${test}`);
  });
  
  console.log(`\n❌ FAILED TESTS (${testResults.failed.length}):`);
  testResults.failed.forEach((test, index) => {
    console.log(`   ${index + 1}. ${test}`);
  });
  
  console.log(`\n📸 SCREENSHOTS CAPTURED (${testResults.screenshots.length}):`);
  testResults.screenshots.forEach((screenshot, index) => {
    console.log(`   ${index + 1}. ${path.join(screenshotDir, screenshot)}`);
  });
  
  const overallStatus = testResults.failed.length === 0 ? '✅ ALL TESTS PASSED' : '❌ TESTS FAILED';
  console.log(`\n${overallStatus}`);
  console.log(`Total: ${testResults.passed.length} passed, ${testResults.failed.length} failed`);
  
  // Write detailed report to file
  const reportPath = path.join(__dirname, 'ui-test-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));
  console.log(`\n📋 Detailed report saved to: ${reportPath}`);
  
  return testResults;
}

// Check if Playwright is available and run tests
(async () => {
  try {
    await runComprehensiveUITests();
  } catch (error) {
    if (error.message.includes('Cannot find module')) {
      console.log('❌ Playwright not installed. Installing now...');
      console.log('Run: npm install -g playwright && playwright install chromium');
    } else {
      console.error('❌ Error running tests:', error.message);
    }
  }
})();