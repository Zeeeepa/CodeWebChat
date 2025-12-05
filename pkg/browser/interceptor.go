package browser

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"sync"

	"github.com/playwright-community/playwright-go"
)

// NetworkInterceptor handles network traffic interception
type NetworkInterceptor struct {
	mu              sync.RWMutex
	capturedData    map[string][]byte
	sseStreams      map[string]chan SSEEvent
	wsMessages      map[string]chan WebSocketMessage
	enabled         bool
	capturePatterns []string
}

// SSEEvent represents a Server-Sent Event
type SSEEvent struct {
	Data      string
	Event     string
	ID        string
	Retry     int
	Timestamp int64
}

// WebSocketMessage represents a WebSocket message
type WebSocketMessage struct {
	Direction string // "send" or "receive"
	Data      string
	Binary    bool
	Timestamp int64
}

// NewNetworkInterceptor creates a new network interceptor
func NewNetworkInterceptor() *NetworkInterceptor {
	return &NetworkInterceptor{
		capturedData:    make(map[string][]byte),
		sseStreams:      make(map[string]chan SSEEvent),
		wsMessages:      make(map[string]chan WebSocketMessage),
		enabled:         true,
		capturePatterns: []string{},
	}
}

// SetupInterception configures network interception on a browser context
func (ni *NetworkInterceptor) SetupInterception(ctx context.Context, browserContext playwright.BrowserContext) error {
	// Intercept HTTP/HTTPS requests and responses
	err := browserContext.Route("**/*", func(route playwright.Route) {
		request := route.Request()
		
		// Log the request
		log.Printf("[Interceptor] Request: %s %s", request.Method(), request.URL())
		
		// Fetch the actual response
		response, err := route.Fetch()
		if err != nil {
			log.Printf("[Interceptor] Error fetching response: %v", err)
			route.Abort("failed")
			return
		}
		
		// Capture response body if it matches our patterns
		if ni.shouldCapture(request.URL()) {
			body, err := response.Body()
			if err != nil {
				log.Printf("[Interceptor] Error reading response body: %v", err)
			} else {
				ni.mu.Lock()
				ni.capturedData[request.URL()] = body
				ni.mu.Unlock()
				
				log.Printf("[Interceptor] Captured %d bytes from %s", len(body), request.URL())
			}
		}
		
		// Fulfill the route with the actual response
		err = route.Fulfill(playwright.RouteFulfillOptions{
			Response: response,
		})
		if err != nil {
			log.Printf("[Interceptor] Error fulfilling route: %v", err)
		}
	})
	
	if err != nil {
		return fmt.Errorf("failed to setup route interception: %w", err)
	}
	
	log.Println("[Interceptor] Network interception enabled")
	return nil
}

// shouldCapture determines if a URL should have its response captured
func (ni *NetworkInterceptor) shouldCapture(url string) bool {
	ni.mu.RLock()
	defer ni.mu.RUnlock()
	
	// If no patterns specified, capture everything
	if len(ni.capturePatterns) == 0 {
		return true
	}
	
	// Check if URL matches any pattern
	for _, pattern := range ni.capturePatterns {
		// Simple substring match for now
		// TODO: Use proper regex or glob patterns
		if contains(url, pattern) {
			return true
		}
	}
	
	return false
}

// GetCapturedData retrieves captured response data for a URL
func (ni *NetworkInterceptor) GetCapturedData(url string) ([]byte, bool) {
	ni.mu.RLock()
	defer ni.mu.RUnlock()
	
	data, exists := ni.capturedData[url]
	return data, exists
}

// GetAllCapturedData returns all captured data
func (ni *NetworkInterceptor) GetAllCapturedData() map[string][]byte {
	ni.mu.RLock()
	defer ni.mu.RUnlock()
	
	// Return a copy to avoid race conditions
	result := make(map[string][]byte)
	for k, v := range ni.capturedData {
		result[k] = v
	}
	
	return result
}

// ClearCapturedData clears all captured data
func (ni *NetworkInterceptor) ClearCapturedData() {
	ni.mu.Lock()
	defer ni.mu.Unlock()
	
	ni.capturedData = make(map[string][]byte)
	log.Println("[Interceptor] Cleared all captured data")
}

// AddCapturePattern adds a URL pattern to capture
func (ni *NetworkInterceptor) AddCapturePattern(pattern string) {
	ni.mu.Lock()
	defer ni.mu.Unlock()
	
	ni.capturePatterns = append(ni.capturePatterns, pattern)
	log.Printf("[Interceptor] Added capture pattern: %s", pattern)
}

// PrintCapturedDataSummary prints a summary of captured data
func (ni *NetworkInterceptor) PrintCapturedDataSummary() {
	ni.mu.RLock()
	defer ni.mu.RUnlock()
	
	fmt.Printf("\n=== Captured Data Summary ===\n")
	fmt.Printf("Total URLs captured: %d\n\n", len(ni.capturedData))
	
	for url, data := range ni.capturedData {
		fmt.Printf("URL: %s\n", url)
		fmt.Printf("Size: %d bytes\n", len(data))
		
		// Try to parse as JSON for pretty printing
		var jsonData interface{}
		if err := json.Unmarshal(data, &jsonData); err == nil {
			prettyJSON, _ := json.MarshalIndent(jsonData, "", "  ")
			fmt.Printf("Content (JSON):\n%s\n\n", string(prettyJSON))
		} else {
			// Not JSON, print first 200 chars
			preview := string(data)
			if len(preview) > 200 {
				preview = preview[:200] + "..."
			}
			fmt.Printf("Content (text):\n%s\n\n", preview)
		}
	}
	
	fmt.Printf("============================\n\n")
}

// Helper function
func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > len(substr) && containsSubstring(s, substr))
}

func containsSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

