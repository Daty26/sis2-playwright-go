package pages

import (
	"fmt"
	"net/url"
	"regexp"
	"strconv"

	"sis2/data"

	"github.com/mxschmitt/playwright-go"
)

type CheckoutPage struct {
	page playwright.Page
}

func NewCheckoutPage(page playwright.Page) *CheckoutPage {
	return &CheckoutPage{page: page}
}

func (p *CheckoutPage) Open() error {
	_, err := p.page.Goto(
		"https://practicesoftwaretesting.com/checkout",
	)
	return err
}

func (p *CheckoutPage) ExpectCart(
	name string,
	quantity int,
	unitPrice float64,
) error {
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(p.page.GetByTestId("product-title")).
		ToHaveCount(1); err != nil {
		return err
	}

	if err := assert.Locator(p.page.GetByTestId("product-title")).
		ToHaveText(name); err != nil {
		return err
	}

	if err := assert.Locator(p.page.GetByTestId("product-quantity")).
		ToHaveValue(strconv.Itoa(quantity)); err != nil {
		return err
	}

	if err := assert.Locator(p.page.GetByTestId("product-price")).
		ToHaveText(fmt.Sprintf("$%.2f", unitPrice)); err != nil {
		return err
	}

	total := unitPrice * float64(quantity)

	return assert.Locator(p.page.GetByTestId("cart-total")).
		ToHaveText(fmt.Sprintf("$%.2f", total))
}

func (p *CheckoutPage) ProceedToBilling() error {
	if err := p.page.GetByTestId("proceed-1").Click(); err != nil {
		return err
	}

	return p.page.GetByTestId("proceed-2").Click()
}

func (p *CheckoutPage) FillBilling(customer data.Customer) error {
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(p.page.GetByTestId("house_number")).
		ToBeVisible(); err != nil {
		return err
	}

	labels := []string{customer.CountryLabel}
	_, err := p.page.GetByTestId("country").SelectOption(
		playwright.SelectOptionValues{Labels: &labels},
	)
	if err != nil {
		return err
	}

	countryCode, err := p.page.GetByTestId("country").InputValue()
	if err != nil {
		return err
	}

	if err := p.page.GetByTestId("postal_code").
		Fill(customer.PostalCode); err != nil {
		return err
	}
	temporaryNumber := "1"
	if customer.HouseNumber == temporaryNumber {
		temporaryNumber = "2"
	}

	for _, houseNumber := range []string{
		temporaryNumber,
		customer.HouseNumber,
	} {
		response, err := p.page.ExpectResponse(
			func(response playwright.Response) bool {
				u, err := url.Parse(response.URL())
				if err != nil {
					return false
				}

				query := u.Query()
				return u.Path == "/postcode-lookup" &&
					query.Get("country") == countryCode &&
					query.Get("postcode") == customer.PostalCode &&
					query.Get("house_number") == houseNumber
			},
			func() error {
				return p.page.GetByTestId("house_number").
					Fill(houseNumber)
			},
		)
		if err != nil {
			return fmt.Errorf("wait for postcode lookup: %w", err)
		}

		if err := response.Finished(); err != nil {
			return err
		}

		if err := assert.Locator(
			p.page.GetByTestId("postcode-lookup-loading"),
		).ToBeHidden(); err != nil {
			return err
		}
	}
	fields := []struct {
		testID string
		value  string
	}{
		{"street", customer.Street},
		{"city", customer.City},
		{"state", customer.State},
	}

	for _, field := range fields {
		if err := p.page.GetByTestId(field.testID).
			Fill(field.value); err != nil {
			return err
		}
	}

	return p.page.GetByTestId("proceed-3").Click()
}

func (p *CheckoutPage) PayCashOnDelivery() error {
	values := []string{"cash-on-delivery"}

	_, err := p.page.GetByTestId("payment-method").SelectOption(
		playwright.SelectOptionValues{Values: &values},
	)
	if err != nil {
		return err
	}

	if err := p.page.GetByTestId("finish").Click(); err != nil {
		return err
	}

	message := p.page.GetByTestId("payment-success-message")
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(message).ToBeVisible(); err != nil {
		return err
	}

	return assert.Locator(message).
		ToHaveText("Payment was successful")
}

func (p *CheckoutPage) ConfirmOrder() error {
	return p.page.GetByTestId("finish").Click()
}
func (p *CheckoutPage) ExpectOrderConfirmed() error {
	confirmation := p.page.Locator("#order-confirmation")
	assert := playwright.NewPlaywrightAssertions()

	if err := assert.Locator(confirmation).ToBeVisible(); err != nil {
		return err
	}

	return assert.Locator(confirmation).ToContainText(
		regexp.MustCompile(`Your invoice number is\s+INV-\d+\.`),
	)
}
