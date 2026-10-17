package pages

import (
	"regexp"

	"github.com/mxschmitt/playwright-go"
)

type HomePage struct {
	page playwright.Page
}

func NewHomePage(page playwright.Page) *HomePage {
	return &HomePage{page: page}
}
func (h *HomePage) Open() error {
	_, err := h.page.Goto("https://practicesoftwaretesting.com/")
	return err
}
func (h *HomePage) ExpectLoaded() error {
	assert := playwright.NewPlaywrightAssertions()
	err := assert.Page(h.page).ToHaveTitle(
		regexp.MustCompile("Practice Software Testing"),
	)
	return err
}
