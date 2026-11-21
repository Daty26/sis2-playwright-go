package pages

import (
	"github.com/mxschmitt/playwright-go"
)

type LoginPage struct {
	page playwright.Page
}

func NewLoginPage(page playwright.Page) *LoginPage {
	return &LoginPage{page: page}
}

func (p *LoginPage) Open() error {
	_, err := p.page.Goto(appURL("/auth/login"))
	return err
}

func (p *LoginPage) SignIn(email, password string) error {
	if err := p.page.GetByTestId("email").Fill(email); err != nil {
		return err
	}
	if err := p.page.GetByTestId("password").Fill(password); err != nil {
		return err
	}
	if err := p.page.GetByTestId("login-submit").Click(); err != nil {
		return err
	}
	return nil
}
func (p *LoginPage) ExpectSignedIn(displayName string) error {
	assert := playwright.NewPlaywrightAssertions()
	if err := assert.Page(p.page).ToHaveURL(appURL("/account")); err != nil {
		return err
	}
	if err := assert.Locator(p.page.GetByTestId("nav-menu")).ToHaveText(displayName); err != nil {
		return err
	}
	return nil
}

func (p *LoginPage) ExpectInvalidCredentials() error {
	assert := playwright.NewPlaywrightAssertions()
	if err := assert.Locator(p.page.GetByText("Invalid email or password")).ToBeVisible(); err != nil {
		return err
	}
	return assert.Page(p.page).ToHaveURL(appURL("/auth/login"))
}
