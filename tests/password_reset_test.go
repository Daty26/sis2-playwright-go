package tests

import (
	"testing"

	"sis2/data"
	"sis2/fixtures"
)

func TestResetPasswordWithKnownEmail(t *testing.T) {
	t.Parallel()

	registerPage, resetPage := fixtures.NewPasswordResetPages(t)
	customer := data.NewRegistrationCustomer()

	if err := registerPage.Open(); err != nil {
		t.Fatalf("open registration page: %v", err)
	}

	if err := registerPage.Registration(customer); err != nil {
		t.Fatalf("register customer: %v", err)
	}

	if err := registerPage.ExpectRedirectToLogin(); err != nil {
		t.Fatalf("verify registration redirect: %v", err)
	}
	if err := resetPage.Open(); err != nil {
		t.Fatalf("open password reset page: %v", err)
	}
	if err := resetPage.RequestReset(customer.Email); err != nil {
		t.Fatalf("request reset for registered email: %v", err)
	}

	if err := resetPage.ExpectConfirmation(); err != nil {
		t.Fatalf("verify reset confirmation: %v", err)
	}
}

func TestResetPasswordWithUnknownEmail(t *testing.T) {
	t.Parallel()

	_, resetPage := fixtures.NewPasswordResetPages(t)
	customer := data.NewRegistrationCustomer()

	if err := resetPage.Open(); err != nil {
		t.Fatalf("open password reset page: %v", err)
	}
	if err := resetPage.RequestReset(customer.Email); err != nil {
		t.Fatalf("request reset for unregistered email: %v", err)
	}
	if err := resetPage.ExpectInvalidEmail(); err != nil {
		t.Fatalf("verify unregistered email error: %v", err)
	}
}
