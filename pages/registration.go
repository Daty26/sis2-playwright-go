package pages

import (
	"sis2/data"

	"github.com/mxschmitt/playwright-go"
)

type RegistrationPage struct {
	page playwright.Page
}

func NewRegisterPage(page playwright.Page) *RegistrationPage {
	return &RegistrationPage{page: page}
}

func (p *RegistrationPage) Open() error {
	_, err := p.page.Goto("https://practicesoftwaretesting.com/auth/register")
	return err
}
func (p *RegistrationPage) Registration(customer data.Customer) error {
	fields := []struct {
		testID string
		value  string
	}{
		{"first-name", customer.FirstName},
		{"last-name", customer.LastName},
		{"dob", customer.DateOfBirth},
		{"postal_code", customer.PostalCode},
		{"house_number", customer.HouseNumber},
		{"street", customer.Street},
		{"city", customer.City},
		{"state", customer.State},
		{"phone", customer.Phone},
		{"email", customer.Email},
		{"password", customer.Password},
	}

	for _, field := range fields {
		if err := p.page.GetByTestId(field.testID).Fill(field.value); err != nil {
			return err
		}
	}

	labels := []string{customer.CountryLabel}
	_, err := p.page.GetByTestId("country").SelectOption(
		playwright.SelectOptionValues{
			Labels: &labels,
		},
	)
	if err != nil {
		return err
	}
	return p.page.GetByTestId("register-submit").Click()
}
func (p *RegistrationPage) ExpectRedirectToLogin() error {
	assert := playwright.NewPlaywrightAssertions()
	return assert.Page(p.page).ToHaveURL("https://practicesoftwaretesting.com/auth/login")
}
