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
		appURL("/"),
	)
	return err
}

func (p *CatalogPage) OpenProduct(name string) error {
	if err := p.page.GetByTestId("search-query").Fill(name); err != nil {
		return err
	}
	if err := p.page.GetByTestId("search-submit").Click(); err != nil {
		return err
	}
	return p.page.GetByRole(
		*playwright.AriaRoleHeading,
		playwright.PageGetByRoleOptions{
			Name:  name,
			Exact: playwright.Bool(true),
		},
	).Click()
}
