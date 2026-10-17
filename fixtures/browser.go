package fixtures

import (
	"sis2/pages"
	"testing"

	"github.com/mxschmitt/playwright-go"
)

type PurchasePages struct {
	Register *pages.RegistrationPage
	Login    *pages.LoginPage
	Catalog  *pages.CatalogPage
	Product  *pages.ProductPage
	Checkout *pages.CheckoutPage
}

func NewPage(t *testing.T) playwright.Page {
	t.Helper()

	pw, err := playwright.Run()
	if err != nil {
		t.Fatalf("could not start the playwright: %v", err)
	}
	pw.Selectors.SetTestIdAttribute("data-test")
	t.Cleanup(func() {
		if err := pw.Stop(); err != nil {
			t.Errorf("close pw Run: %v", err)
		}
	})

	browser, err := pw.Chromium.Launch()
	if err != nil {
		t.Fatalf("couldn't launch browser: %v", err)
	}
	t.Cleanup(func() {
		if err := browser.Close(); err != nil {
			t.Errorf("close browser: %v", err)
		}
	})
	browserCtx, err := browser.NewContext()
	if err != nil {
		t.Fatalf("create browser context: %v", err)
	}
	t.Cleanup(func() {
		if err := browserCtx.Close(); err != nil {
			t.Errorf("couldn't close browser ctx: %v", err)
		}
	})
	page, err := browserCtx.NewPage()
	if err != nil {
		t.Fatalf("couldn't create a page: %v", err)
	}
	return page
}

func NewHomePage(t *testing.T) *pages.HomePage {
	t.Helper()
	page := NewPage(t)
	return pages.NewHomePage(page)
}
func NewLoginPage(t *testing.T) *pages.LoginPage {
	t.Helper()
	page := NewPage(t)
	return pages.NewLoginPage(page)
}
func NewRegistrationPage(t *testing.T) (*pages.RegistrationPage, *pages.LoginPage) {
	t.Helper()
	page := NewPage(t)
	regPage := pages.NewRegisterPage(page)
	logInPage := pages.NewLoginPage(page)
	return regPage, logInPage
}
func NewComparisonPages(t *testing.T) (*pages.CatalogPage, *pages.ProductPage) {
	t.Helper()
	page := NewPage(t)
	return pages.NewCatalogPage(page), pages.NewProductPage(page)
}

func NewPasswordResetPages(t *testing.T) (*pages.RegistrationPage, *pages.PasswordResetPage) {
	t.Helper()
	page := NewPage(t)
	return pages.NewRegisterPage(page), pages.NewPasswordResetPage(page)
}
func NewPurchasePages(t *testing.T) *PurchasePages {
	t.Helper()

	page := NewPage(t)

	return &PurchasePages{
		Register: pages.NewRegisterPage(page),
		Login:    pages.NewLoginPage(page),
		Catalog:  pages.NewCatalogPage(page),
		Product:  pages.NewProductPage(page),
		Checkout: pages.NewCheckoutPage(page),
	}
}
