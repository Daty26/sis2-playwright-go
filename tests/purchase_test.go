package tests

import (
	"testing"

	"sis2/data"
	"sis2/fixtures"
)

func TestBuyProduct(t *testing.T) {
	t.Parallel()

	p := fixtures.NewPurchasePages(t)
	customer := data.NewRegistrationCustomer()
	if err := p.Register.Open(); err != nil {
		t.Fatalf("open registration: %v", err)
	}

	if err := p.Register.Registration(customer); err != nil {
		t.Fatalf("register customer: %v", err)
	}
	if err := p.Register.ExpectRedirectToLogin(); err != nil {
		t.Fatalf("verify registration redirect: %v", err)
	}
	if err := p.Login.SignIn(customer.Email, customer.Password); err != nil {
		t.Fatalf("sign in: %v", err)
	}
	if err := p.Login.ExpectSignedIn(customer.DisplayName); err != nil {
		t.Fatalf("verify signed-in customer: %v", err)
	}
	if err := p.Catalog.Open(); err != nil {
		t.Fatalf("open catalogue: %v", err)
	}

	const productName = "Combination Pliers"
	const quantity = 2

	if err := p.Catalog.OpenProduct(productName); err != nil {
		t.Fatalf("open product: %v", err)
	}

	if err := p.Product.ExpectName(productName); err != nil {
		t.Fatalf("verify product name: %v", err)
	}

	unitPrice, err := p.Product.Price()
	if err != nil {
		t.Fatalf("read unit price: %v", err)
	}

	if err := p.Product.AddToCart(quantity); err != nil {
		t.Fatalf("add product to cart: %v", err)
	}

	if err := p.Checkout.Open(); err != nil {
		t.Fatalf("open checkout: %v", err)
	}
	if err := p.Checkout.ExpectCart(productName, quantity, unitPrice); err != nil {
		t.Fatalf("verify cart contents and total: %v", err)
	}

	if err := p.Checkout.ProceedToBilling(); err != nil {
		t.Fatalf("proceed to billing: %v", err)
	}
	if err := p.Checkout.FillBilling(customer); err != nil {
		t.Fatalf("complete billing address: %v", err)
	}

	if err := p.Checkout.PayCashOnDelivery(); err != nil {
		t.Fatalf("validate cash-on-delivery payment: %v", err)
	}
	if err := p.Checkout.ConfirmOrder(); err != nil {
		t.Fatalf("confirm order: %v", err)
	}

	if err := p.Checkout.ExpectOrderConfirmed(); err != nil {
		t.Fatalf("verify invoice confirmation: %v", err)
	}
}
