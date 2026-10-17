package tests

import (
	"sis2/data"
	"sis2/fixtures"
	"testing"
)

func TestLoginWithValidCredentials(t *testing.T) {
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
		t.Fatalf("sign in with valid credentials: %v", err)
	}
	if err := loginPage.ExpectSignedIn(customer.DisplayName); err != nil {
		t.Fatalf("verify successful login: %v", err)
	}
}

func TestLoginWithInvalidPassword(t *testing.T) {
	t.Parallel()

	loginPage := fixtures.NewLoginPage(t)
	customer := data.DemoCustomer()

	if err := loginPage.Open(); err != nil {
		t.Fatalf("open login page: %v", err)
	}

	if err := loginPage.SignIn(customer.Email, "superpupertest@123123"); err != nil {
		t.Fatalf("submit invalid password: %v", err)
	}

	if err := loginPage.ExpectInvalidCredentials(); err != nil {
		t.Fatalf("verify rejected login: %v", err)
	}
}
