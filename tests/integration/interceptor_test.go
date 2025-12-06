package integration

import (
	"context"
	"testing"
	"time"

	"github.com/Zeeeepa/webchat-gateway/pkg/browser"
	"github.com/playwright-community/playwright-go"
)

// TestNetworkInterceptionPOC tests basic HTTP response interception
func TestNetworkInterceptionPOC(t *testing.T) {
	// Initialize Playwright
	err := playwright.Install()
	if err != nil {
		t.Fatalf("Failed to install Playwright: %v", err)
	}

	pw, err := playwright.Run()
	if err != nil {
		t.Fatalf("Failed to start Playwright: %v", err)
	}
	defer pw.Stop()

	// Launch browser
	browserInstance, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
		Headless: playwright.Bool(true),
	})
	if err != nil {
		t.Fatalf("Failed to launch browser: %v", err)
	}
	defer browserInstance.Close()

	// Create browser context
	ctx := context.Background()
	browserContext, err := browserInstance.NewContext()
	if err != nil {
		t.Fatalf("Failed to create browser context: %v", err)
	}
	defer browserContext.Close()

	// Create network interceptor
	interceptor := browser.NewNetworkInterceptor()

	// Setup interception
	err = interceptor.SetupInterception(ctx, browserContext)
	if err != nil {
		t.Fatalf("Failed to setup interception: %v", err)
	}

	// Create a page
	page, err := browserContext.NewPage()
	if err != nil {
		t.Fatalf("Failed to create page: %v", err)
	}
	defer page.Close()

	// Navigate to httpbin.org/json (test endpoint)
	t.Log("Navigating to httpbin.org/json...")
	_, err = page.Goto("https://httpbin.org/json", playwright.PageGotoOptions{
		WaitUntil: playwright.WaitUntilStateNetworkidle,
	})
	if err != nil {
		t.Fatalf("Failed to navigate: %v", err)
	}

	// Give it a moment to capture the response
	time.Sleep(2 * time.Second)

	// Print captured data summary
	interceptor.PrintCapturedDataSummary()

	// Verify we captured something
	allData := interceptor.GetAllCapturedData()
	if len(allData) == 0 {
		t.Fatal("Expected to capture some network data, but got none")
	}

	// Look for the JSON endpoint response
	found := false
	for url, data := range allData {
		t.Logf("Captured URL: %s (%d bytes)", url, len(data))
		if containsString(url, "httpbin.org/json") {
			found = true
			t.Logf("✓ Successfully captured httpbin.org/json response!")
			t.Logf("Response size: %d bytes", len(data))
			
			// Verify it's valid data
			if len(data) == 0 {
				t.Error("Captured data is empty")
			}
		}
	}

	if !found {
		t.Error("Did not find httpbin.org/json in captured data")
		t.Log("Available URLs:")
		for url := range allData {
			t.Logf("  - %s", url)
		}
	}
}

// Helper function
func containsString(s, substr string) bool {
	return len(s) >= len(substr) && findSubstring(s, substr) >= 0
}

func findSubstring(s, substr string) int {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return i
		}
	}
	return -1
}

