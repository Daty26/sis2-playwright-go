package pages

import "github.com/mxschmitt/playwright-go"

type PasswordResetPage struct {
	page playwright.Page
}

func NewPasswordResetPage(page playwright.Page) *PasswordResetPage {
	return &PasswordResetPage{page: page}
}

func (p *PasswordResetPage) Open() error {
	_, err := p.page.Goto(
		"https://practicesoftwaretesting.com/auth/forgot-password",
	)
	return err
}

func (p *PasswordResetPage) RequestReset(email string) error {
	if err := p.page.GetByTestId("email").Fill(email); err != nil {
		return err
	}

	return p.page.GetByTestId("forgot-password-submit").Click()
}

func (p *PasswordResetPage) ExpectConfirmation() error {
	alert := p.page.GetByRole(*playwright.AriaRoleAlert)
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(alert).ToBeVisible(); err != nil {
		return err
	}

	return assert.Locator(alert).ToHaveText("page.forgot-password.confirm")
}

func (p *PasswordResetPage) ExpectInvalidEmail() error {
	alert := p.page.GetByRole(*playwright.AriaRoleAlert)
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(alert).ToBeVisible(); err != nil {
		return err
	}

	return assert.Locator(alert).ToHaveText("The selected email is invalid.")
}
