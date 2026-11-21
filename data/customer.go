package data

import (
	"crypto/rand"
	"os"
	"strings"
)

type Customer struct {
	Email        string
	Password     string
	DisplayName  string
	FirstName    string
	LastName     string
	DateOfBirth  string
	CountryLabel string
	PostalCode   string
	HouseNumber  string
	Street       string
	City         string
	State        string
	Phone        string
}

const (
	firstName = "Temirlan"
	lastName  = "Altayev"
)

func NewRegistrationCustomer() Customer {
	password := os.Getenv("TEST_PASSWORD")
	if password == "" {
		// Disposable accounts need no personal credentials or repository secrets.
		password = "T!" + rand.Text() + "9a"
	}
	return Customer{
		Email:        "sis2" + strings.ToLower(rand.Text()) + "@example.test",
		Password:     password,
		DisplayName:  firstName + " " + lastName,
		FirstName:    firstName,
		LastName:     lastName,
		DateOfBirth:  "2004-10-09",
		CountryLabel: "United States of America (the)",
		PostalCode:   "84070",
		HouseNumber:  "10",
		Street:       "Schuster Light",
		City:         "Nathanielton",
		State:        "Maine",
		Phone:        "88016803855",
	}
}
