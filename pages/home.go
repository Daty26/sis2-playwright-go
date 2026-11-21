package pages

import (
	"os"
	"regexp"
	"strings"

	"github.com/mxschmitt/playwright-go"
)

type HomePage struct {
	page playwright.Page
}

func NewHomePage(page playwright.Page) *HomePage {
	return &HomePage{page: page}
}
func (h *HomePage) Open() error {
	_, err := h.page.Goto(appURL("/"))
	return err
}

func (h *HomePage) ExpectLoaded() error {
	assert := playwright.NewPlaywrightAssertions()
	err := assert.Page(h.page).ToHaveTitle(
		regexp.MustCompile("Practice Software Testing"),
	)
	return err
}

func appURL(path string) string {
	baseURL := os.Getenv("BASE_URL")
	if baseURL == "" {
		baseURL = "https://practicesoftwaretesting.com"
	}
	return strings.TrimRight(baseURL, "/") + "/" + strings.TrimLeft(path, "/")
}
