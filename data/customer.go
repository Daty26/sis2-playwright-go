package data

import (
	"crypto/rand"
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

func DemoCustomer() Customer {
	return Customer{
		Email:       "temirlanaltaev26092004@gmail.com",
		Password:    "SuperPuperHardPass@1254",
		DisplayName: firstName + " " + lastName,
	}
}

func NewRegistrationCustomer() Customer {

	return Customer{
		Email:        "temirlan" + strings.ToLower(rand.Text()) + "@gmail.com",
		Password:     "SuperPuperHardPass@1254",
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
