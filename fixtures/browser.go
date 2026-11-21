package fixtures

import (
	"os"
	"path/filepath"
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
	if err := browserCtx.Tracing().Start(playwright.TracingStartOptions{
		Screenshots: playwright.Bool(true),
		Snapshots:   playwright.Bool(true),
		Sources:     playwright.Bool(true),
		Title:       playwright.String(t.Name()),
	}); err != nil {
		t.Fatalf("start trace: %v", err)
	}
	root := os.Getenv("TEST_RESULTS_DIR")
	if root == "" {
		root = filepath.Join("..", "test-results", "local")
	}
	dir := filepath.Join(root, filepath.FromSlash(t.Name()))
	t.Cleanup(func() {
		if err := os.MkdirAll(dir, 0755); err != nil {
			t.Errorf("create trace directory: %v", err)
			return
		}
		if err := browserCtx.Tracing().Stop(filepath.Join(dir, "trace.zip")); err != nil {
			t.Errorf("save trace: %v", err)
		}
	})
	page, err := browserCtx.NewPage()
	if err != nil {
		t.Fatalf("couldn't create a page: %v", err)
	}

	t.Cleanup(func() {
		if !t.Failed() {
			return
		}

		t.Logf("Failure URL: %s", page.URL())

		if title, err := page.Title(); err != nil {
			t.Logf("Could not read title: %v", err)
		} else {
			t.Logf("Failure title: %s", title)
		}

		if err := os.MkdirAll(dir, 0755); err != nil {
			t.Logf("Could not create evidence directory: %v", err)
			return
		}

		html, err := page.Content()
		if err != nil {
			t.Logf("Could not capture HTML: %v", err)
		} else if err := os.WriteFile(
			filepath.Join(dir, "page.html"),
			[]byte(html),
			0644,
		); err != nil {
			t.Logf("Could not save HTML: %v", err)
		}

		if _, err := page.Screenshot(playwright.PageScreenshotOptions{
			Path:     playwright.String(filepath.Join(dir, "page.png")),
			FullPage: playwright.Bool(true),
			Timeout:  playwright.Float(5000),
		}); err != nil {
			t.Logf("Could not save screenshot: %v", err)
		}
	})
	if os.Getenv("CI_VERIFY_FAILURE") == t.Name() {
		t.Cleanup(func() { t.Error("intentional CI evidence check") })
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
