package tests

import (
	"testing"

	"sis2/data"
	"sis2/fixtures"
)

func TestRegisterNewCustomer(t *testing.T) {
	t.Parallel()

	registerPage, loginPage := fixtures.NewRegistrationPage(t)
	customer := data.NewRegistrationCustomer()
	if err := registerPage.Open(); err != nil {
		t.Fatalf("open registration page: %v", err)
	}

	if err := registerPage.Registration(customer); err != nil {
		t.Fatalf("register customer: %v", err)
	}
	if err := registerPage.ExpectRedirectToLogin(); err != nil {
		t.Fatalf("verify redirect to login: %v", err)
	}
	if err := loginPage.SignIn(customer.Email, customer.Password); err != nil {
		t.Fatalf("sign in with registered customer: %v", err)
	}
	if err := loginPage.ExpectSignedIn(customer.DisplayName); err != nil {
		t.Fatalf("verify registered customer is signed in: %v", err)
	}
}