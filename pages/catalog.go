package pages

import "github.com/mxschmitt/playwright-go"

type CatalogPage struct {
	page playwright.Page
}

func NewCatalogPage(page playwright.Page) *CatalogPage {
	return &CatalogPage{page: page}
}

func (p *CatalogPage) Open() error {
	_, err := p.page.Goto(
		"https://practicesoftwaretesting.com/category/hand-tools",
	)
	return err
}

func (p *CatalogPage) OpenProduct(name string) error {
	return p.page.GetByRole(
		*playwright.AriaRoleHeading,
		playwright.PageGetByRoleOptions{
			Name:  name,
			Exact: playwright.Bool(true),
		},
	).Click()
}
