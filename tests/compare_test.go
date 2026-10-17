package tests

import (
	"testing"

	"sis2/fixtures"
)

func TestCompareTwoProducts(t *testing.T) {
	t.Parallel()

	catalogPage, productPage := fixtures.NewComparisonPages(t)

	if err := catalogPage.Open(); err != nil {
		t.Fatalf("open catalogue for product A: %v", err)
	}

	if err := catalogPage.OpenProduct("Combination Pliers"); err != nil {
		t.Fatalf("open Combination Pliers: %v", err)
	}

	if err := productPage.ExpectName("Combination Pliers"); err != nil {
		t.Fatalf("verify product a name: %v", err)
	}

	nameA, err := productPage.Name()
	if err != nil {
		t.Fatalf("read product a name: %v", err)
	}

	priceA, err := productPage.Price()
	if err != nil {
		t.Fatalf("read product a price: %v", err)
	}

	if err := catalogPage.Open(); err != nil {
		t.Fatalf("open catalogue for product b: %v", err)
	}

	if err := catalogPage.OpenProduct("Pliers"); err != nil {
		t.Fatalf("open Pliers: %v", err)
	}

	if err := productPage.ExpectName("Pliers"); err != nil {
		t.Fatalf("verify product b name: %v", err)
	}
	nameB, err := productPage.Name()
	if err != nil {
		t.Fatalf("read product b name: %v", err)
	}

	priceB, err := productPage.Price()
	if err != nil {
		t.Fatalf("read product b price: %v", err)
	}

	t.Logf("%s: $%.2f; %s: $%.2f", nameA, priceA, nameB, priceB)

	if priceA <= priceB {
		t.Fatalf(
			"expected %s ($%.2f) to cost more than %s ($%.2f)",
			nameA, priceA, nameB, priceB,
		)
	}
}
