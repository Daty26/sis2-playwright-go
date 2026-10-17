package pages

import (
	"regexp"
	"strconv"
	"strings"

	"github.com/mxschmitt/playwright-go"
)

type ProductPage struct {
	page playwright.Page
}

func NewProductPage(page playwright.Page) *ProductPage {
	return &ProductPage{page: page}
}

func (p *ProductPage) Open(url string) error {
	_, err := p.page.Goto(url)
	return err
}
func (p *ProductPage) ExpectName(expectedName string) error {
	assert := playwright.NewPlaywrightAssertions()

	return assert.Locator(p.page.GetByTestId("product-name")).
		ToHaveText(expectedName)
}
func (p *ProductPage) Name() (string, error) {
	text, err := p.page.GetByTestId("product-name").InnerText()
	if err != nil {
		return "", err
	}

	return strings.TrimSpace(text), nil
}

func (p *ProductPage) Price() (float64, error) {
	price := p.page.GetByTestId("unit-price")
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(price).
		ToHaveText(regexp.MustCompile(`^\d+\.\d{2}$`)); err != nil {
		return 0, err
	}

	text, err := price.InnerText()
	if err != nil {
		return 0, err
	}

	return strconv.ParseFloat(strings.TrimSpace(text), 64)
}

func (p *ProductPage) AddToCart(quantity int) error {
	value := strconv.Itoa(quantity)

	if err := p.page.GetByTestId("quantity").Fill(value); err != nil {
		return err
	}

	if err := p.page.GetByTestId("add-to-cart").Click(); err != nil {
		return err
	}

	assert := playwright.NewPlaywrightAssertions()
	return assert.Locator(p.page.GetByTestId("cart-quantity")).
		ToHaveText(value)
}
